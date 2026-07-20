"""Groq provider implementation using OpenAI-compatible API."""
from __future__ import annotations

import json
import logging
import re
import time
from typing import Any

from openai import AsyncOpenAI

from app.domain.entities import CommunicationEvent
from app.infrastructure.ai_providers.base import AIProvider
from app.prompts.prompt_builder import PromptBuilder

logger = logging.getLogger(__name__)


class GroqProvider(AIProvider):
    """Groq AI provider using OpenAI-compatible Chat Completions API.
    
    This provider implements domain-specific methods for:
    - Conversation summarization
    - Task extraction
    - Entity extraction
    - Sentiment analysis
    - Chat completion
    """

    DEFAULT_MODEL = "llama-3.3-70b-versatile"
    DEFAULT_TIMEOUT = 120.0  # 120 second timeout
    DEFAULT_TEMPERATURE = 0.2
    MAX_RETRIES = 1  # Retry once on transient failures
    GROQ_BASE_URL = "https://api.groq.com/openai/v1"

    def __init__(
        self,
        api_key: str,
        model: str = DEFAULT_MODEL,
        prompt_builder: PromptBuilder | None = None,
        timeout: float = DEFAULT_TIMEOUT,
    ):
        self.api_key = api_key
        self.model = model
        self.prompt_builder = prompt_builder or PromptBuilder()
        self.timeout = timeout
        self.temperature = self.DEFAULT_TEMPERATURE
        self._client = AsyncOpenAI(
            api_key=api_key,
            base_url=self.GROQ_BASE_URL,
            timeout=timeout,
        )

    async def summarize_conversation(
        self,
        events: list[CommunicationEvent],
        project_name: str | None = None,
    ) -> dict[str, Any]:
        """Generate conversation summary using Groq.
        
        Args:
            events: Communication events to analyze
            project_name: Optional project name for context
            
        Returns:
            Dictionary with summary, topics, decisions
        """
        prompt = self.prompt_builder.build_conversation_prompt(events, project_name)
        logger.info(f"GroqProvider.summarize_conversation - PROMPT (first 500 chars): {prompt[:500]}")
        
        response, usage = await self._chat_completion(prompt)
        logger.info(f"GroqProvider.summarize_conversation - RAW RESPONSE: '{response[:200] if response else ''}...'")
        logger.info(f"GroqProvider.summarize_conversation - USAGE: {usage}")
        result = self._parse_json_response(response)
        logger.info(f"GroqProvider.summarize_conversation - PARSED RESULT: {result}")
        return result

    async def extract_tasks(
        self,
        events: list[CommunicationEvent],
        project_name: str | None = None,
    ) -> dict[str, Any]:
        """Extract tasks using Groq.
        
        Args:
            events: Communication events to analyze
            project_name: Optional project name for context
            
        Returns:
            Dictionary with tasks list
        """
        prompt = self.prompt_builder.build_task_prompt(events, project_name)
        logger.info(f"GroqProvider.extract_tasks - PROMPT (first 500 chars): {prompt[:500]}")
        
        response, usage = await self._chat_completion(prompt)
        logger.info(f"GroqProvider.extract_tasks - RAW RESPONSE: '{response[:200] if response else ''}...'")
        logger.info(f"GroqProvider.extract_tasks - USAGE: {usage}")
        result = self._parse_json_response(response)
        logger.info(f"GroqProvider.extract_tasks - PARSED RESULT: {result}")
        return result

    async def extract_entities(
        self,
        events: list[CommunicationEvent],
        project_name: str | None = None,
    ) -> dict[str, Any]:
        """Extract entities using Groq.
        
        Args:
            events: Communication events to analyze
            project_name: Optional project name for context
            
        Returns:
            Dictionary with entities list
        """
        prompt = self.prompt_builder.build_entity_prompt(events, project_name)
        logger.info(f"GroqProvider.extract_entities - PROMPT (first 500 chars): {prompt[:500]}")
        
        response, usage = await self._chat_completion(prompt)
        logger.info(f"GroqProvider.extract_entities - RAW RESPONSE: '{response[:200] if response else ''}...'")
        logger.info(f"GroqProvider.extract_entities - USAGE: {usage}")
        result = self._parse_json_response(response)
        logger.info(f"GroqProvider.extract_entities - PARSED RESULT: {result}")
        return result

    async def analyze_sentiment(
        self,
        events: list[CommunicationEvent],
        project_name: str | None = None,
    ) -> dict[str, Any]:
        """Analyze sentiment using Groq.
        
        Args:
            events: Communication events to analyze
            project_name: Optional project name for context
            
        Returns:
            Dictionary with sentiment analysis results
        """
        prompt = self.prompt_builder.build_sentiment_prompt(events, project_name)
        logger.info(f"GroqProvider.analyze_sentiment - PROMPT (first 500 chars): {prompt[:500]}")
        
        response, usage = await self._chat_completion(prompt)
        logger.info(f"GroqProvider.analyze_sentiment - RAW RESPONSE: '{response[:200] if response else ''}...'")
        logger.info(f"GroqProvider.analyze_sentiment - USAGE: {usage}")
        result = self._parse_json_response(response)
        logger.info(f"GroqProvider.analyze_sentiment - PARSED RESULT: {result}")
        return result

    async def chat(
        self,
        messages: list[dict[str, str]],
        system_prompt: str | None = None,
    ) -> dict[str, Any]:
        """Chat completion using Groq.
        
        Args:
            messages: List of message dicts with role and content
            system_prompt: Optional system prompt
            
        Returns:
            Dictionary with response
        """
        formatted_messages = self.prompt_builder.build_chat_prompt(messages, system_prompt)
        
        try:
            response, usage = await self._chat_completion_messages(formatted_messages)
            logger.info(f"GroqProvider.chat - USAGE: {usage}")
            return {"response": response}
        except Exception as e:
            logger.error(f"Groq chat failed: {e}")
            return {"response": "Error: Unable to generate response"}

    async def _chat_completion(self, prompt: str) -> tuple[str, dict[str, int]]:
        """Generate completion using Groq chat API with retry logic.
        
        Args:
            prompt: The prompt string to send
            
        Returns:
            Tuple of (generated text, usage dict with token counts)
        """
        messages = [{"role": "user", "content": prompt}]
        return await self._chat_completion_messages(messages)

    async def _chat_completion_messages(
        self, 
        messages: list[dict[str, str]]
    ) -> tuple[str, dict[str, int]]:
        """Generate completion using Groq chat API with retry logic.
        
        Args:
            messages: List of message dicts for chat completion
            
        Returns:
            Tuple of (generated text, usage dict with token counts)
        """
        start_time = time.time()
        last_exception = None
        usage: dict[str, int] = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}

        for attempt in range(self.MAX_RETRIES + 1):
            try:
                response = await self._client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=self.temperature,
                )
                
                response_time = time.time() - start_time
                text = response.choices[0].message.content or ""
                
                if response.usage:
                    usage = {
                        "prompt_tokens": response.usage.prompt_tokens,
                        "completion_tokens": response.usage.completion_tokens,
                        "total_tokens": response.usage.total_tokens,
                    }
                
                logger.info(
                    f"GroqProvider._chat_completion - Model: {self.model}, "
                    f"Response time: {response_time:.2f}s, "
                    f"Tokens - Prompt: {usage['prompt_tokens']}, "
                    f"Completion: {usage['completion_tokens']}, "
                    f"Total: {usage['total_tokens']}"
                )
                
                return text, usage
                
            except Exception as e:
                last_exception = e
                logger.warning(f"Groq API call attempt {attempt + 1} failed: {e}")
                if attempt < self.MAX_RETRIES:
                    logger.info("Retrying...")
                    
        logger.error(f"Groq API call failed after {self.MAX_RETRIES + 1} attempts: {last_exception}")
        raise last_exception

    def _parse_json_response(self, response: str) -> dict[str, Any]:
        """Parse JSON response from Groq.
        
        Extracts JSON from anywhere in the response, including markdown code blocks.
        
        Args:
            response: Text response from API
            
        Returns:
            Parsed JSON dictionary or empty dict if invalid
        """
        response = response.strip()
        
        if not response:
            logger.warning("Empty response from Groq")
            return {}
        
        # Try to find JSON code block first (```json ... ```)
        json_code_block_match = re.search(r'```json\s*([\s\S]*?)\s*```', response)
        if json_code_block_match:
            json_str = json_code_block_match.group(1).strip()
            try:
                return json.loads(json_str)
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse JSON from code block: {e}")
                logger.warning(f"Raw response was: '{response[:200]}...'")
                return {}
        
        # Try to find any code block (``` ... ```)
        code_block_match = re.search(r'```\s*([\s\S]*?)\s*```', response)
        if code_block_match:
            json_str = code_block_match.group(1).strip()
            try:
                return json.loads(json_str)
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse JSON from code block: {e}")
                logger.warning(f"Raw response was: '{response[:200]}...'")
                return {}
        
        # Try to extract JSON object directly (find {...} or [...] patterns)
        json_object_match = re.search(r'(\{[\s\S]*\}|\[[\s\S]*\])', response)
        if json_object_match:
            json_str = json_object_match.group(1).strip()
            try:
                return json.loads(json_str)
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse extracted JSON: {e}")
                logger.warning(f"Raw response was: '{response[:200]}...'")
                return {}
        
        # Try direct parse
        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON response from Groq: {e}")
            logger.warning(f"Raw response was: '{response[:200]}...'")
            return {}

    async def close(self) -> None:
        """Close the client connection."""
        await self._client.close()

    async def __aenter__(self) -> "GroqProvider":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()