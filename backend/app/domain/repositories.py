"""Repository interfaces (ports). Infrastructure provides the implementation;
application/domain code only ever depends on these abstractions -- this is
what keeps the architecture "clean" and lets us swap Postgres for anything
else without touching business logic."""
from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.entities import CommunicationEvent, Document, ImportJob, Project


class ProjectRepository(ABC):
    @abstractmethod
    async def create(self, project: Project) -> Project: ...

    @abstractmethod
    async def get(self, project_id: UUID) -> Project | None: ...

    @abstractmethod
    async def list(self, limit: int = 50, offset: int = 0) -> list[Project]: ...

    @abstractmethod
    async def update(self, project: Project) -> Project: ...

    @abstractmethod
    async def delete(self, project_id: UUID) -> bool: ...


class ImportJobRepository(ABC):
    @abstractmethod
    async def create(self, job: ImportJob) -> ImportJob: ...

    @abstractmethod
    async def get(self, job_id: UUID) -> ImportJob | None: ...

    @abstractmethod
    async def list(self, project_id: UUID | None = None, limit: int = 50, offset: int = 0) -> list[ImportJob]: ...

    @abstractmethod
    async def update(self, job: ImportJob) -> ImportJob: ...


class DocumentRepository(ABC):
    @abstractmethod
    async def create(self, document: Document) -> Document: ...

    @abstractmethod
    async def get(self, document_id: UUID) -> Document | None: ...

    @abstractmethod
    async def list(self, project_id: UUID | None = None, limit: int = 50, offset: int = 0) -> list[Document]: ...


class CommunicationEventRepository(ABC):
    @abstractmethod
    async def create(self, event: CommunicationEvent) -> CommunicationEvent: ...

    @abstractmethod
    async def list(self, document_id: UUID, limit: int = 100, offset: int = 0) -> list[CommunicationEvent]: ...

    @abstractmethod
    async def count(self, document_id: UUID) -> int: ...
