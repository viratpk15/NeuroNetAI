import json
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import AgentRun
from app.domain.repositories import AgentRunRepository
from app.infrastructure.models import AgentRunModel


def _to_entity(row: AgentRunModel) -> AgentRun:
    metadata = {}
    if row.metadata_json:
        try:
            metadata = json.loads(row.metadata_json) if isinstance(row.metadata_json, str) else row.metadata_json
        except (json.JSONDecodeError, TypeError):
            metadata = {}
    return AgentRun(
        id=row.id,
        project_id=row.project_id,
        status=row.status,
        created_at=row.created_at,
        completed_at=row.completed_at,
        error_message=row.error_message,
        metadata=metadata,
    )


def _to_model(entity: AgentRun) -> AgentRunModel:
    return AgentRunModel(
        id=entity.id,
        project_id=entity.project_id,
        status=entity.status,
        created_at=entity.created_at,
        completed_at=entity.completed_at,
        error_message=entity.error_message,
        metadata_json=entity.metadata if entity.metadata else None,
    )


class SqlAlchemyAgentRunRepository(AgentRunRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, run: AgentRun) -> AgentRun:
        row = _to_model(run)
        self._session.add(row)
        await self._session.commit()
        await self._session.refresh(row)
        return _to_entity(row)

    async def get(self, run_id: UUID) -> AgentRun | None:
        result = await self._session.execute(select(AgentRunModel).where(AgentRunModel.id == run_id))
        row = result.scalar_one_or_none()
        return _to_entity(row) if row else None

    async def get_latest_for_project(self, project_id: UUID) -> AgentRun | None:
        result = await self._session.execute(
            select(AgentRunModel)
            .where(AgentRunModel.project_id == project_id)
            .order_by(AgentRunModel.created_at.desc())
            .limit(1)
        )
        row = result.scalar_one_or_none()
        return _to_entity(row) if row else None

    async def list(self, project_id: UUID, limit: int = 50, offset: int = 0) -> list[AgentRun]:
        result = await self._session.execute(
            select(AgentRunModel)
            .where(AgentRunModel.project_id == project_id)
            .order_by(AgentRunModel.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return [_to_entity(row) for row in result.scalars().all()]

    async def update(self, run: AgentRun) -> AgentRun:
        result = await self._session.execute(select(AgentRunModel).where(AgentRunModel.id == run.id))
        row = result.scalar_one_or_none()
        if row is None:
            raise ValueError(f"AgentRun {run.id} not found")
        row.project_id = run.project_id
        row.status = run.status
        row.completed_at = run.completed_at
        row.error_message = run.error_message
        row.metadata_json = run.metadata if run.metadata else None
        await self._session.commit()
        await self._session.refresh(row)
        return _to_entity(row)