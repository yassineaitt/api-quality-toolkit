// k6 performance smoke for the booking API.
// Thresholds are the contract: the build fails when p95 latency or the error rate exceeds them.
// Tune with K6_P95_MS / K6_ERROR_RATE / K6_VUS / K6_DURATION; run with `make perf` or `k6 run perf/k6/smoke.js`.
import http from 'k6/http';
import { check, group, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';
import { textSummary } from 'https://jslib.k6.io/k6-summary/0.1.0/index.js';

const BASE_URL = __ENV.API_BASE_URL || 'https://restful-booker.herokuapp.com';
const P95_MS = Number(__ENV.K6_P95_MS || 1500);
const ERROR_RATE = Number(__ENV.K6_ERROR_RATE || 0.02);

export const options = {
  scenarios: {
    smoke: {
      executor: 'constant-vus',
      vus: Number(__ENV.K6_VUS || 5),
      duration: __ENV.K6_DURATION || '30s',
      gracefulStop: '5s',
    },
  },
  thresholds: {
    // Build-failing SLOs (abortOnFail stops the run early so CI feedback is fast).
    http_req_failed: [{ threshold: `rate<${ERROR_RATE}`, abortOnFail: true, delayAbortEval: '10s' }],
    http_req_duration: [{ threshold: `p(95)<${P95_MS}`, abortOnFail: false }],
    // Per-endpoint budgets, so one slow route cannot hide behind a fast one.
    'http_req_duration{name:ping}': [`p(95)<${P95_MS}`],
    'http_req_duration{name:list}': [`p(95)<${P95_MS}`],
    'http_req_duration{name:get}': [`p(95)<${P95_MS}`],
    checks: ['rate>0.98'],
    contract_errors: ['rate<0.01'],
  },
  summaryTrendStats: ['avg', 'min', 'med', 'p(90)', 'p(95)', 'p(99)', 'max'],
};

const contractErrors = new Rate('contract_errors');
const listSize = new Trend('booking_list_size');
const params = { headers: { Accept: 'application/json' } };

export function setup() {
  const res = http.get(`${BASE_URL}/ping`, { tags: { name: 'ping' } });
  if (res.status !== 201) {
    throw new Error(`target is not healthy: GET /ping -> ${res.status}`);
  }
  // One booking id to read repeatedly without creating load-test data.
  const list = http.get(`${BASE_URL}/booking`, params).json();
  return { bookingId: list.length ? list[0].bookingid : null };
}

export default function (data) {
  group('health', () => {
    const res = http.get(`${BASE_URL}/ping`, { tags: { name: 'ping' } });
    check(res, { 'ping is 201': (r) => r.status === 201 });
  });

  group('read bookings', () => {
    const list = http.get(`${BASE_URL}/booking`, { ...params, tags: { name: 'list' } });
    const ok = check(list, {
      'list is 200': (r) => r.status === 200,
      'list is JSON array': (r) => Array.isArray(r.json()),
      'ids are positive integers': (r) => r.json().every((b) => Number.isInteger(b.bookingid) && b.bookingid > 0),
    });
    contractErrors.add(!ok);
    if (list.status === 200) listSize.add(list.json().length);

    if (data.bookingId) {
      const one = http.get(`${BASE_URL}/booking/${data.bookingId}`, { ...params, tags: { name: 'get' } });
      const shape = check(one, {
        'get is 200 or 404': (r) => r.status === 200 || r.status === 404,
        'booking has required fields': (r) =>
          r.status !== 200 ||
          ['firstname', 'lastname', 'totalprice', 'depositpaid', 'bookingdates'].every((k) => k in r.json()),
      });
      contractErrors.add(!shape);
    }
  });

  sleep(1);
}

export function handleSummary(data) {
  return {
    stdout: textSummary(data, { indent: ' ', enableColors: true }),
    'reports/k6-summary.json': JSON.stringify(data, null, 2),
  };
}
