import json
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import ConversationSummary
from app.domain.repositories import ConversationSummaryRepository
from app.infrastructure.models import ConversationSummaryModel


def _to_entity(row: ConversationSummaryModel) -> ConversationSummary:
    topics = []
    if row.topics:
        try:
            topics = json.loads(row.topics) if isinstance(row.topics, str) else row.topics
        except (json.JSONDecodeError, TypeError):
            topics = []
    decisions = []
    if row.decisions:
        try:
            decisions = json.loads(row.decisions) if isinstance(row.decisions, str) else row.decisions
        except (json.JSONDecodeError, TypeError):
            decisions = []
    return ConversationSummary(
        id=row.id,
        project_id=row.project_id,
        agent_run_id=row.agent_run_id,
        summary=row.summary,
        topics=topics,
        decisions=decisions,
        created_at=row.created_at,
    )


def _to_model(entity: ConversationSummary) -> ConversationSummaryModel:
    return ConversationSummaryModel(
        id=entity.id,
        project_id=entity.project_id,
        agent_run_id=entity.agent_run_id,
        summary=entity.summary,
        topics=entity.topics,
        decisions=entity.decisions,
        created_at=entity.created_at,
    )


class SqlAlchemyConversationSummaryRepository(ConversationSummaryRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, summary: ConversationSummary) -> ConversationSummary:
        row = _to_model(summary)
        self._session.add(row)
        await self._session.commit()
        await self._session.refresh(row)
        return _to_entity(row)

    async def get(self, summary_id: UUID) -> ConversationSummary | None:
        result = await self._session.execute(
            select(ConversationSummaryModel).where(ConversationSummaryModel.id == summary_id)
        )
        row = result.scalar_one_or_none()
        return _to_entity(row) if row else None

    async def get_for_project(self, project_id: UUID, agent_run_id: UUID) -> ConversationSummary | None:
        result = await self._session.execute(
            select(ConversationSummaryModel)
            .where(
                (ConversationSummaryModel.project_id == project_id) &
                (ConversationSummaryModel.agent_run_id == agent_run_id)
            )
        )
        row = result.scalar_one_or_none()
        return _to_entity(row) if row else None