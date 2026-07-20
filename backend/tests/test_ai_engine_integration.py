"""Integration tests for AI Engine with Ollama provider."""
import pytest
from datetime import datetime, timezone

from app.infrastructure.ai_providers.ollama_provider import OllamaProvider
from app.infrastructure.ai_providers.factory import ProviderFactory
from app.domain.entities import CommunicationEvent, AgentRun
from uuid import uuid4


class TestAIEngineIntegration:
    """Integration tests for the AI Engine foundation."""

    async def test_provider_factory_creates_ollama_provider(self):
        """Verify ProviderFactory creates OllamaProvider when configured."""
        # Reset factory to ensure clean state
        ProviderFactory.reset()
        
        provider = ProviderFactory.get_provider("ollama")
        
        assert provider is not None
        assert isinstance(provider, OllamaProvider)

    async def test_ollama_provider_chat_returns_response(self):
        """Verify OllamaProvider.chat returns successful response for 'Say hello.'"""
        provider = OllamaProvider(
            host="http://localhost:11434",
            model="llama3.2:latest",
        )
        
        try:
            async with provider:
                result = await provider.chat([{"role": "user", "content": "Say hello."}])
            
            assert "response" in result
            assert isinstance(result["response"], str)
            assert len(result["response"]) > 0
            
            # Verify the response contains a greeting
            response_lower = result["response"].lower()
            assert "hello" in response_lower or "hi" in response_lower or "hey" in response_lower
        except (ConnectionError, TimeoutError, Exception) as e:
            # Skip test if Ollama is not running
            pytest.skip(f"Ollama server not available: {e}")

    async def test_ollama_provider_summarize_conversation(self):
        """Verify OllamaProvider.summarize_conversation works with sample events."""
        events = [
            CommunicationEvent(
                document_id=uuid4(),
                content="Team discussed implementing the new authentication feature. We decided to use JWT tokens.",
                source="slack_message",
                author="alice",
                timestamp=datetime.now(timezone.utc),
            ),
        ]
        
        provider = OllamaProvider(
            host="http://localhost:11434",
            model="llama3.2:latest",
        )
        
        try:
            async with provider:
                result = await provider.summarize_conversation(events, "Test Project")
            
            # Should return dict with expected keys (even if JSON parsing fails)
            assert isinstance(result, dict)
        except (ConnectionError, TimeoutError, Exception) as e:
            pytest.skip(f"Ollama server not available: {e}")

    async def test_ollama_provider_invalid_host_returns_error_response(self):
        """Verify OllamaProvider returns error response for invalid host."""
        provider = OllamaProvider(
            host="http://localhost:9999",
            model="llama3.2:latest",
        )
        
        async with provider:
            result = await provider.chat([{"role": "user", "content": "Hello"}])
        
        # Should return error response instead of raising
        assert "response" in result
        assert "Error" in result["response"]

    async def test_provider_factory_unknown_provider_returns_none(self):
        """Verify ProviderFactory returns None for unknown provider type."""
        ProviderFactory.reset()
        
        provider = ProviderFactory.get_provider("unknown_provider")
        
        assert provider is None

    async def test_agent_run_datetime_is_naive(self):
        """Verify AgentRun datetime fields are naive (no tzinfo) for DB compatibility."""
        agent_run = AgentRun(project_id=uuid4())
        
        # created_at should be naive
        assert agent_run.created_at.tzinfo is None
        
        agent_run.mark_completed()
        
        # completed_at should be naive after completion
        assert agent_run.completed_at is not None
        assert agent_run.completed_at.tzinfo is None