"""Repository interfaces (ports). Infrastructure provides the implementation;
application/domain code only ever depends on these abstractions -- this is
what keeps the architecture "clean" and lets us swap Postgres for anything
else without touching business logic."""
from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.entities import (
    AgentRun,
    CommunicationEvent,
    ConversationSummary,
    Document,
    Entity,
    ImportJob,
    Project,
    SentimentResult,
    Task,
)


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

    async def rollback(self) -> None:
        """Roll back the current session transaction. Used for error recovery."""
        ...


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

    @abstractmethod
    async def list_for_project(self, project_id: UUID, limit: int = 500, offset: int = 0) -> list[tuple[CommunicationEvent, dict]]:
        """List communication events for a project with document metadata.

        Args:
            project_id: The project to get events for
            limit: Maximum number of events
            offset: Pagination offset

        Returns:
            List of tuples containing (CommunicationEvent, document_metadata)
        """
        ...


# AI Intelligence Engine Repositories

class AgentRunRepository(ABC):
    @abstractmethod
    async def create(self, run: AgentRun) -> AgentRun: ...

    @abstractmethod
    async def get(self, run_id: UUID) -> AgentRun | None: ...

    @abstractmethod
    async def get_latest_for_project(self, project_id: UUID) -> AgentRun | None: ...

    @abstractmethod
    async def list(self, project_id: UUID, limit: int = 50, offset: int = 0) -> list[AgentRun]: ...

    @abstractmethod
    async def update(self, run: AgentRun) -> AgentRun: ...


class ConversationSummaryRepository(ABC):
    @abstractmethod
    async def create(self, summary: ConversationSummary) -> ConversationSummary: ...

    @abstractmethod
    async def get(self, summary_id: UUID) -> ConversationSummary | None: ...

    @abstractmethod
    async def get_for_project(self, project_id: UUID, agent_run_id: UUID) -> ConversationSummary | None: ...


class TaskRepository(ABC):
    @abstractmethod
    async def create(self, task: Task) -> Task: ...

    @abstractmethod
    async def list(self, project_id: UUID, agent_run_id: UUID | None = None, limit: int = 100, offset: int = 0) -> list[Task]: ...

    @abstractmethod
    async def get(self, task_id: UUID) -> Task | None: ...


class SentimentResultRepository(ABC):
    @abstractmethod
    async def create(self, result: SentimentResult) -> SentimentResult: ...

    @abstractmethod
    async def get_for_project(self, project_id: UUID, agent_run_id: UUID) -> SentimentResult | None: ...


class EntityRepository(ABC):
    @abstractmethod
    async def create(self, entity: Entity) -> Entity: ...

    @abstractmethod
    async def list(self, project_id: UUID, agent_run_id: UUID | None = None, limit: int = 100, offset: int = 0) -> list[Entity]: ...