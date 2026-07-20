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

    # Keywords that indicate ACTUAL decisions (not action items)
    # Only match explicit decision language, NOT "will" which indicates tasks
    DECISION_KEYWORDS = [
        "decided to", "decided on", "agreed to use", "agreed on", 
        "we'll use", "we will use", "use ", "adopt", "selected", "chose",
        "confirmed", "approved", "final decision", "resolve",
    ]

    # Risk-indicating patterns
    RISK_KEYWORDS = [
        "pending", "blocked", "concern", "at risk", "might fail", "uncertain",
        "delayed", "behind", "worried", "testing pending", "review pending",
    ]

    # Action item patterns (separate from decisions)
    ACTION_KEYWORDS = [
        "will", "need to", "should", "going to", "plan to", "assigned to",
        "i'll", "i will", "take on", "work on", "implement", "deploy",
    ]

    # Topic categories
    TOPIC_PATTERNS = {
        "technical": ["api", "database", "server", "endpoint", "function", "code", "implementation"],
        "project_management": ["timeline", "deadline", "milestone", "sprint", "plan", "roadmap"],
        "bug": ["error", "bug", "issue", "crash", "fail", "broken", "not working"],
        "feature": ["feature", "enhancement", "new", "add", "implement", "request"],
        "review": ["review", "feedback", "approve", "merge", "pull request", "pr"],
    }

    # Technology keywords for summary generation
    TECH_KEYWORDS = [
        "fastapi", "django", "flask", "next.js", "jwt", "postgresql", "mongodb", 
        "redis", "python", "javascript", "typescript", "aws", "docker", "kubernetes",
        "authentication", "deployment", "migration", "staging",
    ]

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
        
        # TEMPORARY DEBUG LOGGING - FALLBACK DETECTION
        logger.info(f"ConversationAgent.process - PROVIDER AVAILABLE: {provider is not None}")
        if provider:
            logger.info(f"ConversationAgent.process - PROVIDER TYPE: {provider.__class__.__name__}")
            logger.info(f"ConversationAgent.process - MODEL: {getattr(provider, 'model', 'unknown')}")
        
        if provider:
            try:
                result = await self._llm_process(events, provider)
                if result is not None:
                    logger.info(f"ConversationAgent.process - LLM SUCCESS, returning result with keys: {list(result.keys())}")
                    return result
                else:
                    logger.warning("ConversationAgent.process - LLM returned None, falling back to rule-based")
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

        # TEMPORARY DEBUG LOGGING - TRACE PROMPT IN AGENT
        logger.info(f"ConversationAgent._llm_process - PROMPT BEING SENT: {prompt[:500]}")
        logger.info(f"ConversationAgent._llm_process - PROMPT FULL LENGTH: {len(prompt)}")

        logger.info(
            f"LLM request - provider: {provider.__class__.__name__}, "
            f"model: {getattr(provider, 'model', 'unknown')}, "
            f"prompt_size: {len(prompt)} chars",
        )

        response = await provider.summarize_conversation(events, self._project_name)

        # TEMPORARY DEBUG LOGGING - TRACE RESPONSE IN AGENT
        logger.info(f"ConversationAgent._llm_process - RAW RESPONSE FROM PROVIDER: {response}")

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
        # Generate summary
        summary = self._generate_summary_improved(events)

        # Extract topics
        all_content = " ".join(event.content for event in events)
        topics = self._extract_topics(events, all_content)

        # Extract decisions
        decisions = self._extract_decisions(events)

        # Extract risks
        risks = self._extract_risks(events)

        # Extract action items
        action_items = self._extract_action_items(events)

        logger.info(
            f"ConversationAgent rule-based found {len(topics)} topics, "
            f"{len(decisions)} decisions, {len(risks)} risks, {len(action_items)} action items",
        )

        return {
            "conversation_summary": summary,
            "discussion_topics": topics,
            "important_decisions": decisions,
            "risks": risks,
            "blockers": [],
            "action_items": action_items,
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

    def _generate_summary_improved(self, events: list[CommunicationEvent]) -> str:
        """Generate a concise executive summary of the conversation.

        Better logic that focuses on key topics and outcomes rather than just concatenating messages.
        Max 100 words.
        """
        # Extract key topics and entities
        tech_mentioned = []
        actions_mentioned = []
        
        for event in events:
            content = event.content
            # Look for technology mentions
            for keyword in self.TECH_KEYWORDS:
                if keyword in content.lower() and keyword not in tech_mentioned:
                    tech_mentioned.append(keyword.title())

        # Build a natural summary
        participants = list(set(e.author for e in events if e.author))
        
        # Find key discussion points
        discussion_points = []
        for event in events:
            content_lower = event.content.lower()
            if "migration" in content_lower or "migrate" in content_lower:
                discussion_points.append("backend migration")
            if "authentication" in content_lower or "auth" in content_lower:
                discussion_points.append("authentication progress")
            if "deploy" in content_lower or "deployment" in content_lower:
                discussion_points.append("deployment planning")
            if "database" in content_lower or "postgresql" in content_lower:
                discussion_points.append("database decisions")
            if "testing" in content_lower:
                discussion_points.append("testing updates")

        # Remove duplicates while preserving order
        seen = set()
        unique_points = []
        for p in discussion_points:
            if p not in seen:
                seen.add(p)
                unique_points.append(p)

        if unique_points:
            summary = f"A team meeting discussed {', '.join(unique_points[:4])}."
        elif len(events) <= 3:
            summary = ". ".join(e.content for e in events if e.content)
        else:
            summary = f"Discussion with {len(participants)} participants on project topics."

        # Clean up "Unknown:" prefixes
        summary = re.sub(r'\bUnknown:\s*', '', summary)
        
        # Ensure max 100 words
        words = summary.split()
        if len(words) > 100:
            summary = " ".join(words[:100])
            
        return summary

    def _extract_risks(self, events: list[CommunicationEvent]) -> list[str]:
        """Extract risks from events using risk keywords."""
        risks = []
        
        for event in events:
            content_lower = event.content.lower()
            for keyword in self.RISK_KEYWORDS:
                if keyword in content_lower:
                    # Extract the risk statement
                    match = re.search(
                        rf'.{{0,80}}{re.escape(keyword)}.{{0,80}}',
                        event.content,
                        re.IGNORECASE,
                    )
                    if match:
                        risk_text = match.group(0).strip()
                        # Clean up and normalize
                        if risk_text not in risks:
                            risks.append(risk_text)
        
        return risks[:10]

    def _extract_action_items(self, events: list[CommunicationEvent]) -> list[str]:
        """Extract action items from events."""
        action_items = []
        seen_actions = set()
        
        for event in events:
            content_lower = event.content.lower()
            for keyword in self.ACTION_KEYWORDS:
                if keyword in content_lower:
                    # Extract the action statement
                    match = re.search(
                        rf'.{{0,80}}{re.escape(keyword)}.{{0,80}}',
                        event.content,
                        re.IGNORECASE,
                    )
                    if match:
                        action_text = match.group(0).strip()
                        # Normalize
                        action_normalized = action_text.lower()[:50]
                        if action_normalized not in seen_actions:
                            seen_actions.add(action_normalized)
                            # Clean up "I will" prefix to make it more natural
                            action_text = re.sub(r'^(i\s+will|i\'ll|will)\s+', '', action_text, flags=re.IGNORECASE)
                            action_items.append(action_text)
        
        return action_items[:10]

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
