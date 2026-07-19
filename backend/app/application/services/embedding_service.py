"""Embedding service for RAG foundation."""
import logging
from abc import ABC, abstractmethod

import ollama
from app.shared.config import get_settings

logger = logging.getLogger(__name__)


class EmbeddingProvider(ABC):
    """Abstract embedding provider interface."""

    @abstractmethod
    def embed(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for texts.

        Args:
            texts: List of text strings to embed

        Returns:
            List of embedding vectors
        """
        ...


class OllamaEmbeddingProvider(EmbeddingProvider):
    """Ollama embedding provider using the official client."""

    def __init__(self, host: str | None = None, model: str | None = None):
        settings = get_settings()
        self.host = host or settings.ollama_host
        self.model = model or settings.ollama_model
        self._client = ollama.AsyncClient(host=self.host)

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings using Ollama.

        Args:
            texts: List of text strings to embed

        Returns:
            List of embedding vectors
        """
        embeddings = []
        for text in texts:
            try:
                response = self._client.embeddings(model=self.model, prompt=text)
                embedding = response.get("embedding", [])
                embeddings.append(embedding)
            except Exception as e:
                logger.error(f"Failed to embed text: {e}")
                embeddings.append([0.0] * 1536)  # Default empty embedding

        return embeddings


class EmbeddingService:
    """Service for generating embeddings."""

    def __init__(self, provider: str | None = None):
        settings = get_settings()
        provider_name = provider or settings.embedding_provider

        if provider_name == "ollama":
            self._provider = OllamaEmbeddingProvider()
        elif provider_name == "openai":
            self._provider = OpenAIEmbeddingProvider()
        elif provider_name == "gemini":
            self._provider = GeminiEmbeddingProvider()
        else:
            raise ValueError(f"Unknown embedding provider: {provider_name}")

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for texts."""
        return self._provider.embed(texts)


class OpenAIEmbeddingProvider(EmbeddingProvider):
    """OpenAI embedding provider placeholder."""

    def __init__(self, api_key: str | None = None, model: str = "text-embedding-3-small"):
        self.model = model
        # Would use openai library when implemented

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings using OpenAI."""
        # Placeholder - would call OpenAI API
        return [[0.0] * 1536 for _ in texts]


class GeminiEmbeddingProvider(EmbeddingProvider):
    """Gemini embedding provider placeholder."""

    def __init__(self, api_key: str | None = None):
        # Would use google-genai when implemented
        pass

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings using Gemini."""
        # Placeholder - would call Gemini API
        return [[0.0] * 1536 for _ in texts]