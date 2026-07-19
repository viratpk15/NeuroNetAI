"""Agent service for providing access to all AI agents."""
import logging
from typing import Any

from app.application.agents.conversation_agent import ConversationAgent
from app.application.agents.task_agent import TaskAgent
from app.application.agents.sentiment_agent import SentimentAgent
from app.application.agents.entity_agent import EntityAgent

logger = logging.getLogger(__name__)


class AgentService:
    """Service that provides access to all AI agents.
    
    This is the central service that agents use to process communication events.
    """

    def __init__(
        self,
        conversation_agent: ConversationAgent | None = None,
        task_agent: TaskAgent | None = None,
        sentiment_agent: SentimentAgent | None = None,
        entity_agent: EntityAgent | None = None,
    ):
        self.conversation_agent = conversation_agent or ConversationAgent()
        self.task_agent = task_agent or TaskAgent()
        self.sentiment_agent = sentiment_agent or SentimentAgent()
        self.entity_agent = entity_agent or EntityAgent()

    async def run_all_agents(
        self, communication_events: list[Any]
    ) -> dict[str, Any]:
        """Run all agents and aggregate results.
        
        Args:
            communication_events: List of CommunicationEvent entities to analyze
            
        Returns:
            Aggregated results from all agents
        """
        results: dict[str, Any] = {}

        # Run each agent
        results.update(await self.conversation_agent.process(communication_events))
        results.update(await self.task_agent.process(communication_events))
        results.update(await self.sentiment_agent.process(communication_events))
        results.update(await self.entity_agent.process(communication_events))

        return results