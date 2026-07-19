"""Repository interfaces (ports). Infrastructure provides the implementation;
application/domain code only ever depends on these abstractions -- this is
what keeps the architecture "clean" and lets us swap Postgres for anything
else without touching business logic."""
from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.entities import Project


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
