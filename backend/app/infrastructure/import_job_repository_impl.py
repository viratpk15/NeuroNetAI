from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import ImportJob, ImportJobStatus
from app.domain.repositories import ImportJobRepository
from app.infrastructure.models import ImportJobModel


def _to_entity(row: ImportJobModel) -> ImportJob:
    return ImportJob(
        id=row.id,
        project_id=row.project_id,
        source_type=row.source_type,
        original_filename=row.original_filename,
        status=row.status,
        created_at=row.created_at,
        completed_at=row.completed_at,
        error_message=row.error_message,
        document_count=row.document_count,
    )


def _to_model(entity: ImportJob) -> ImportJobModel:
    return ImportJobModel(
        id=entity.id,
        project_id=entity.project_id,
        source_type=entity.source_type,
        original_filename=entity.original_filename,
        status=entity.status,
        created_at=entity.created_at,
        completed_at=entity.completed_at,
        error_message=entity.error_message,
        document_count=entity.document_count,
    )


class SqlAlchemyImportJobRepository(ImportJobRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def rollback(self) -> None:
        """Roll back the current session transaction. Used for error recovery."""
        await self._session.rollback()

    async def create(self, job: ImportJob) -> ImportJob:
        row = _to_model(job)
        self._session.add(row)
        await self._session.commit()
        await self._session.refresh(row)
        return _to_entity(row)

    async def get(self, job_id: UUID) -> ImportJob | None:
        result = await self._session.execute(select(ImportJobModel).where(ImportJobModel.id == job_id))
        row = result.scalar_one_or_none()
        return _to_entity(row) if row else None

    async def list(
        self, project_id: UUID | None = None, limit: int = 50, offset: int = 0
    ) -> list[ImportJob]:
        query = select(ImportJobModel)
        if project_id is not None:
            query = query.where(ImportJobModel.project_id == project_id)
        query = query.order_by(ImportJobModel.created_at.desc()).limit(limit).offset(offset)
        result = await self._session.execute(query)
        return [_to_entity(row) for row in result.scalars().all()]

    async def update(self, job: ImportJob) -> ImportJob:
        result = await self._session.execute(select(ImportJobModel).where(ImportJobModel.id == job.id))
        row = result.scalar_one_or_none()
        if row is None:
            raise ValueError(f"ImportJob {job.id} not found")
        row.project_id = job.project_id
        row.source_type = job.source_type
        row.original_filename = job.original_filename
        row.status = job.status
        row.completed_at = job.completed_at
        row.error_message = job.error_message
        row.document_count = job.document_count
        await self._session.commit()
        await self._session.refresh(row)
        return _to_entity(row)