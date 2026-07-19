from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.dependencies import get_project_service
from app.api.schemas import (
    ProjectCreateRequest,
    ProjectListResponse,
    ProjectRenameRequest,
    ProjectResponse,
)
from app.application.project_service import ProjectService
from app.shared.exceptions import NotFoundError, ValidationError

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    payload: ProjectCreateRequest,
    service: ProjectService = Depends(get_project_service),
):
    try:
        project = await service.create_project(payload.name, payload.description)
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return project


@router.get("", response_model=ProjectListResponse)
async def list_projects(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    service: ProjectService = Depends(get_project_service),
):
    projects = await service.list_projects(limit=limit, offset=offset)
    return ProjectListResponse(items=projects, limit=limit, offset=offset)


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: UUID, service: ProjectService = Depends(get_project_service)):
    try:
        return await service.get_project(project_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.patch("/{project_id}", response_model=ProjectResponse)
async def rename_project(
    project_id: UUID,
    payload: ProjectRenameRequest,
    service: ProjectService = Depends(get_project_service),
):
    try:
        return await service.rename_project(project_id, payload.name)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/{project_id}/archive", response_model=ProjectResponse)
async def archive_project(project_id: UUID, service: ProjectService = Depends(get_project_service)):
    try:
        return await service.archive_project(project_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(project_id: UUID, service: ProjectService = Depends(get_project_service)):
    try:
        await service.delete_project(project_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
