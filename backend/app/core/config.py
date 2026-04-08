from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "BriefBiz API"
    app_env: str = Field(default="development", alias="APP_ENV")
    database_url: str = Field(alias="DATABASE_URL")
    redis_url: str = Field(alias="REDIS_URL")
    elasticsearch_url: str = Field(alias="ELASTICSEARCH_URL")
    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    openrouter_api_key: str | None = Field(default=None, alias="OPENROUTER_API_KEY")
    llm_base_url: str | None = Field(default=None, alias="LLM_BASE_URL")
    llm_model: str = Field(default="openrouter/free", alias="LLM_MODEL")
    embedding_model: str | None = Field(default=None, alias="EMBEDDING_MODEL")
    news_api_key: str | None = Field(default=None, alias="NEWS_API_KEY")
    google_tts_key: str | None = Field(default=None, alias="GOOGLE_TTS_KEY")
    jwt_secret: str = Field(alias="JWT_SECRET")
    sendgrid_api_key: str | None = Field(default=None, alias="SENDGRID_API_KEY")
    sendgrid_from_email: str | None = Field(default=None, alias="SENDGRID_FROM_EMAIL")
    resend_api_key: str | None = Field(default=None, alias="RESEND_API_KEY")
    resend_from_email: str | None = Field(default=None, alias="RESEND_FROM_EMAIL")
    app_base_url: str = Field(default="http://localhost:8000", alias="APP_BASE_URL")
    cors_allowed_origins: str = Field(
        default="http://localhost:5173,http://127.0.0.1:5173,http://localhost",
        alias="CORS_ALLOWED_ORIGINS",
    )
    access_token_expire_minutes: int = Field(default=60 * 24 * 7, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    jwt_issuer: str = Field(default="briefbiz-api", alias="JWT_ISSUER")
    jwt_audience: str = Field(default="briefbiz-clients", alias="JWT_AUDIENCE")
    auth_rate_limit_window_seconds: int = Field(default=60, alias="AUTH_RATE_LIMIT_WINDOW_SECONDS")
    auth_rate_limit_max_requests: int = Field(default=10, alias="AUTH_RATE_LIMIT_MAX_REQUESTS")
    celery_broker_url: str | None = Field(default=None, alias="CELERY_BROKER_URL")
    celery_result_backend: str | None = Field(default=None, alias="CELERY_RESULT_BACKEND")

    @property
    def effective_celery_broker_url(self) -> str:
        return self.celery_broker_url or self.redis_url

    @property
    def effective_celery_result_backend(self) -> str:
        return self.celery_result_backend or self.redis_url

    @property
    def effective_llm_api_key(self) -> str | None:
        return self.openrouter_api_key or self.openai_api_key

    @property
    def effective_llm_base_url(self) -> str | None:
        if self.llm_base_url:
            return self.llm_base_url
        if self.openrouter_api_key:
            return "https://openrouter.ai/api/v1"
        return None

    @property
    def effective_embedding_model(self) -> str | None:
        if self.embedding_model:
            return self.embedding_model
        if self.openai_api_key and not self.openrouter_api_key:
            return "text-embedding-3-small"
        return None

    @property
    def effective_cors_allowed_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_allowed_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
