# Pydantic Settings
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Pathlib
from pathlib import Path

# JSON
import json

ROOT_DIR = Path(__file__).resolve().parent.parent  # Root directory


# Class Settings
class Settings(BaseSettings):
    # Application
    app_mode: str

    # Database Application
    postgresql_app_url: str

    # Database Andromeda
    timescaledb_andromeda_url: str

    # Security
    secret: str = ""
    algorithm: str = ""

    # Sentry
    sentry_dsn: str = ""

    # Firebase
    firebase_credentials: str = ""

    # Resend
    resend_apikey: str = ""

    # Email
    email_endpoint: str = ""
    email_port: int = 0
    email_username: str = ""
    email_password: str = ""

    frontend_url: str = ""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Validate: postgresql_app_url
    @field_validator("postgresql_app_url")
    @classmethod
    def validate_postgresql_app_url(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("postgresql_app_url must be set")
        if not value.startswith(
            ("postgresql://", "postgresql+psycopg2://", "postgresql+psycopg://")
        ):
            raise ValueError(
                "postgresql_app_url must be a valid PostgreSQL connection string"
            )
        return value

    # Validate: timescaledb_andromeda_url
    @field_validator("timescaledb_andromeda_url")
    @classmethod
    def validate_timescaledb_andromeda_url(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("timescaledb_andromeda_url must be set")
        if not value.startswith(
            ("postgresql://", "postgresql+psycopg2://", "postgresql+psycopg://")
        ):
            raise ValueError(
                "timescaledb_andromeda_url must be a valid PostgreSQL connection string"
            )
        return value

    # Validator: secret
    @field_validator("secret")
    @classmethod
    def validate_secret(cls, value: str) -> str:
        value = value.strip()
        if len(value) < 32:
            raise ValueError("secret must be at least 32 characters long")
        return value

    # Validator: algorithm
    @field_validator("algorithm")
    @classmethod
    def validate_algorithm(cls, value: str) -> str:
        allowed_algorithms = {"HS256", "HS384", "HS512"}
        value = value.strip()
        if value not in allowed_algorithms:
            raise ValueError(f"algorithm must be one of {sorted(allowed_algorithms)}")
        return value

    def get_firebase_credentials_dict(self) -> dict:
        raw_val = self.firebase_credentials.strip()

        if raw_val.startswith("{"):
            return json.loads(raw_val)

        path = Path(raw_val) if raw_val else ROOT_DIR / "openhubble-cloud-firebase.json"
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)

        raise ValueError(f"Firebase credentials not found or invalid at: {path}")


# settings
settings = Settings()
