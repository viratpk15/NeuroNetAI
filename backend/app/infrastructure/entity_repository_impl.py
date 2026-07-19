from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import Entity
from app.domain.repositories import EntityRepository
from app.infrastructure.models import EntityModel


def _to_entity(row: EntityModel) -> Entity:
    return Entity(
        id=row.id,
        project_id=row.project_id,
        agent_run_id=row.agent_run_id,
        entity_type=row.entity_type,
        name=row.name,
        context=row.context,
        confidence=row.confidence,
        created_at=row.created_at,
    )


def _to_model(entity: Entity) -> EntityModel:
    return EntityModel(
        id=entity.id,
        project_id=entity.project_id,
        agent_run_id=entity.agent_run_id,
        entity_type=entity.entity_type,
        name=entity.name,
        context=entity.context,
        confidence=entity.confidence,
        created_at=entity.created_at,
    )


class SqlAlchemyEntityRepository(EntityRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, entity: Entity) -> Entity:
        row = _to_model(entity)
        self._session.add(row)
        await self._session.commit()
        await self._session.refresh(row)
        return _to_entity(row)

    async def list(
        self,
        project_id: UUID,
        agent_run_id: UUID | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Entity]:
        stmt = select(EntityModel).where(EntityModel.project_id == project_id)
        if agent_run_id:
            stmt = stmt.where(EntityModel.agent_run_id == agent_run_id)
        stmt = stmt.order_by(EntityModel.created_at.desc()).limit(limit).offset(offset)
        result = await self._session.execute(stmt)
        return [_to_entity(row) for row in result.scalars().all()]