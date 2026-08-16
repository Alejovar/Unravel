from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuración central de Unravel, cargada desde variables de entorno."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    env: str = "development"

    # --- Database ---
    database_url: str = "postgresql+psycopg://unravel:unravel@localhost:5432/unravel"

    # --- Queue ---
    redis_url: str = "redis://localhost:6379/0"

    # --- LLM (OpenRouter — único proveedor soportado) ---
    openrouter_api_key: str = ""
    openrouter_model: str = "google/gemma-4-26b-a4b-it:free"
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_site_url: str = "http://localhost:3000"
    openrouter_app_name: str = "Unravel"

    # --- Discovery ---
    gdelt_doc_api_url: str = "https://api.gdeltproject.org/api/v2/doc/doc"
    search_max_results: int = 20
    discovery_max_depth: int = 2
    discovery_max_sources: int = 30

    # --- CORS ---
    backend_cors_origins: str = "http://localhost:3000"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.backend_cors_origins.split(",") if o.strip()]

    @property
    def llm_configured(self) -> bool:
        return bool(self.openrouter_api_key)


@lru_cache
def get_settings() -> Settings:
    return Settings()
