"""Google Gemini provider implementation using google-genai SDK."""
from __future__ import annotations

import json
import logging
from typing import Any

from google import genai

from app.domain.entities import CommunicationEvent
from app.infrastructure.ai_providers.base import AIProvider
from app.prompts.prompt_builder import PromptBuilder

logger = logging.getLogger(__name__)


class GeminiProvider(AIProvider):
    """Google Gemini AI provider using the official google-genai SDK.
    
    This provider implements domain-specific methods for:
    - Conversation summarization
    - Task extraction
    - Entity extraction
    - Sentiment analysis
    - Chat completion
    """

    DEFAULT_MODEL = "gemini-2.0-flash"

    def __init__(
        self,
        api_key: str,
        model: str = DEFAULT_MODEL,
        prompt_builder: PromptBuilder | None = None,
    ):
        self.api_key = api_key
        self.model = model
        self.prompt_builder = prompt_builder or PromptBuilder()
        self._client = genai.Client(api_key=api_key)

    async def summarize_conversation(
        self,
        events: list[CommunicationEvent],
        project_name: str | None = None,
    ) -> dict[str, Any]:
        """Generate conversation summary using Gemini.
        
        Args:
            events: Communication events to analyze
            project_name: Optional project name for context
            
        Returns:
            Dictionary with summary, topics, decisions
        """
        prompt = self.prompt_builder.build_conversation_prompt(events, project_name)
        
        try:
            response = await self._generate_content(prompt)
            return self._parse_json_response(response)
        except Exception as e:
            logger.error(f"Gemini conversation summary failed: {e}")
            # Return fallback values matching rule-based agent structure
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
        """Extract tasks using Gemini.
        
        Args:
            events: Communication events to analyze
            project_name: Optional project name for context
            
        Returns:
            Dictionary with tasks list
        """
        prompt = self.prompt_builder.build_task_prompt(events, project_name)
        
        try:
            response = await self._generate_content(prompt)
            return self._parse_json_response(response)
        except Exception as e:
            logger.error(f"Gemini task extraction failed: {e}")
            return {"tasks": []}

    async def extract_entities(
        self,
        events: list[CommunicationEvent],
        project_name: str | None = None,
    ) -> dict[str, Any]:
        """Extract entities using Gemini.
        
        Args:
            events: Communication events to analyze
            project_name: Optional project name for context
            
        Returns:
            Dictionary with entities list
        """
        prompt = self.prompt_builder.build_entity_prompt(events, project_name)
        
        try:
            response = await self._generate_content(prompt)
            return self._parse_json_response(response)
        except Exception as e:
            logger.error(f"Gemini entity extraction failed: {e}")
            return {"entities": []}

    async def analyze_sentiment(
        self,
        events: list[CommunicationEvent],
        project_name: str | None = None,
    ) -> dict[str, Any]:
        """Analyze sentiment using Gemini.
        
        Args:
            events: Communication events to analyze
            project_name: Optional project name for context
            
        Returns:
            Dictionary with sentiment analysis results
        """
        prompt = self.prompt_builder.build_sentiment_prompt(events, project_name)
        
        try:
            response = await self._generate_content(prompt)
            return self._parse_json_response(response)
        except Exception as e:
            logger.error(f"Gemini sentiment analysis failed: {e}")
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
        """Chat completion using Gemini.
        
        Args:
            messages: List of message dicts with role and content
            system_prompt: Optional system prompt
            
        Returns:
            Dictionary with response
        """
        formatted_messages = self.prompt_builder.build_chat_prompt(messages, system_prompt)
        
        try:
            # Build contents for Gemini
            contents = self._format_chat_contents(formatted_messages)
            response = await self._generate_content(contents, use_chat_format=True)
            return {"response": response}
        except Exception as e:
            logger.error(f"Gemini chat failed: {e}")
            return {"response": "Error: Unable to generate response"}

    async def _generate_content(
        self,
        prompt_or_contents: str | list[dict[str, str]],
        use_chat_format: bool = False,
    ) -> str:
        """Generate content using Gemini API.
        
        Args:
            prompt_or_contents: Prompt string or formatted chat contents
            use_chat_format: Whether contents are in chat format
            
        Returns:
            Generated text response
        """
        try:
            if use_chat_format:
                # For chat format, convert to Gemini's expected format
                contents = []
                for msg in prompt_or_contents:
                    contents.append({
                        "role": msg.get("role", "user"),
                        "parts": [{"text": msg.get("content", "")}],
                    })
            else:
                contents = prompt_or_contents

            response = self._client.models.generate_content(
                model=self.model,
                contents=contents,
            )
            
            return response.text or ""
        except Exception as e:
            logger.error(f"Gemini API call failed: {e}")
            raise

    def _format_chat_contents(
        self,
        messages: list[dict[str, str]],
    ) -> list[dict[str, Any]]:
        """Format messages for Gemini chat API.
        
        Args:
            messages: List of message dicts
            
        Returns:
            Formatted contents for Gemini
        """
        contents = []
        for msg in messages:
            # Gemini uses 'model' for assistant role
            role = "model" if msg.get("role") == "assistant" else msg.get("role", "user")
            if role not in ("user", "model", "system"):
                role = "user"
            
            contents.append({
                "role": role,
                "parts": [{"text": msg.get("content", "")}],
            })
        return contents

    def _parse_json_response(self, response: str) -> dict[str, Any]:
        """Parse JSON response from Gemini.
        
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
            # Return empty dict as fallback
            return {}