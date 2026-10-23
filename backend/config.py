
import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Application settings
    app_name: str = "WorkSphere HRMS"
    app_version: str = "2.0.0"
    debug: bool = False

    # Database configuration
    database_url: str = "sqlite:///./worksphere.db"

    # JWT security settings
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Load values from .env file
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


# Create settings object
settings = Settings()
