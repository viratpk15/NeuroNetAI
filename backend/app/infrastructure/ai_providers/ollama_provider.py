"""Ollama provider implementation for local LLM integration using official client."""
from __future__ import annotations

import json
import logging
from typing import Any

import httpx
import ollama

from app.domain.entities import CommunicationEvent
from app.infrastructure.ai_providers.base import AIProvider
from app.prompts.prompt_builder import PromptBuilder

logger = logging.getLogger(__name__)


class OllamaProvider(AIProvider):
    """Ollama AI provider for local LLM integration.
    
    Communicates with Ollama server using the official ollama Python client.
    """

    DEFAULT_HOST = "http://localhost:11434"
    DEFAULT_MODEL = "llama3.2:latest"
    DEFAULT_TIMEOUT = 120.0  # Increased for model cold-start

    def __init__(
        self,
        host: str = DEFAULT_HOST,
        model: str = DEFAULT_MODEL,
        prompt_builder: PromptBuilder | None = None,
        timeout: float = DEFAULT_TIMEOUT,
    ):
        self.host = host.rstrip("/")
        self.model = model
        self.prompt_builder = prompt_builder or PromptBuilder()
        self.timeout = timeout
        # Initialize ollama client with custom host
        self._client = ollama.AsyncClient(host=self.host, timeout=timeout)

    async def summarize_conversation(
        self,
        events: list[CommunicationEvent],
        project_name: str | None = None,
    ) -> dict[str, Any]:
        """Generate conversation summary using Ollama.
        
        Args:
            events: Communication events to analyze
            project_name: Optional project name for context
            
        Returns:
            Dictionary with summary, topics, decisions
            
        Raises:
            Exception: If LLM call fails or returns invalid response
        """
        prompt = self.prompt_builder.build_conversation_prompt(events, project_name)
        
        # TEMPORARY DEBUG LOGGING - TRACE PROMPT
        logger.info(f"OllamaProvider.summarize_conversation - PROMPT (first 500 chars): {prompt[:500]}")
        
        response = await self._generate(prompt)
        
        # TEMPORARY DEBUG LOGGING - TRACE RAW RESPONSE
        logger.info(f"OllamaProvider.summarize_conversation - RAW RESPONSE: '{response}'")
        logger.info(f"OllamaProvider.summarize_conversation - RAW RESPONSE LENGTH: {len(response)}")
        
        result = self._parse_json_response(response)
        logger.info(f"OllamaProvider.summarize_conversation - PARSED RESULT: {result}")
        
        if result is None:
            raise ValueError("LLM returned empty or invalid JSON response")
        return result

    async def extract_tasks(
        self,
        events: list[CommunicationEvent],
        project_name: str | None = None,
    ) -> dict[str, Any]:
        """Extract tasks using Ollama.
        
        Args:
            events: Communication events to analyze
            project_name: Optional project name for context
            
        Returns:
            Dictionary with tasks list
            
        Raises:
            Exception: If LLM call fails or returns invalid response
        """
        prompt = self.prompt_builder.build_task_prompt(events, project_name)
        
        # TEMPORARY DEBUG LOGGING
        logger.info(f"OllamaProvider.extract_tasks - PROMPT (first 500 chars): {prompt[:500]}")
        
        response = await self._generate(prompt)
        
        # TEMPORARY DEBUG LOGGING
        logger.info(f"OllamaProvider.extract_tasks - RAW RESPONSE: '{response[:200]}...'")
        
        result = self._parse_json_response(response)
        
        logger.info(f"OllamaProvider.extract_tasks - PARSED RESULT: {result}")
        
        if result is None:
            raise ValueError("LLM returned empty or invalid JSON response")
        return result

    async def extract_entities(
        self,
        events: list[CommunicationEvent],
        project_name: str | None = None,
    ) -> dict[str, Any]:
        """Extract entities using Ollama.
        
        Args:
            events: Communication events to analyze
            project_name: Optional project name for context
            
        Returns:
            Dictionary with entities list
            
        Raises:
            Exception: If LLM call fails or returns invalid response
        """
        prompt = self.prompt_builder.build_entity_prompt(events, project_name)
        
        # TEMPORARY DEBUG LOGGING
        logger.info(f"OllamaProvider.extract_entities - PROMPT (first 500 chars): {prompt[:500]}")
        
        response = await self._generate(prompt)
        
        # TEMPORARY DEBUG LOGGING
        logger.info(f"OllamaProvider.extract_entities - RAW RESPONSE: '{response[:200]}...'")
        
        result = self._parse_json_response(response)
        
        logger.info(f"OllamaProvider.extract_entities - PARSED RESULT: {result}")
        
        if result is None:
            raise ValueError("LLM returned empty or invalid JSON response")
        return result

    async def analyze_sentiment(
        self,
        events: list[CommunicationEvent],
        project_name: str | None = None,
    ) -> dict[str, Any]:
        """Analyze sentiment using Ollama.
        
        Args:
            events: Communication events to analyze
            project_name: Optional project name for context
            
        Returns:
            Dictionary with sentiment analysis results
            
        Raises:
            Exception: If LLM call fails or returns invalid response
        """
        prompt = self.prompt_builder.build_sentiment_prompt(events, project_name)
        
        # TEMPORARY DEBUG LOGGING
        logger.info(f"OllamaProvider.analyze_sentiment - PROMPT (first 500 chars): {prompt[:500]}")
        
        response = await self._generate(prompt)
        
        # TEMPORARY DEBUG LOGGING
        logger.info(f"OllamaProvider.analyze_sentiment - RAW RESPONSE: '{response[:200]}...'")
        
        result = self._parse_json_response(response)
        
        logger.info(f"OllamaProvider.analyze_sentiment - PARSED RESULT: {result}")
        
        if result is None:
            raise ValueError("LLM returned empty or invalid JSON response")
        return result

    async def chat(
        self,
        messages: list[dict[str, str]],
        system_prompt: str | None = None,
    ) -> dict[str, Any]:
        """Chat completion using Ollama.
        
        Args:
            messages: List of message dicts with role and content
            system_prompt: Optional system prompt
            
        Returns:
            Dictionary with response
        """
        # Build prompt from messages
        prompt_parts = []
        
        if system_prompt:
            prompt_parts.append(f"System: {system_prompt}")
        else:
            # Use default chat template
            chat_template = self.prompt_builder._load_template("chat.md")
            prompt_parts.append(f"System: {chat_template}")
        
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            prompt_parts.append(f"{role.capitalize()}: {content}")
        
        prompt = "\n".join(prompt_parts)
        
        try:
            response = await self._generate(prompt)
            return {"response": response}
        except Exception as e:
            logger.error(f"Ollama chat failed: {e}")
            return {"response": "Error: Unable to generate response"}

    async def _generate(self, prompt: str) -> str:
        """Generate content using Ollama API.
        
        Args:
            prompt: The prompt string to send
            
        Returns:
            Generated text response
        """
        try:
            response = await self._client.generate(
                model=self.model,
                prompt=prompt,
            )
            raw_response = response.get("response", "") or ""
            # TEMPORARY DEBUG LOGGING - TRACE FULL API RESPONSE
            logger.info(f"OllamaProvider._generate - FULL API RESPONSE OBJECT: {response}")
            return raw_response
        except ollama.ResponseError as e:
            logger.error(f"Ollama API response error: {e}")
            raise
        except httpx.ReadTimeout as e:
            logger.warning(f"Ollama request timed out: {e}")
            raise TimeoutError(f"Ollama request timed out after {self.timeout}s") from e
        except httpx.ConnectError as e:
            logger.warning(f"Could not connect to Ollama at {self.host}: {e}")
            raise ConnectionError(f"Could not connect to Ollama at {self.host}") from e
        except Exception as e:
            logger.error(f"Ollama API call failed: {e}")
            raise

    def _parse_json_response(self, response: str) -> dict[str, Any] | None:
        """Parse JSON response from Ollama.

        Args:
            response: Text response from API

        Returns:
            Parsed JSON dictionary or None if invalid/empty
        """
        response = response.strip()

        # Remove markdown code block wrappers if present
        if response.startswith("```json"):
            response = response[7:]
        if response.startswith("```"):
            response = response[3:]
        if response.endswith("```"):
            response = response[:-3]

        response = response.strip()

        if not response:
            logger.warning("Empty response from LLM")
            return None

        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON response: {e}")
            return None

    async def close(self) -> None:
        """Close the client connection."""
        # ollama client doesn't require explicit cleanup
        pass

    async def __aenter__(self) -> "OllamaProvider":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()