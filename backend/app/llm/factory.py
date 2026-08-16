from functools import lru_cache

from app.llm.base import LLMProvider
from app.llm.openrouter import OpenRouterProvider


@lru_cache
def get_llm_provider() -> LLMProvider:
    """Único proveedor soportado hoy: OpenRouter. Cambiar de proveedor en
    el futuro solo requiere implementar LLMProvider y devolverlo aquí."""
    return OpenRouterProvider()
