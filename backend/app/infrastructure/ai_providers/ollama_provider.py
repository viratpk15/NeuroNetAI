"""Ollama provider implementation for local LLM integration using official client."""
from __future__ import annotations

import json
import logging
from typing import Any

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
    DEFAULT_TIMEOUT = 60.0

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
        """
        prompt = self.prompt_builder.build_conversation_prompt(events, project_name)
        
        try:
            response = await self._generate(prompt)
            return self._parse_json_response(response)
        except Exception as e:
            logger.error(f"Ollama conversation summary failed: {e}")
            return {
                "conversation_summary": "",
                "discussion_topics": [],
                "important_decisions": [],
            }

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
        """
        prompt = self.prompt_builder.build_task_prompt(events, project_name)
        
        try:
            response = await self._generate(prompt)
            return self._parse_json_response(response)
        except Exception as e:
            logger.error(f"Ollama task extraction failed: {e}")
            return {"tasks": []}

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
        """
        prompt = self.prompt_builder.build_entity_prompt(events, project_name)
        
        try:
            response = await self._generate(prompt)
            return self._parse_json_response(response)
        except Exception as e:
            logger.error(f"Ollama entity extraction failed: {e}")
            return {"entities": []}

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
        """
        prompt = self.prompt_builder.build_sentiment_prompt(events, project_name)
        
        try:
            response = await self._generate(prompt)
            return self._parse_json_response(response)
        except Exception as e:
            logger.error(f"Ollama sentiment analysis failed: {e}")
            return {
                "overall_sentiment": "neutral",
                "positivity_score": 0.0,
                "stress_score": 0.0,
                "confidence_score": 0.0,
            }

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
            return response.get("response", "") or ""
        except ollama.ResponseError as e:
            logger.error(f"Ollama API response error: {e}")
            raise
        except Exception as e:
            logger.error(f"Ollama API call failed: {e}")
            raise

    def _parse_json_response(self, response: str) -> dict[str, Any]:
        """Parse JSON response from Ollama.
        
        Args:
            response: Text response from API
            
        Returns:
            Parsed JSON dictionary
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
        
        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON response: {e}")
            return {}

    async def close(self) -> None:
        """Close the client connection."""
        # ollama client doesn't require explicit cleanup
        pass

    async def __aenter__(self) -> "OllamaProvider":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()