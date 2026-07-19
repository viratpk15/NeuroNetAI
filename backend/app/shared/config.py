"""
Application configuration.

All configuration is read from environment variables (via a local .env file
in development, or real environment variables in production/hosting
platforms like Render, Fly.io, or Vercel + Supabase). Nothing is hardcoded.
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # App
    app_name: str = "NeuroNet AI"
    environment: str = "development"
    api_v1_prefix: str = "/api/v1"
    cors_origins: str = "http://localhost:3000"

    # Database (Supabase Postgres connection string)
    # Example: postgresql+asyncpg://postgres:[password]@[host].supabase.co:5432/postgres
    database_url: str

    # Vector store
    chroma_db_path: str = "./chroma_data"

    # AI providers
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    model_provider: str = "anthropic"
    embedding_provider: str = "openai"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
