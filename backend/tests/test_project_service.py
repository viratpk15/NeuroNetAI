from uuid import UUID

import pytest

from app.application.project_service import ProjectService
from app.domain.entities import Project
from app.domain.repositories import ProjectRepository
from app.shared.exceptions import NotFoundError, ValidationError


class FakeProjectRepository(ProjectRepository):
    """In-memory repository so application-layer logic is testable without
    a real Postgres/Supabase connection."""

    def __init__(self):
        self._store: dict[UUID, Project] = {}

    async def create(self, project: Project) -> Project:
        self._store[project.id] = project
        return project

    async def get(self, project_id: UUID) -> Project | None:
        return self._store.get(project_id)

    async def list(self, limit: int = 50, offset: int = 0) -> list[Project]:
        return list(self._store.values())[offset : offset + limit]

    async def update(self, project: Project) -> Project:
        self._store[project.id] = project
        return project

    async def delete(self, project_id: UUID) -> bool:
        return self._store.pop(project_id, None) is not None


@pytest.fixture
def service() -> ProjectService:
    return ProjectService(FakeProjectRepository())


@pytest.mark.asyncio
async def test_create_project(service: ProjectService):
    project = await service.create_project("Platform Team", "Backend + infra")
    assert project.name == "Platform Team"
    assert project.status.value == "active"


@pytest.mark.asyncio
async def test_create_project_rejects_empty_name(service: ProjectService):
    with pytest.raises(ValidationError):
        await service.create_project("   ")


@pytest.mark.asyncio
async def test_get_missing_project_raises(service: ProjectService):
    with pytest.raises(NotFoundError):
        await service.get_project(UUID(int=0))


@pytest.mark.asyncio
async def test_rename_and_archive(service: ProjectService):
    project = await service.create_project("Old Name")
    renamed = await service.rename_project(project.id, "New Name")
    assert renamed.name == "New Name"

    archived = await service.archive_project(project.id)
    assert archived.status.value == "archived"


@pytest.mark.asyncio
async def test_delete_project(service: ProjectService):
    project = await service.create_project("Temp")
    await service.delete_project(project.id)
    with pytest.raises(NotFoundError):
        await service.get_project(project.id)
