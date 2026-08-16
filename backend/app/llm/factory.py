from functools import lru_cache

from app.llm.base import LLMProvider
from app.llm.openrouter import OpenRouterProvider


@lru_cache
def get_llm_provider() -> LLMProvider:
    """The only provider supported today: OpenRouter. Switching provider
    later only requires implementing LLMProvider and returning it here."""
    return OpenRouterProvider()
