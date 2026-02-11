from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from backend.const import ENV_DEBUG_MODE, UTF8


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding=UTF8, extra="ignore")

    debug_mode: bool = Field(default=False, alias=ENV_DEBUG_MODE)
    ibm_quantum_api_token: str | None = Field(default=None, alias="IBM_QUANTUM_API_TOKEN")
    ibm_quantum_channel: str = Field(default="ibm_quantum", alias="IBM_QUANTUM_CHANNEL")
    ibm_quantum_instance: str | None = Field(default=None, alias="IBM_QUANTUM_INSTANCE")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached settings instance."""

    return Settings()


settings = get_settings()

# backwards-compatible module level constant
DEBUG_MODE = settings.debug_mode
