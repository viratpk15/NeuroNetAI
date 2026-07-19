"""Abstract base class for AI providers."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from app.domain.entities import CommunicationEvent


class AIProvider(ABC):
    """Abstract base class defining the interface for AI providers.
    
    All AI providers must implement these domain-specific methods
    rather than generic text generation.
    """

    @abstractmethod
    async def summarize_conversation(
        self,
        events: list[CommunicationEvent],
        project_name: str | None = None,
    ) -> dict[str, Any]:
        """Generate a conversation summary with topics and decisions.
        
        Args:
            events: List of communication events to analyze
            project_name: Optional project name for context
            
        Returns:
            Dictionary with 'summary', 'topics', and 'decisions' keys
        """
        ...

    @abstractmethod
    async def extract_tasks(
        self,
        events: list[CommunicationEvent],
        project_name: str | None = None,
    ) -> dict[str, Any]:
        """Extract actionable tasks from communication events.
        
        Args:
            events: List of communication events to analyze
            project_name: Optional project name for context
            
        Returns:
            Dictionary with 'tasks' key containing list of task dicts
        """
        ...

    @abstractmethod
    async def extract_entities(
        self,
        events: list[CommunicationEvent],
        project_name: str | None = None,
    ) -> dict[str, Any]:
        """Extract named entities from communication events.
        
        Args:
            events: List of communication events to analyze
            project_name: Optional project name for context
            
        Returns:
            Dictionary with 'entities' key containing list of entity dicts
        """
        ...

    @abstractmethod
    async def analyze_sentiment(
        self,
        events: list[CommunicationEvent],
        project_name: str | None = None,
    ) -> dict[str, Any]:
        """Analyze sentiment in communication events.
        
        Args:
            events: List of communication events to analyze
            project_name: Optional project name for context
            
        Returns:
            Dictionary with sentiment analysis results
        """
        ...

    @abstractmethod
    async def chat(
        self,
        messages: list[dict[str, str]],
        system_prompt: str | None = None,
    ) -> dict[str, Any]:
        """Engage in a chat conversation.
        
        Args:
            messages: List of message dicts with 'role' and 'content' keys
            system_prompt: Optional system prompt for context
            
        Returns:
            Dictionary with 'response' key containing the AI response
        """
        ...