"""PromptBuilder service for assembling token-safe prompts for AI providers."""
from __future__ import annotations

from typing import Any
from datetime import datetime

from app.domain.entities import CommunicationEvent


class PromptBuilder:
    """Builds structured prompts for AI providers.
    
    Assembles prompts with:
    - Project metadata
    - Communication events
    - Timestamps
    - Participants
    - Token-safe formatting
    """

    # Default token limits for different models
    DEFAULT_MAX_TOKENS = 30000  # Gemini 2.0 Flash context window
    
    MAX_CONTENT_CHARS = 15000  # Limit content to stay within token budget

    def __init__(self, max_tokens: int = DEFAULT_MAX_TOKENS):
        self.max_tokens = max_tokens

    def build_conversation_prompt(
        self,
        events: list[CommunicationEvent],
        project_name: str | None = None,
    ) -> str:
        """Build a prompt for conversation summarization.
        
        Args:
            events: Communication events to analyze
            project_name: Optional project name for context
            
        Returns:
            Formatted prompt string
        """
        prompt_parts = []
        
        # Load template from conversation.md
        template = self._load_template("conversation.md")
        
        # Build context section
        context_parts = []
        if project_name:
            context_parts.append(f"Project: {project_name}")
        
        # Add unique participants
        participants = self._extract_participants(events)
        if participants:
            context_parts.append(f"Participants: {', '.join(participants)}")
        
        context = "\n".join(context_parts) if context_parts else "No additional context"
        
        # Build events section with token-safe formatting
        events_text = self._format_events(events, max_chars=self.MAX_CONTENT_CHARS)
        
        # Assemble prompt
        return template.format(
            context=context,
            events=events_text,
        )

    def build_task_prompt(
        self,
        events: list[CommunicationEvent],
        project_name: str | None = None,
    ) -> str:
        """Build a prompt for task extraction.
        
        Args:
            events: Communication events to analyze
            project_name: Optional project name for context
            
        Returns:
            Formatted prompt string
        """
        template = self._load_template("tasks.md")
        
        context_parts = []
        if project_name:
            context_parts.append(f"Project: {project_name}")
        
        participants = self._extract_participants(events)
        if participants:
            context_parts.append(f"Participants: {', '.join(participants)}")
        
        context = "\n".join(context_parts) if context_parts else "No additional context"
        events_text = self._format_events(events, max_chars=self.MAX_CONTENT_CHARS)
        
        return template.format(
            context=context,
            events=events_text,
        )

    def build_entity_prompt(
        self,
        events: list[CommunicationEvent],
        project_name: str | None = None,
    ) -> str:
        """Build a prompt for entity extraction.
        
        Args:
            events: Communication events to analyze
            project_name: Optional project name for context
            
        Returns:
            Formatted prompt string
        """
        template = self._load_template("entities.md")
        
        context_parts = []
        if project_name:
            context_parts.append(f"Project: {project_name}")
        
        context = "\n".join(context_parts) if context_parts else "No additional context"
        events_text = self._format_events(events, max_chars=self.MAX_CONTENT_CHARS)
        
        return template.format(
            context=context,
            events=events_text,
        )

    def build_sentiment_prompt(
        self,
        events: list[CommunicationEvent],
        project_name: str | None = None,
    ) -> str:
        """Build a prompt for sentiment analysis.
        
        Args:
            events: Communication events to analyze
            project_name: Optional project name for context
            
        Returns:
            Formatted prompt string
        """
        template = self._load_template("sentiment.md")
        
        context_parts = []
        if project_name:
            context_parts.append(f"Project: {project_name}")
        
        context = "\n".join(context_parts) if context_parts else "No additional context"
        events_text = self._format_events(events, max_chars=self.MAX_CONTENT_CHARS)
        
        return template.format(
            context=context,
            events=events_text,
        )

    def build_chat_prompt(
        self,
        messages: list[dict[str, str]],
        system_prompt: str | None = None,
    ) -> list[dict[str, str]]:
        """Build a prompt for chat conversations.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            system_prompt: Optional system prompt
            
        Returns:
            List of formatted message dicts
        """
        formatted_messages = []
        
        # Add system prompt if provided
        if system_prompt:
            formatted_messages.append({
                "role": "system",
                "content": system_prompt,
            })
        
        # Add chat template if no system prompt
        if not system_prompt:
            template = self._load_template("chat.md")
            formatted_messages.append({
                "role": "system",
                "content": template,
            })
        
        # Add user messages
        for msg in messages:
            if isinstance(msg, dict) and "role" in msg and "content" in msg:
                formatted_messages.append({
                    "role": msg["role"],
                    "content": msg["content"],
                })
        
        return formatted_messages

    def _load_template(self, template_name: str) -> str:
        """Load a prompt template from the prompts directory.
        
        Args:
            template_name: Name of the template file
            
        Returns:
            Template content as string
        """
        import os
        from pathlib import Path
        
        template_path = Path(__file__).parent / template_name
        
        try:
            with open(template_path, "r") as f:
                return f.read()
        except FileNotFoundError:
            # Return a basic template if file doesn't exist
            return self._get_default_template(template_name)

    def _get_default_template(self, template_name: str) -> str:
        """Get default template for a given type.

        Args:
            template_name: Name of the template

        Returns:
            Default template string
        """
        templates = {
            "conversation.md": """Analyze the following communication events and provide:
1. A concise summary (2-3 sentences)
2. Key discussion topics
3. Important decisions made

Context: {context}

Events:
{events}

Response format (JSON):
{{"summary": "...", "topics": ["..."], "decisions": ["..."]}}""",
            "tasks.md": """Extract actionable tasks from the following communication events.
Identify who is responsible for each task and infer priority.

Context: {context}

Events:
{events}

Response format (JSON):
{{"tasks": [{{"title": "...", "description": "...", "assignee": "@username or null", "priority": "low|medium|high"}}]}}""",
            "entities.md": """Extract named entities from the communication events.
Entity types: person, technology, repository, api, library, framework, deadline, organization

Context: {context}

Events:
{events}

Response format (JSON):
{{"entities": [{{"entity_type": "...", "name": "...", "context": "...", "confidence": 0.0-1.0}}]}}""",
            "sentiment.md": """Analyze the sentiment of the following communication events.
Consider overall tone, stress indicators, and confidence levels.

Context: {context}

Events:
{events}

Response format (JSON):
{{"overall_sentiment": "positive|neutral|negative", "positivity_score": 0.0-1.0, "stress_score": 0.0-1.0, "confidence_score": 0.0-1.0}}""",
            "chat.md": """You are a helpful AI assistant for NeuroNet AI, a multi-agent collaboration intelligence platform.
Provide clear, concise responses focused on project analysis and team insights.""",
        }
        return templates.get(template_name, "")

    def _extract_participants(self, events: list[CommunicationEvent]) -> list[str]:
        """Extract unique participant names from events.
        
        Args:
            events: Communication events
            
        Returns:
            Sorted list of unique participant names
        """
        participants = set()
        for event in events:
            if event.author:
                participants.add(event.author.strip())
        return sorted(participants)

    def _format_events(
        self,
        events: list[CommunicationEvent],
        max_chars: int = MAX_CONTENT_CHARS,
    ) -> str:
        """Format events into a token-safe string format.
        
        Args:
            events: Communication events to format
            max_chars: Maximum characters to include
            
        Returns:
            Formatted events string
        """
        if not events:
            return "No events to analyze"
        
        lines = []
        total_chars = 0
        
        for event in events:
            timestamp_str = ""
            if event.timestamp:
                timestamp_str = f" [{event.timestamp.isoformat()}]"
            
            line = f"{event.author or 'Unknown'}{timestamp_str}: {event.content}"
            
            # Check if adding this line would exceed limit
            if total_chars + len(line) > max_chars:
                # Add truncated indicator and stop
                remaining = events[events.index(event):]
                if remaining:
                    lines.append(f"... ({len(remaining)} more events)")
                break
            
            lines.append(line)
            total_chars += len(line) + 1  # +1 for newline
        
        return "\n".join(lines)