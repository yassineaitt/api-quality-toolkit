"""Runtime configuration, validated once. No secrets are required for the public sandboxes."""

from __future__ import annotations

import os

from pydantic import BaseModel, Field, HttpUrl


class Settings(BaseModel):
    api_base_url: HttpUrl = Field(default=HttpUrl("https://restful-booker.herokuapp.com"))
    api_username: str = "admin"
    api_password: str = "password123"  # noqa: S105 - published demo credential of a public sandbox
    contract_schema_url: str = "https://petstore3.swagger.io/api/v3/openapi.json"
    contract_base_url: HttpUrl = Field(default=HttpUrl("https://petstore3.swagger.io/api/v3"))
    contract_max_examples: int = Field(default=15, ge=1, le=500)
    timeout_s: float = Field(default=15.0, gt=0)

    @classmethod
    def from_env(cls, environ: dict[str, str] | None = None) -> Settings:
        env = os.environ if environ is None else environ
        raw = {
            "api_base_url": env.get("API_BASE_URL"),
            "api_username": env.get("API_USERNAME"),
            "api_password": env.get("API_PASSWORD"),
            "contract_schema_url": env.get("CONTRACT_SCHEMA_URL"),
            "contract_base_url": env.get("CONTRACT_BASE_URL"),
            "contract_max_examples": env.get("CONTRACT_MAX_EXAMPLES"),
            "timeout_s": env.get("API_TIMEOUT_S"),
        }
        return cls.model_validate({k: v for k, v in raw.items() if v})


settings = Settings.from_env()
