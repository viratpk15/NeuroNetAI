"""Entity Extraction Agent for extracting entities from communication events."""
import logging
import re
from typing import Any

from app.domain.entities import CommunicationEvent
from app.application.agents.base import BaseAgent

logger = logging.getLogger(__name__)


class EntityAgent(BaseAgent):
    """Extracts entities from communication events.
    
    This implementation uses deterministic rule-based analysis.
    When LLM providers are available, this can be replaced with LLM-powered analysis.
    """

    # Entity patterns
    PATTERNS = {
        "person": [
            r"@(\w+)",  # @username mentions
            r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b",  # Capitalized names
        ],
        "technology": [
            r"\b(Python|JavaScript|TypeScript|React|Vue|Angular|Node\.?js|FastAPI|Django|Flask)\b",
            r"\b(API|REST|GraphQL|SQL|NoSQL|PostgreSQL|MongoDB|Redis)\b",
            r"\b(AWS|Azure|GCP|Docker|Kubernetes|Terraform)\b",
        ],
        "repository": [
            r"\b[\w-]+\/[\w-]+\b",  # owner/repo pattern
            r"github\.com/[\w-]+/[\w-]+",
        ],
        "api": [
            r"\b/v\d+(?:/[\w-]+)*\b",  # /v1/endpoint paths
            r"\b(API|endpoint|route):\s*/[\w/-]+",
        ],
        "library": [
            r"\b(pydantic|sqlalchemy|httpx|requests|numpy|pandas|langchain|langgraph)\b",
        ],
        "framework": [
            r"\b(fastapi|django|flask|express|next\.?js|nuxt)\b",
        ],
        "deadline": [
            r"\b(?:due|by|deadline|milestone):\s*(?:\d{4}-\d{2}-\d{2}|\w+ \d{1,2})",
            r"\b(?:sprint|release)\s+(?:\d+|v\d)",
        ],
        "organization": [
            r"\b(Inc|LLC|Corp|Company|Team|Department|Organization)\b",
        ],
    }

    async def process(self, events: list[CommunicationEvent]) -> dict[str, Any]:
        """Process communication events to extract entities.
        
        Args:
            events: List of communication events to analyze
            
        Returns:
            Dictionary with 'entities' key containing list of entity dictionaries
        """
        if not events:
            return {"entities": []}

        entities = []
        seen_entities = set()

        for event in events:
            for entity_type, patterns in self.PATTERNS.items():
                for pattern in patterns:
                    matches = re.findall(pattern, event.content, re.IGNORECASE)
                    for match in matches:
                        if isinstance(match, str):
                            name = match.strip()
                        elif isinstance(match, tuple):
                            name = match[0] if match[0] else match[-1]
                        else:
                            continue

                        name = name.strip()
                        if len(name) < 2 or len(name) > 100:
                            continue

                        entity_key = f"{entity_type}:{name.lower()}"
                        if entity_key not in seen_entities:
                            seen_entities.add(entity_key)
                            entities.append({
                                "entity_type": entity_type,
                                "name": name,
                                "context": event.content[:150],
                                "confidence": 0.8 if entity_type in ("person", "technology") else 0.7,
                            })

        # Limit to reasonable number of entities
        entities = entities[:50]

        logger.info(f"EntityAgent found {len(entities)} entities")

        return {"entities": entities}