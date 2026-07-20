from __future__ import annotations

import json
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import CommunicationEvent
from app.domain.repositories import CommunicationEventRepository
from app.infrastructure.models import CommunicationEventModel, DocumentModel


def _to_entity(row: CommunicationEventModel) -> CommunicationEvent:
    metadata = {}
    if row.metadata_json:
        try:
            metadata = json.loads(row.metadata_json) if isinstance(row.metadata_json, str) else row.metadata_json
        except (json.JSONDecodeError, TypeError):
            metadata = {}
    return CommunicationEvent(
        id=row.id,
        document_id=row.document_id,
        content=row.content,
        timestamp=row.timestamp,
        source=row.source,
        author=row.author,
        metadata=metadata,
        created_at=row.created_at,
    )


def _to_model(entity: CommunicationEvent) -> CommunicationEventModel:
    return CommunicationEventModel(
        id=entity.id,
        document_id=entity.document_id,
        content=entity.content,
        timestamp=entity.timestamp,
        source=entity.source,
        author=entity.author,
        metadata_json=entity.metadata if entity.metadata else None,
        created_at=entity.created_at,
    )


class SqlAlchemyCommunicationEventRepository(CommunicationEventRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, event: CommunicationEvent) -> CommunicationEvent:
        row = _to_model(event)
        self._session.add(row)
        await self._session.commit()
        await self._session.refresh(row)
        return _to_entity(row)

    async def list(
        self, document_id: UUID, limit: int = 100, offset: int = 0
    ) -> list[CommunicationEvent]:
        result = await self._session.execute(
            select(CommunicationEventModel)
            .where(CommunicationEventModel.document_id == document_id)
            .order_by(CommunicationEventModel.timestamp.asc())
            .limit(limit)
            .offset(offset)
        )
        return [_to_entity(row) for row in result.scalars().all()]

    async def count(self, document_id: UUID) -> int:
        result = await self._session.execute(
            select(func.count())
            .select_from(CommunicationEventModel)
            .where(CommunicationEventModel.document_id == document_id)
        )
        return result.scalar_one()

    async def list_for_project(
        self, project_id: UUID, limit: int = 500, offset: int = 0
    ) -> list[tuple[CommunicationEvent, dict]]:
        """List communication events for a project with document metadata."""
        result = await self._session.execute(
            select(CommunicationEventModel, DocumentModel.source_type)
            .join(DocumentModel, CommunicationEventModel.document_id == DocumentModel.id)
            .where(DocumentModel.project_id == project_id)
            .order_by(CommunicationEventModel.timestamp.asc())
            .limit(limit)
            .offset(offset)
        )
        events_with_metadata = []
        for event_row, source_type in result.all():
            event = _to_entity(event_row)
            metadata = {"source_type": source_type}
            events_with_metadata.append((event, metadata))
        return events_with_metadata