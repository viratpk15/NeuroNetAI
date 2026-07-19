"""Application layer: orchestrates domain entities + repositories to
implement use cases. No FastAPI or SQLAlchemy imports here -- this layer is
what makes the business logic testable in isolation."""
from uuid import UUID

from app.domain.entities import Project
from app.domain.repositories import ProjectRepository
from app.shared.exceptions import NotFoundError, ValidationError


class ProjectService:
    def __init__(self, repository: ProjectRepository):
        self._repository = repository

    async def create_project(self, name: str, description: str = "") -> Project:
        if not name or not name.strip():
            raise ValidationError("Project name is required")
        project = Project(name=name.strip(), description=description.strip())
        return await self._repository.create(project)

    async def get_project(self, project_id: UUID) -> Project:
        project = await self._repository.get(project_id)
        if project is None:
            raise NotFoundError("Project", str(project_id))
        return project

    async def list_projects(self, limit: int = 50, offset: int = 0) -> list[Project]:
        return await self._repository.list(limit=limit, offset=offset)

    async def rename_project(self, project_id: UUID, new_name: str) -> Project:
        project = await self.get_project(project_id)
        project.rename(new_name)
        return await self._repository.update(project)

    async def archive_project(self, project_id: UUID) -> Project:
        project = await self.get_project(project_id)
        project.archive()
        return await self._repository.update(project)

    async def delete_project(self, project_id: UUID) -> None:
        deleted = await self._repository.delete(project_id)
        if not deleted:
            raise NotFoundError("Project", str(project_id))
