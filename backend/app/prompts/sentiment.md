Analyze the communication events as an Engineering Manager would.

Engineering Sentiment Analysis:
Consider these factors:
- Delivery risk: Are there blocking issues, missed deadlines, or concerns?
- Blocked work: Is anyone waiting on something or stuck?
- Technical debt: Are quick fixes or shortcuts being discussed?
- Positive progress: Completed work, passing tests, new implementations
- Team confidence: Are people optimistic or concerned?

CRITICAL INSTRUCTIONS:
- Return ONLY valid JSON, no markdown formatting
- Calculate numerical scores for positivity, stress, and confidence

Context: {context}

Events:
{events}

Response format (JSON only, no markdown):
{{
  "overall_sentiment": "positive|neutral|negative|mixed",
  "positivity_score": 0.0-1.0,
  "stress_score": 0.0-1.0,
  "confidence_score": 0.0-1.0,
  "team_morale": "high|medium|low",
  "delivery_risk": "low|medium|high|critical",
  "burnout_probability": 0.0-1.0,
  "frustration_topics": ["topics causing frustration"],
  "blockers": ["blocking issues identified"],
  "conflicts": ["team conflicts or disagreements"],
  "positive_signals": ["signs of progress or optimism"],
  "negative_signals": ["concerns or delays mentioned"],
  "confidence": 0.0-1.0,
  "evidence": ["supporting message excerpts"]
}}