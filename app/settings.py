from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Client -> ModelGate auth
    gateway_token: str = Field(default="change-me", alias="MODELGATE_TOKEN")

    # Upstreams
    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    openai_base_url: str = Field(default="https://api.openai.com/v1", alias="OPENAI_BASE_URL")

    ollama_base_url: str = Field(default="http://127.0.0.1:11434/v1", alias="OLLAMA_BASE_URL")

    default_provider: str = Field(default="openai", alias="DEFAULT_PROVIDER")  # openai|ollama
    timeout_seconds: float = Field(default=60.0, alias="TIMEOUT_SECONDS")

settings = Settings()
