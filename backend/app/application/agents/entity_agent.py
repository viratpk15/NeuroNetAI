"""Entity Extraction Agent for extracting entities from communication events."""
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


class EntityRelationship(BaseModel):
    """Pydantic model for entity relationships."""

    related_to: str = Field(default="", description="Related entity name")
    relationship_type: str = Field(
        default="references",
        description="Relationship type: used_by|depends_on|owns|belongs_to|references",
    )


class EntityItem(BaseModel):
    """Pydantic model for a single extracted entity."""

    entity_type: str = Field(default="", description="Entity type")
    name: str = Field(default="", description="Entity name")
    context: str = Field(default="", description="Supporting context")
    confidence: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Confidence score",
    )
    relationships: list[EntityRelationship] = Field(
        default_factory=list,
        description="Related entities",
    )
    evidence: list[str] = Field(
        default_factory=list,
        description="Supporting evidence",
    )


class EntityResponse(BaseModel):
    """Pydantic model for validated LLM entity extraction response."""

    entities: list[EntityItem] = Field(
        default_factory=list,
        description="List of extracted entities",
    )


class EntityAgent(BaseAgent):
    """Extracts entities from communication events.

    Uses LLM provider (Ollama/Gemini) when available, falls back to rule-based analysis.
    """

    # Entity patterns for rule-based fallback with proper categorization
    PATTERNS = {
        "person": [
            r"@(\w+)",  # @username mentions
            r"^\s*([A-Z][a-z]+)\s*:\s*",  # Speaker names at start of message followed by colon
            r"\b(Alice|Bob|Charlie|Sarah|Mike|Emma|John|Jane|David|David|Alex)\b",  # Common names
        ],
        "framework": [
            r"\b(FastAPI|Django|Flask|Express|Next\.?js|Nuxt|Spring|Rails|Laravel)\b",
            r"\b(Vue|React|Angular)\b",
        ],
        "programming_language": [
            r"\b(Python|JavaScript|TypeScript|Go|Rust|Java|C\+\+|C#|PHP|Ruby|Swift|Kotlin)\b",
        ],
        "database": [
            r"\b(PostgreSQL|MongoDb|Redis|MySQL|SQLite|Cassandra|DynamoDB|Supabase)\b",
        ],
        "technology": [
            r"\b(AWS|Azure|GCP|Docker|Kubernetes|Terraform|JWT|REST|GraphQL|API|Linux|Windows|macOS)\b",
        ],
        "tool": [
            r"\b(Git|GitHub|GitLab|Jenkins|CircleCI|Travis|npm|pip|yarn|Maven)\b",
        ],
        "concept": [
            r"\b(authentication|deployment|migration|testing|review|setup|configuration|integration|architecture)\b",
        ],
        "repository": [
            r"\b[\w-]+\/[\w-]+\b",  # owner/repo pattern
            r"github\.com/[\w-]+/[\w-]+",
        ],
        "api": [
            r"\b/v\d+(?:/[\w-]+)*\b",  # /v1/endpoint paths
            r"\b(API|endpoint|route):\s*/[\w/-]+",
        ],
        "organization": [
            r"\b(Inc|LLC|Corp|Company|Team|Organization)\b",
        ],
    }

    def __init__(self, project_name: str | None = None):
        self._project_name = project_name
        self._prompt_builder = PromptBuilder()

    async def process(self, events: list[CommunicationEvent]) -> dict[str, Any]:
        """Process communication events to extract entities.

        Uses LLM provider when available, falls back to rule-based analysis.

        Args:
            events: List of communication events to analyze

        Returns:
            Dictionary with 'entities' key containing list of entity dictionaries
        """
        if not events:
            return {"entities": []}

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
        logger.info("Using rule-based fallback for EntityAgent")
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
        prompt = self._prompt_builder.build_entity_prompt(events, self._project_name)

        logger.info(
            f"LLM request - provider: {provider.__class__.__name__}, "
            f"model: {getattr(provider, 'model', 'unknown')}, "
            f"prompt_size: {len(prompt)} chars",
        )

        response = await provider.extract_entities(events, self._project_name)

        latency_ms = int((time.time() - start_time) * 1000)

        # Validate response with Pydantic
        try:
            validated = EntityResponse(**response)
            entities = [entity.model_dump() for entity in validated.entities]

            logger.info(
                f"LLM response - latency: {latency_ms}ms, "
                f"entity_count: {len(entities)}",
            )

            return {"entities": entities}
        except Exception as e:
            logger.warning(f"Failed to validate LLM response, falling back: {e}")
            return None

    def _rule_based_process(self, events: list[CommunicationEvent]) -> dict[str, Any]:
        """Rule-based analysis fallback.

        Args:
            events: List of communication events to analyze

        Returns:
            Dictionary with analysis results
        """
        entities = []
        seen_entities = set()

        for event in events:
            # Extract author as person entity if present
            if event.author:
                author = event.author.strip()
                # Check if author looks like a person name (capitalized, not generic)
                if author and len(author) >= 2 and author.lower() not in ["unknown", "system", "bot", "task", "risk", "decision"]:
                    # Use the person name pattern to validate
                    person_pattern = r"^[A-Z][a-z]+$"
                    if re.match(person_pattern, author) or author.lower() in ["alice", "bob", "charlie", "sarah", "mike", "emma", "john", "jane", "alex"]:
                        entity_key = f"person:{author.lower()}"
                        if entity_key not in seen_entities:
                            seen_entities.add(entity_key)
                            entities.append({
                                "entity_type": "person",
                                "name": author,
                                "context": event.content[:150],
                                "confidence": 0.8,
                                "relationships": [],
                                "evidence": [event.content[:100]],
                            })

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
                                "confidence": 0.8 if entity_type in ("person", "technology", "database", "framework") else 0.7,
                                "relationships": [],
                                "evidence": [event.content[:100]],
                            })

        # Limit to reasonable number of entities
        entities = entities[:50]

        logger.info(f"EntityAgent rule-based found {len(entities)} entities")

        return {"entities": entities}

    def _normalize_entity_name(self, name: str) -> str:
        """Normalize entity names for deduplication."""
        # Normalize common variations
        name = re.sub(r'\s+', ' ', name).strip()
        # Normalize GPT-4 variants
        name = re.sub(r'gpt[-\s]?4', 'gpt4', name, flags=re.IGNORECASE)
        name = re.sub(r'openai\s+gpt4', 'gpt4', name, flags=re.IGNORECASE)
        return name.lower()