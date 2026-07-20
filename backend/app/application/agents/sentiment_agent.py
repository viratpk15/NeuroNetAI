"""Sentiment Analysis Agent for analyzing communication sentiment and engineering risks."""
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


class SentimentResponse(BaseModel):
    """Pydantic model for validated LLM sentiment analysis response."""

    overall_sentiment: str = Field(default="neutral", description="Overall sentiment")
    team_morale: str = Field(default="medium", description="Team morale level")
    delivery_risk: str = Field(default="low", description="Delivery risk level")
    burnout_probability: float = Field(default=0.0, ge=0.0, le=1.0, description="Burnout probability")
    frustration_topics: list[str] = Field(default_factory=list, description="Frustration topics")
    blockers: list[str] = Field(default_factory=list, description="Blocking issues")
    conflicts: list[str] = Field(default_factory=list, description="Detected conflicts")
    positive_signals: list[str] = Field(default_factory=list, description="Positive signals")
    negative_signals: list[str] = Field(default_factory=list, description="Negative signals")
    confidence: float = Field(default=0.5, ge=0.0, le=1.0, description="Overall confidence")
    evidence: list[str] = Field(default_factory=list, description="Supporting evidence")


class SentimentAgent(BaseAgent):
    """Analyzes communication sentiment and engineering risks.

    Uses LLM provider (Ollama/Gemini) when available, falls back to rule-based analysis.
    """

    # Sentiment keywords
    POSITIVE_KEYWORDS = [
        "great", "awesome", "excellent", "good", "nice", "perfect", "working", "passing",
        "success", "completed", "done", "fixed", "resolved", "thanks", "appreciate",
    ]
    NEGATIVE_KEYWORDS = [
        "broken", "fail", "error", "bug", "issue", "problem", "bad", "terrible", "urgent",
        "critical", "blocked", "stuck", "waiting", "frustrated", "confused", "delay", "behind",
    ]
    STRESS_KEYWORDS = [
        "overtime", "deadline", "crunch", "urgent", "critical", "asap", "behind",
        "pressure", "stress", "burnout", "exhausted", "overworked", "sleepless",
    ]
    BURNOUT_KEYWORDS = [
        "exhausted", "burnout", "tired", "frustrated", "overworked", "crunch", "sleepless",
        "no time", "can't keep up", "overwhelmed", "drowning",
    ]

    def __init__(self, project_name: str | None = None):
        self._project_name = project_name
        self._prompt_builder = PromptBuilder()

    async def process(self, events: list[CommunicationEvent]) -> dict[str, Any]:
        """Process communication events to extract sentiment and risk analysis.

        Uses LLM provider when available, falls back to rule-based analysis.

        Args:
            events: List of communication events to analyze

        Returns:
            Dictionary with sentiment analysis results
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
        logger.info("Using rule-based fallback for SentimentAgent")
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
        prompt = self._prompt_builder.build_sentiment_prompt(events, self._project_name)

        logger.info(
            f"LLM request - provider: {provider.__class__.__name__}, "
            f"model: {getattr(provider, 'model', 'unknown')}, "
            f"prompt_size: {len(prompt)} chars",
        )

        response = await provider.analyze_sentiment(events, self._project_name)

        latency_ms = int((time.time() - start_time) * 1000)

        # Validate response with Pydantic
        try:
            validated = SentimentResponse(**response)

            logger.info(
                f"LLM response - latency: {latency_ms}ms, "
                f"risk_level: {validated.delivery_risk}, "
                f"confidence: {validated.confidence}",
            )

            result = validated.model_dump()
            # Maintain backward compatibility - map confidence to confidence_score
            result["confidence_score"] = result.pop("confidence", 0.5)
            result["positivity_score"] = 0.5
            result["stress_score"] = 0.5
            return result
        except Exception as e:
            logger.warning(f"Failed to validate LLM response, falling back: {e}")
            return None

    def _empty_response(self) -> dict[str, Any]:
        """Return empty response structure."""
        return {
            "overall_sentiment": "neutral",
            "team_morale": "medium",
            "delivery_risk": "low",
            "burnout_probability": 0.0,
            "frustration_topics": [],
            "blockers": [],
            "conflicts": [],
            "positive_signals": [],
            "negative_signals": [],
            "confidence_score": 0.0,
            "evidence": [],
        }

    def _rule_based_process(self, events: list[CommunicationEvent]) -> dict[str, Any]:
        """Rule-based analysis fallback.

        Args:
            events: List of communication events to analyze

        Returns:
            Dictionary with analysis results
        """
        positive_count = 0
        negative_count = 0
        stress_count = 0
        burnout_count = 0
        positive_signals = []
        negative_signals = []

        for event in events:
            content_lower = event.content.lower()

            for keyword in self.POSITIVE_KEYWORDS:
                if keyword in content_lower:
                    positive_count += 1
                    positive_signals.append(keyword)

            for keyword in self.NEGATIVE_KEYWORDS:
                if keyword in content_lower:
                    negative_count += 1
                    negative_signals.append(keyword)

            for keyword in self.STRESS_KEYWORDS:
                if keyword in content_lower:
                    stress_count += 1

            for keyword in self.BURNOUT_KEYWORDS:
                if keyword in content_lower:
                    burnout_count += 1

        # Determine overall sentiment
        if positive_count > negative_count:
            overall_sentiment = "positive"
        elif negative_count > positive_count:
            overall_sentiment = "negative"
        else:
            overall_sentiment = "neutral"

        # Determine team morale
        if positive_count > negative_count + 2:
            team_morale = "high"
        elif negative_count > positive_count + 2:
            team_morale = "low"
        else:
            team_morale = "medium"

        # Determine delivery risk
        if burnout_count > 0 or stress_count > 3:
            delivery_risk = "critical"
        elif stress_count > 1 or negative_count > 2:
            delivery_risk = "high"
        elif negative_count > 0:
            delivery_risk = "medium"
        else:
            delivery_risk = "low"

        burnout_probability = min(burnout_count / max(len(events), 1), 1.0)

        logger.info(
            f"SentimentAgent rule-based found sentiment: {overall_sentiment}, "
            f"morale: {team_morale}, "
            f"risk: {delivery_risk}",
        )

        # Calculate numerical scores
        total_events = max(len(events), 1)
        max_signals = max(max(positive_count, negative_count), 1)
        
        positivity_score = min(positive_count / max_signals, 1.0) if positive_count > 0 else 0.3
        stress_score = min(stress_count / total_events, 1.0)
        confidence_score = 0.5 + (positive_count + negative_count) / (total_events * 2)
        
        logger.info(
            f"SentimentAgent rule-based found sentiment: {overall_sentiment}, "
            f"morale: {team_morale}, "
            f"risk: {delivery_risk}, "
            f"positivity: {positivity_score:.2f}, "
            f"stress: {stress_score:.2f}",
        )

        return {
            "overall_sentiment": overall_sentiment,
            "team_morale": team_morale,
            "delivery_risk": delivery_risk,
            "burnout_probability": burnout_probability,
            "frustration_topics": list(set(negative_signals))[:5],
            "blockers": [],
            "conflicts": [],
            "positive_signals": list(set(positive_signals))[:5],
            "negative_signals": list(set(negative_signals))[:5],
            "confidence_score": round(confidence_score, 2),
            "positivity_score": round(positivity_score, 2),
            "stress_score": round(stress_score, 2),
            "evidence": [e.content[:100] for e in events[:3]],
        }
