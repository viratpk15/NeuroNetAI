"""Analysis Service for orchestrating AI Intelligence Engine."""
import logging
import time
from uuid import UUID

from app.domain.entities import AgentRun, CommunicationEvent
from app.domain.repositories import (
    AgentRunRepository,
    CommunicationEventRepository,
    ConversationSummaryRepository,
    EntityRepository,
    SentimentResultRepository,
    TaskRepository,
)
from app.application.agent_service import AgentService

logger = logging.getLogger(__name__)


class AnalysisResult:
    """Result of running the AI analysis pipeline."""

    def __init__(
        self,
        agent_run: AgentRun,
        summary: str,
        topics: list[str],
        decisions: list[str],
        tasks: list[dict],
        sentiment: dict,
        entities: list[dict],
    ):
        self.agent_run = agent_run
        self.summary = summary
        self.topics = topics
        self.decisions = decisions
        self.tasks = tasks
        self.sentiment = sentiment
        self.entities = entities


class AnalysisService:
    """Service for running AI analysis on imported communication events.

    Workflow:
    Communication Events → Conversation Agent → Task Agent → Sentiment Agent → Entity Agent
    """

    def __init__(
        self,
        agent_run_repository: AgentRunRepository,
        communication_event_repository: CommunicationEventRepository,
        conversation_summary_repository: ConversationSummaryRepository,
        task_repository: TaskRepository,
        sentiment_result_repository: SentimentResultRepository,
        entity_repository: EntityRepository,
    ):
        self._agent_run_repository = agent_run_repository
        self._communication_event_repository = communication_event_repository
        self._conversation_summary_repository = conversation_summary_repository
        self._task_repository = task_repository
        self._sentiment_result_repository = sentiment_result_repository
        self._entity_repository = entity_repository

        self._agent_service = AgentService()

    def _str_to_uuid(self, id_str: str) -> UUID:
        """Convert string to UUID, creating one from the string if needed."""
        try:
            return UUID(id_str)
        except ValueError:
            return UUID(id_str.replace("-", "")[:32].ljust(32, "0"))

    async def analyze_project_str(
        self,
        project_id: str,
        communication_events: list[CommunicationEvent] | None = None,
    ) -> AnalysisResult:
        """Run complete AI analysis on a project's communication events.

        Args:
            project_id: The project ID as string
            communication_events: Optional events to analyze. If not provided, loads from DB.

        Returns:
            AnalysisResult with all extracted insights
        """
        project_uuid = self._str_to_uuid(project_id)
        if communication_events is None:
            events_with_metadata = await self._communication_event_repository.list_for_project(
                project_uuid
            )
            communication_events = [e for e, _ in events_with_metadata]
            logger.info(
                f"Loaded {len(communication_events)} events from project {project_id}"
            )
        return await self.analyze_project(project_uuid, communication_events)

    async def analyze_project(
        self,
        project_id: UUID,
        communication_events: list[CommunicationEvent],
    ) -> AnalysisResult:
        """Run complete AI analysis on a project's communication events.

        Args:
            project_id: The project to analyze
            communication_events: Events to analyze

        Returns:
            AnalysisResult with all extracted insights
        """
        start_time = time.time()

        # Create agent run record
        agent_run = AgentRun(project_id=project_id)
        agent_run = await self._agent_run_repository.create(agent_run)

        try:
            agent_run.mark_running()
            agent_run = await self._agent_run_repository.update(agent_run)

            # Run all agents
            results = await self._agent_service.run_all_agents(communication_events)

            # Store conversation summary
            summary = results.get("conversation_summary", "")
            topics = results.get("discussion_topics", [])
            decisions = results.get("important_decisions", [])

            from app.domain.entities import ConversationSummary
            conversation_summary = ConversationSummary(
                project_id=project_id,
                agent_run_id=agent_run.id,
                summary=summary,
                topics=topics,
                decisions=decisions,
            )
            await self._conversation_summary_repository.create(conversation_summary)

            # Store tasks
            tasks = results.get("tasks", [])
            from app.domain.entities import Task
            for task_data in tasks:
                task = Task(
                    project_id=project_id,
                    agent_run_id=agent_run.id,
                    title=task_data.get("title", ""),
                    description=task_data.get("description", ""),
                    assignee=task_data.get("assignee"),
                    priority=task_data.get("priority", "medium"),
                    status=task_data.get("status", "open"),
                    due_date=task_data.get("due_date"),
                )
                await self._task_repository.create(task)

            # Store sentiment
            from app.domain.entities import SentimentResult
            sentiment_result = SentimentResult(
                project_id=project_id,
                agent_run_id=agent_run.id,
                overall_sentiment=results.get("overall_sentiment", "neutral"),
                positivity_score=results.get("positivity_score", 0.0),
                stress_score=results.get("stress_score", 0.0),
                confidence_score=results.get("confidence_score", 0.0),
                delivery_risk=results.get("delivery_risk", "unknown"),
                team_morale=results.get("team_morale", "unknown"),
                burnout_probability=results.get("burnout_probability", 0.0),
                timeline_signals=results.get("timeline_signals", []),
                blockers=results.get("blockers", []),
                conflicts=results.get("conflicts", []),
            )
            await self._sentiment_result_repository.create(sentiment_result)

            # Store entities
            entities = results.get("entities", [])
            from app.domain.entities import Entity
            for entity_data in entities:
                entity = Entity(
                    project_id=project_id,
                    agent_run_id=agent_run.id,
                    entity_type=entity_data.get("entity_type", "unknown"),
                    name=entity_data.get("name", ""),
                    context=entity_data.get("context", ""),
                    confidence=entity_data.get("confidence", 0.5),
                )
                await self._entity_repository.create(entity)

            # Mark as completed
            agent_run.mark_completed(metadata={"event_count": len(communication_events)})
            agent_run = await self._agent_run_repository.update(agent_run)

            duration_ms = int((time.time() - start_time) * 1000)
            logger.info(
                f"Analysis completed - project_id: {project_id}, "
                f"duration: {duration_ms}ms, events: {len(communication_events)}"
            )

            return AnalysisResult(
                agent_run=agent_run,
                summary=summary,
                topics=topics,
                decisions=decisions,
                tasks=tasks,
                sentiment={
                    "overall_sentiment": results.get("overall_sentiment", "neutral"),
                    "positivity_score": results.get("positivity_score", 0.0),
                    "stress_score": results.get("stress_score", 0.0),
                    "confidence_score": results.get("confidence_score", 0.0),
                    "delivery_risk": results.get("delivery_risk", "unknown"),
                    "team_morale": results.get("team_morale", "unknown"),
                    "burnout_probability": results.get("burnout_probability", 0.0),
                    "timeline_signals": results.get("timeline_signals", []),
                    "blockers": results.get("blockers", []),
                },
                entities=entities,
            )

        except Exception as e:
            agent_run.mark_failed(str(e))
            await self._agent_run_repository.update(agent_run)
            logger.error(f"Analysis failed for project {project_id}: {e}")
            raise

    async def get_analysis_str(self, project_id: str) -> dict | None:
        """Get the latest analysis results for a project by string ID."""
        project_uuid = self._str_to_uuid(project_id)
        return await self.get_analysis(project_uuid)

    async def get_analysis(self, project_id: UUID) -> dict | None:
        """Get the latest analysis results for a project."""
        agent_run = await self._agent_run_repository.get_latest_for_project(project_id)
        if not agent_run:
            logger.info("AnalysisService.get_analysis - No agent_run found for project")
            return None

        # Get summary
        summaries = await self._conversation_summary_repository.get_for_project(project_id, agent_run.id)

        # Get tasks
        tasks = await self._task_repository.list(project_id, agent_run.id)

        # Get sentiment
        sentiment_row = await self._sentiment_result_repository.get_for_project(project_id, agent_run.id)

        # Get entities
        entities = await self._entity_repository.list(project_id, agent_run.id)

        return {
            "agent_run_id": str(agent_run.id),
            "status": agent_run.status,
            "summary": summaries.summary if summaries else "",
            "topics": summaries.topics if summaries else [],
            "decisions": summaries.decisions if summaries else [],
            "tasks": [
                {
                    "id": str(t.id),
                    "project_id": str(project_id),
                    "agent_run_id": str(agent_run.id),
                    "title": t.title,
                    "description": t.description,
                    "assignee": t.assignee,
                    "priority": t.priority,
                    "status": t.status,
                    "due_date": t.due_date,
                    "created_at": t.created_at,
                }
                for t in tasks
            ],
            "sentiment": {
                "id": str(sentiment_row.id) if sentiment_row else "00000000-0000-0000-0000-000000000000",
                "project_id": str(project_id),
                "agent_run_id": str(agent_run.id),
                "overall_sentiment": sentiment_row.overall_sentiment if sentiment_row else "neutral",
                "positivity_score": sentiment_row.positivity_score if sentiment_row else 0.0,
                "stress_score": sentiment_row.stress_score if sentiment_row else 0.0,
                "confidence_score": sentiment_row.confidence_score if sentiment_row else 0.0,
                "created_at": sentiment_row.created_at if sentiment_row else None,
            },
            "entities": [
                {
                    "id": str(e.id),
                    "project_id": str(project_id),
                    "agent_run_id": str(agent_run.id),
                    "entity_type": e.entity_type,
                    "name": e.name,
                    "context": e.context,
                    "confidence": e.confidence,
                    "created_at": e.created_at,
                }
                for e in entities
            ],
        }
