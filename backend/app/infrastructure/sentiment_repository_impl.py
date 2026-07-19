from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import SentimentResult
from app.domain.repositories import SentimentResultRepository
from app.infrastructure.models import SentimentResultModel


def _to_entity(row: SentimentResultModel) -> SentimentResult:
    return SentimentResult(
        id=row.id,
        project_id=row.project_id,
        agent_run_id=row.agent_run_id,
        overall_sentiment=row.overall_sentiment,
        positivity_score=row.positivity_score,
        stress_score=row.stress_score,
        confidence_score=row.confidence_score,
        created_at=row.created_at,
    )


def _to_model(entity: SentimentResult) -> SentimentResultModel:
    return SentimentResultModel(
        id=entity.id,
        project_id=entity.project_id,
        agent_run_id=entity.agent_run_id,
        overall_sentiment=entity.overall_sentiment,
        positivity_score=entity.positivity_score,
        stress_score=entity.stress_score,
        confidence_score=entity.confidence_score,
        created_at=entity.created_at,
    )


class SqlAlchemySentimentResultRepository(SentimentResultRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, result: SentimentResult) -> SentimentResult:
        row = _to_model(result)
        self._session.add(row)
        await self._session.commit()
        await self._session.refresh(row)
        return _to_entity(row)

    async def get_for_project(self, project_id: UUID, agent_run_id: UUID) -> SentimentResult | None:
        result = await self._session.execute(
            select(SentimentResultModel)
            .where(
                (SentimentResultModel.project_id == project_id) &
                (SentimentResultModel.agent_run_id == agent_run_id)
            )
        )
        row = result.scalar_one_or_none()
        return _to_entity(row) if row else None