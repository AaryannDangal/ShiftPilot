"""Application configuration loaded from environment variables."""
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Environment-driven configuration for the application."""

    model_config = SettingsConfigDict(env_file=".env", env_prefix="SHIFTPILLOT_", extra="ignore")

    # Application
    app_name: str = Field(default="ShiftPilot")
    debug: bool = Field(default=False)

    # Database
    database_url: str = Field(default="sqlite:///./shiftpilot.db")

    # Security
    secret_key: str = Field(default="change-me-in-production")
    access_token_expires_minutes: int = Field(default=60 * 24)

    # CORS
    backend_cors_origins: str = Field(default="http://localhost:3000")


settings = Settings()
