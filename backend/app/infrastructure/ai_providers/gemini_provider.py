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

    DEFAULT_MODEL = "gemini-2.5-flash"
    DEFAULT_TIMEOUT = 120.0  # 120 second timeout
    DEFAULT_TEMPERATURE = 0.2
    MAX_RETRIES = 1  # Retry once on transient failures

    def __init__(
        self,
        api_key: str,
        model: str = DEFAULT_MODEL,
        prompt_builder: PromptBuilder | None = None,
    ):
        self.api_key = api_key
        self.model = model
        self.prompt_builder = prompt_builder or PromptBuilder()
        self.timeout = self.DEFAULT_TIMEOUT
        self.temperature = self.DEFAULT_TEMPERATURE
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
            
        Raises:
            Exception: If LLM call fails (agents will handle fallback)
        """
        prompt = self.prompt_builder.build_conversation_prompt(events, project_name)
        logger.info(f"GeminiProvider.summarize_conversation - PROMPT (first 500 chars): {prompt[:500]}")
        
        response = await self._generate_content(prompt)
        logger.info(f"GeminiProvider.summarize_conversation - RAW RESPONSE: '{response[:200] if response else ''}...'")
        result = self._parse_json_response(response)
        logger.info(f"GeminiProvider.summarize_conversation - PARSED RESULT: {result}")
        return result

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
            
        Raises:
            Exception: If LLM call fails (agents will handle fallback)
        """
        prompt = self.prompt_builder.build_task_prompt(events, project_name)
        logger.info(f"GeminiProvider.extract_tasks - PROMPT (first 500 chars): {prompt[:500]}")
        
        response = await self._generate_content(prompt)
        logger.info(f"GeminiProvider.extract_tasks - RAW RESPONSE: '{response[:200] if response else ''}...'")
        result = self._parse_json_response(response)
        logger.info(f"GeminiProvider.extract_tasks - PARSED RESULT: {result}")
        return result

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
            
        Raises:
            Exception: If LLM call fails (agents will handle fallback)
        """
        prompt = self.prompt_builder.build_entity_prompt(events, project_name)
        logger.info(f"GeminiProvider.extract_entities - PROMPT (first 500 chars): {prompt[:500]}")
        
        response = await self._generate_content(prompt)
        logger.info(f"GeminiProvider.extract_entities - RAW RESPONSE: '{response[:200] if response else ''}...'")
        result = self._parse_json_response(response)
        logger.info(f"GeminiProvider.extract_entities - PARSED RESULT: {result}")
        return result

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
            
        Raises:
            Exception: If LLM call fails (agents will handle fallback)
        """
        prompt = self.prompt_builder.build_sentiment_prompt(events, project_name)
        logger.info(f"GeminiProvider.analyze_sentiment - PROMPT (first 500 chars): {prompt[:500]}")
        
        response = await self._generate_content(prompt)
        logger.info(f"GeminiProvider.analyze_sentiment - RAW RESPONSE: '{response[:200] if response else ''}...'")
        result = self._parse_json_response(response)
        logger.info(f"GeminiProvider.analyze_sentiment - PARSED RESULT: {result}")
        return result

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
        """Generate content using Gemini API with retry logic.
        
        Args:
            prompt_or_contents: Prompt string or formatted chat contents
            use_chat_format: Whether contents are in chat format
            
        Returns:
            Generated text response
        """
        last_exception = None
        
        for attempt in range(self.MAX_RETRIES + 1):
            try:
                if use_chat_format:
                    # For chat format, contents are already in Gemini's expected format
                    contents = prompt_or_contents
                else:
                    contents = prompt_or_contents

                # Use async generate_content with JSON response format
                response = self._client.models.generate_content(
                    model=self.model,
                    contents=contents,
                    config={
                        "temperature": self.temperature,
                    },
                )
                
                logger.info(f"GeminiProvider._generate_content - API RESPONSE TEXT: '{response.text[:200] if response.text else ''}...'")
                return response.text or ""
                
            except Exception as e:
                last_exception = e
                logger.warning(f"Gemini API call attempt {attempt + 1} failed: {e}")
                if attempt < self.MAX_RETRIES:
                    logger.info("Retrying...")
                    
        logger.error(f"Gemini API call failed after {self.MAX_RETRIES + 1} attempts: {last_exception}")
        raise last_exception

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
            Parsed JSON dictionary or empty dict if invalid
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
            logger.warning("Empty response from Gemini")
            return {}
        
        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON response from Gemini: {e}")
            logger.warning(f"Raw response was: '{response[:200]}...'")
            return {}