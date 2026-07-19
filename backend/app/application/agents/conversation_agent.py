"""Conversation Agent for analyzing communication events."""
import logging
import re
import time
from typing import Any

from pydantic import BaseModel, Field

from app.domain.entities import CommunicationEvent
from app.application.agents.base import BaseAgent
from app.infrastructure.ai_providers.factory import ProviderFactory
from app.infrastructure.ai_providers.base import AIProvider
from app.prompts.prompt_builder import PromptBuilder

logger = logging.getLogger(__name__)


class ConversationResponse(BaseModel):
    """Pydantic model for validated LLM conversation response."""

    summary: str = Field(default="", description="Conversation summary")
    topics: list[str] = Field(default_factory=list, description="Discussion topics")
    decisions: list[str] = Field(default_factory=list, description="Important decisions")
    risks: list[str] = Field(default_factory=list, description="Identified risks")
    blockers: list[str] = Field(default_factory=list, description="Blocking issues")
    action_items: list[str] = Field(default_factory=list, description="Action items")


class ConversationAgent(BaseAgent):
    """Analyzes communication events to produce conversation summaries and identify topics/decisions/risks.

    Uses LLM provider (Ollama/Gemini) when available, falls back to rule-based analysis.
    """

    # Keywords that indicate decisions
    DECISION_KEYWORDS = [
        "decided", "agreed", "will", "let's", "going to", "plan to",
        "confirmed", "approved", "final", "conclusion", "resolve",
    ]

    # Topic categories
    TOPIC_PATTERNS = {
        "technical": ["api", "database", "server", "endpoint", "function", "code", "implementation"],
        "project_management": ["timeline", "deadline", "milestone", "sprint", "plan", "roadmap"],
        "bug": ["error", "bug", "issue", "crash", "fail", "broken", "not working"],
        "feature": ["feature", "enhancement", "new", "add", "implement", "request"],
        "review": ["review", "feedback", "approve", "merge", "pull request", "pr"],
    }

    def __init__(self, project_name: str | None = None):
        self._project_name = project_name
        self._prompt_builder = PromptBuilder()

    async def process(self, events: list[CommunicationEvent]) -> dict[str, Any]:
        """Process communication events to extract summary, topics, decisions, risks.

        Uses LLM provider when available, falls back to rule-based analysis.

        Args:
            events: List of communication events to analyze

        Returns:
            Dictionary with conversation_summary, discussion_topics, important_decisions, risks, blockers, action_items
        """
        if not events:
            return self._empty_response()

        # Try LLM provider first
        provider = ProviderFactory.get_provider()
        if provider:
            try:
                result = await self._llm_process(events, provider)
                if result is not None:
                    return result
            except Exception as e:
                logger.warning(f"LLM provider failed, falling back to rule-based: {e}")

        # Fallback to rule-based analysis
        logger.info("Using rule-based fallback for ConversationAgent")
        return self._rule_based_process(events)

    async def _llm_process(
        self,
        events: list[CommunicationEvent],
        provider: AIProvider,
    ) -> dict[str, Any] | None:
        """Process using LLM provider with logging.

        Args:
            events: Communication events to analyze
            provider: AI provider to use

        Returns:
            Structured response or None on failure
        """
        start_time = time.time()
        prompt = self._prompt_builder.build_conversation_prompt(events, self._project_name)

        logger.info(
            f"LLM request - provider: {provider.__class__.__name__}, "
            f"model: {getattr(provider, 'model', 'unknown')}, "
            f"prompt_size: {len(prompt)} chars",
        )

        response = await provider.summarize_conversation(events, self._project_name)

        latency_ms = int((time.time() - start_time) * 1000)
        logger.info(
            f"LLM response - latency: {latency_ms}ms, "
            f"response_size: {len(str(response))} chars",
        )

        # Validate response with Pydantic
        try:
            validated = ConversationResponse(**response)
            return {
                "conversation_summary": validated.summary,
                "discussion_topics": validated.topics,
                "important_decisions": validated.decisions,
                "risks": validated.risks,
                "blockers": validated.blockers,
                "action_items": validated.action_items,
            }
        except Exception as e:
            logger.warning(f"Failed to validate LLM response, falling back: {e}")
            return None

    def _empty_response(self) -> dict[str, Any]:
        """Return empty response structure."""
        return {
            "conversation_summary": "",
            "discussion_topics": [],
            "important_decisions": [],
            "risks": [],
            "blockers": [],
            "action_items": [],
        }

    def _rule_based_process(self, events: list[CommunicationEvent]) -> dict[str, Any]:
        """Rule-based analysis fallback.

        Args:
            events: List of communication events to analyze

        Returns:
            Dictionary with analysis results
        """
        # Combine all content for analysis
        all_content = " ".join(
            f"{event.author or 'Unknown'}: {event.content}"
            for event in events
        )

        # Generate summary
        summary = self._generate_summary(events, all_content)

        # Extract topics
        topics = self._extract_topics(events, all_content)

        # Extract decisions
        decisions = self._extract_decisions(events)

        logger.info(
            f"ConversationAgent rule-based found {len(topics)} topics, "
            f"{len(decisions)} decisions",
        )

        # Rule-based can't extract risks/blockers/action_items reliably
        # Return empty arrays for those
        return {
            "conversation_summary": summary,
            "discussion_topics": topics,
            "important_decisions": decisions,
            "risks": [],
            "blockers": [],
            "action_items": [],
        }

    def _generate_summary(self, events: list[CommunicationEvent], content: str) -> str:
        """Generate a concise summary of the conversation."""
        if len(content) <= 300:
            return content

        # Find key sentences
        sentences = re.split(r'[.!?]+', content)
        key_sentences = []

        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 20:
                key_sentences.append(sentence)
            if len(key_sentences) >= 3:
                break

        summary = ". ".join(key_sentences[:3])
        if len(summary) > 250:
            summary = summary[:250] + "..."
        return summary + "." if not summary.endswith(".") else summary

    def _extract_topics(self, events: list[CommunicationEvent], content: str) -> list[str]:
        """Extract discussion topics from events."""
        topics = []
        content_lower = content.lower()

        for topic_name, keywords in self.TOPIC_PATTERNS.items():
            if any(keyword in content_lower for keyword in keywords):
                topics.append(topic_name)

        # Add source-based topics
        sources = set(event.source for event in events)
        for source in sources:
            if "github" in source.lower():
                if "issue" not in topics:
                    topics.append("issue")
            elif "slack" in source.lower() or "markdown" in source.lower():
                if "team_discussion" not in topics:
                    topics.append("team_discussion")

        return topics

    def _extract_decisions(self, events: list[CommunicationEvent]) -> list[str]:
        """Extract decisions from events."""
        decisions = []

        for event in events:
            content_lower = event.content.lower()
            for keyword in self.DECISION_KEYWORDS:
                if keyword in content_lower:
                    # Extract context around the decision
                    match = re.search(
                        rf'.{{0,50}}{re.escape(keyword)}.{{0,50}}',
                        event.content,
                        re.IGNORECASE,
                    )
                    if match:
                        decisions.append(match.group(0).strip())
                    break

        # Deduplicate and limit
        unique_decisions = list(dict.fromkeys(decisions))[:5]
        return unique_decisions