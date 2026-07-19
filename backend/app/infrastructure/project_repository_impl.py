from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import Project
from app.domain.repositories import ProjectRepository
from app.infrastructure.models import ProjectModel


def _to_entity(row: ProjectModel) -> Project:
    return Project(
        id=row.id,
        name=row.name,
        description=row.description,
        status=row.status,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


def _to_model(entity: Project) -> ProjectModel:
    return ProjectModel(
        id=entity.id,
        name=entity.name,
        description=entity.description,
        status=entity.status,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
    )


class SqlAlchemyProjectRepository(ProjectRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, project: Project) -> Project:
        row = _to_model(project)
        self._session.add(row)
        await self._session.commit()
        await self._session.refresh(row)
        return _to_entity(row)

    async def get(self, project_id: UUID) -> Project | None:
        result = await self._session.execute(select(ProjectModel).where(ProjectModel.id == project_id))
        row = result.scalar_one_or_none()
        return _to_entity(row) if row else None

    async def list(self, limit: int = 50, offset: int = 0) -> list[Project]:
        result = await self._session.execute(
            select(ProjectModel).order_by(ProjectModel.created_at.desc()).limit(limit).offset(offset)
        )
        return [_to_entity(row) for row in result.scalars().all()]

    async def update(self, project: Project) -> Project:
        result = await self._session.execute(select(ProjectModel).where(ProjectModel.id == project.id))
        row = result.scalar_one_or_none()
        if row is None:
            raise ValueError(f"Project {project.id} not found")
        row.name = project.name
        row.description = project.description
        row.status = project.status
        row.updated_at = project.updated_at
        await self._session.commit()
        await self._session.refresh(row)
        return _to_entity(row)

    async def delete(self, project_id: UUID) -> bool:
        result = await self._session.execute(delete(ProjectModel).where(ProjectModel.id == project_id))
        await self._session.commit()
        return result.rowcount > 0
