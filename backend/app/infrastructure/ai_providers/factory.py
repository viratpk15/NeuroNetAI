"""Provider factory for creating AI provider instances."""
from __future__ import annotations

import logging
from typing import Any

from app.infrastructure.ai_providers.base import AIProvider
from app.infrastructure.ai_providers.gemini_provider import GeminiProvider
from app.infrastructure.ai_providers.ollama_provider import OllamaProvider
from app.prompts.prompt_builder import PromptBuilder
from app.shared.config import get_settings

logger = logging.getLogger(__name__)


class ProviderFactory:
    """Factory for creating AI provider instances.
    
    Creates providers based on configuration settings.
    Supports gemini, ollama, openai, and anthropic providers.
    """

    _instance: AIProvider | None = None

    @classmethod
    def get_provider(cls, provider_type: str | None = None) -> AIProvider | None:
        """Get an AI provider instance based on configuration.
        
        Args:
            provider_type: Optional provider type override. 
                          If None, uses MODEL_PROVIDER from config.
        
        Returns:
            AIProvider instance or None if provider not configured
        """
        settings = get_settings()
        provider_type = provider_type or settings.model_provider
        
        # Return cached instance if available
        if cls._instance is not None:
            return cls._instance
        
        if provider_type == "gemini":
            api_key = settings.gemini_api_key
            if not api_key:
                logger.warning("Gemini provider requested but GEMINI_API_KEY not configured")
                return None
            cls._instance = GeminiProvider(api_key=api_key)
            logger.info("Created Gemini provider instance")
            return cls._instance
        
        elif provider_type == "ollama":
            cls._instance = OllamaProvider(
                host=settings.ollama_host,
                model=settings.ollama_model,
            )
            logger.info(f"Created Ollama provider instance (model: {settings.ollama_model})")
            return cls._instance
        
        elif provider_type == "openai":
            # Placeholder for future OpenAI provider
            api_key = settings.openai_api_key
            if not api_key:
                logger.warning("OpenAI provider requested but OPENAI_API_KEY not configured")
                return None
            logger.warning("OpenAI provider not yet implemented")
            return None
        
        elif provider_type == "anthropic":
            # Placeholder for future Anthropic provider
            api_key = settings.anthropic_api_key
            if not api_key:
                logger.warning("Anthropic provider requested but ANTHROPIC_API_KEY not configured")
                return None
            logger.warning("Anthropic provider not yet implemented")
            return None
        
        else:
            logger.warning(f"Unknown provider type: {provider_type}")
            return None

    @classmethod
    def reset(cls) -> None:
        """Reset the cached provider instance.
        
        Useful for testing or configuration changes.
        """
        cls._instance = None


def create_ai_provider(provider_type: str | None = None) -> AIProvider | None:
    """Convenience function to create an AI provider.
    
    Args:
        provider_type: Optional provider type override
        
    Returns:
        AIProvider instance or None
    """
    return ProviderFactory.get_provider(provider_type)