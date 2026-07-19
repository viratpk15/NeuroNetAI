"""Sentiment Agent for analyzing sentiment in communication events."""
import logging
from typing import Any

from app.domain.entities import CommunicationEvent
from app.application.agents.base import BaseAgent

logger = logging.getLogger(__name__)


class SentimentAgent(BaseAgent):
    """Analyzes sentiment in communication events.
    
    This implementation uses deterministic rule-based analysis.
    When LLM providers are available, this can be replaced with LLM-powered analysis.
    """

    # Sentiment-indicating words
    POSITIVE_WORDS = [
        "good", "great", "excellent", "awesome", "fantastic", "wonderful",
        "happy", "pleased", "glad", "excited", "positive", "love", "like",
        "success", "achieve", "complete", "working", "ready", "perfect",
    ]

    NEGATIVE_WORDS = [
        "bad", "terrible", "awful", "horrible", "hate", "dislike",
        "frustrated", "annoyed", "angry", "upset", "sad", "unhappy",
        "fail", "failed", "broken", "bug", "issue", "error", "problem",
        "concern", "worry", "stress", "stressed", "blocked", "stuck",
    ]

    STRESS_INDICATORS = [
        "urgent", "asap", "deadline", "pressure", "behind schedule",
        "overtime", "crunch", "blocked", "waiting", "delayed",
    ]

    async def process(self, events: list[CommunicationEvent]) -> dict[str, Any]:
        """Process communication events to extract sentiment scores.
        
        Args:
            events: List of communication events to analyze
            
        Returns:
            Dictionary with sentiment analysis results
        """
        if not events:
            return {
                "overall_sentiment": "neutral",
                "positivity_score": 0.0,
                "stress_score": 0.0,
                "confidence_score": 0.0,
            }

        positive_count = 0
        negative_count = 0
        stress_count = 0

        for event in events:
            content_lower = event.content.lower()
            positive_count += sum(1 for word in self.POSITIVE_WORDS if word in content_lower)
            negative_count += sum(1 for word in self.NEGATIVE_WORDS if word in content_lower)
            stress_count += sum(1 for word in self.STRESS_INDICATORS if word in content_lower)

        total_words = sum(len(event.content.split()) for event in events) or 1
        positivity_score = min(1.0, positive_count / max(1, total_words / 20))
        negativity_score = min(1.0, negative_count / max(1, total_words / 20))
        stress_score = min(1.0, stress_count / max(1, len(events) / 5))

        # Determine overall sentiment
        if positivity_score > negativity_score + 0.1:
            overall_sentiment = "positive"
        elif negativity_score > positivity_score + 0.1:
            overall_sentiment = "negative"
        else:
            overall_sentiment = "neutral"

        # Confidence based on ratio of sentiment words to total events
        confidence_score = min(1.0, (positive_count + negative_count) / max(1, len(events)))

        logger.info(f"SentimentAgent: {overall_sentiment} (pos={positivity_score:.2f}, neg={negativity_score:.2f})")

        return {
            "overall_sentiment": overall_sentiment,
            "positivity_score": round(positivity_score, 2),
            "stress_score": round(stress_score, 2),
            "confidence_score": round(confidence_score, 2),
        }