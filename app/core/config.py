from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings loaded from environment or .env."""

    app_name: str = "AI LC-MS/MS Method MVP"
    environment: str = "local"
    database_url: str = Field(
        default="postgresql+psycopg://lcms:lcms@localhost:5432/lcms_method_dev",
        validation_alias="DATABASE_URL",
    )
    model_artifact_dir: str = "data/processed/models"
    recommendation_quality_weight: float = 0.45
    recommendation_rt_weight: float = 0.4
    recommendation_runtime_weight: float = 0.15
    recommendation_confidence_weight: float = 0.05

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()
