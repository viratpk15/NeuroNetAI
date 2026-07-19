Analyze the communication events as an Engineering Manager would.

Extract engineering intelligence including team morale, delivery risks, burnout signals, and blockers.

Context: {context}

Events:
{events}

Response format (JSON):
{
  "overall_sentiment": "positive|neutral|negative|mixed",
  "team_morale": "high|medium|low",
  "delivery_risk": "low|medium|high|critical",
  "burnout_probability": 0.0-1.0,
  "frustration_topics": [],
  "blockers": [],
  "conflicts": [],
  "positive_signals": [],
  "negative_signals": [],
  "confidence": 0.0-1.0,
  "evidence": ["supporting message excerpts"]
}