from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import Document
from app.domain.repositories import DocumentRepository
from app.infrastructure.models import DocumentModel


def _to_entity(row: DocumentModel) -> Document:
    return Document(
        id=row.id,
        project_id=row.project_id,
        import_job_id=row.import_job_id,
        source_type=row.source_type,
        raw_content=row.raw_content,
        created_at=row.created_at,
    )


def _to_model(entity: Document) -> DocumentModel:
    return DocumentModel(
        id=entity.id,
        project_id=entity.project_id,
        import_job_id=entity.import_job_id,
        source_type=entity.source_type,
        raw_content=entity.raw_content,
        created_at=entity.created_at,
    )


class SqlAlchemyDocumentRepository(DocumentRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, document: Document) -> Document:
        row = _to_model(document)
        self._session.add(row)
        await self._session.commit()
        await self._session.refresh(row)
        return _to_entity(row)

    async def get(self, document_id: UUID) -> Document | None:
        result = await self._session.execute(select(DocumentModel).where(DocumentModel.id == document_id))
        row = result.scalar_one_or_none()
        return _to_entity(row) if row else None

    async def list(
        self, project_id: UUID | None = None, limit: int = 50, offset: int = 0
    ) -> list[Document]:
        query = select(DocumentModel)
        if project_id is not None:
            query = query.where(DocumentModel.project_id == project_id)
        query = query.order_by(DocumentModel.created_at.desc()).limit(limit).offset(offset)
        result = await self._session.execute(query)
        return [_to_entity(row) for row in result.scalars().all()]