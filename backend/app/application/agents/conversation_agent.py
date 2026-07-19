"""Conversation Agent for analyzing communication events."""
import logging
import re
from typing import Any

from app.domain.entities import CommunicationEvent
from app.application.agents.base import BaseAgent

logger = logging.getLogger(__name__)


class ConversationAgent(BaseAgent):
    """Analyzes communication events to produce conversation summaries and identify topics/decisions.
    
    This implementation uses deterministic rule-based analysis.
    When LLM providers are available, this can be replaced with LLM-powered analysis.
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

    async def process(self, events: list[CommunicationEvent]) -> dict[str, Any]:
        """Process communication events to extract summary, topics, and decisions.
        
        Args:
            events: List of communication events to analyze
            
        Returns:
            Dictionary with 'conversation_summary', 'discussion_topics', 'important_decisions'
        """
        if not events:
            return {
                "conversation_summary": "",
                "discussion_topics": [],
                "important_decisions": [],
            }

        # Combine all content for analysis
        all_content = " ".join(
            f"{event.author or 'Unknown'}: {event.content}"
            for event in events
        )

        # Generate summary (first 500 chars + truncation)
        summary = self._generate_summary(events, all_content)

        # Extract topics
        topics = self._extract_topics(events, all_content)

        # Extract decisions
        decisions = self._extract_decisions(events)

        logger.info(f"ConversationAgent found {len(topics)} topics, {len(decisions)} decisions")

        return {
            "conversation_summary": summary,
            "discussion_topics": topics,
            "important_decisions": decisions,
        }

    def _generate_summary(self, events: list[CommunicationEvent], content: str) -> str:
        """Generate a concise summary of the conversation."""
        if len(content) <= 300:
            return content

        # Find key sentences (those with specific patterns)
        sentences = re.split(r'[.!?]+', content)
        key_sentences = []

        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 20:  # Filter out short fragments
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
                        re.IGNORECASE
                    )
                    if match:
                        decisions.append(match.group(0).strip())
                    break

        # Deduplicate and limit
        unique_decisions = list(dict.fromkeys(decisions))[:5]
        return unique_decisions