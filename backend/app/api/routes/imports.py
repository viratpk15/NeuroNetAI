"""Import API routes.

POST /imports/markdown
POST /imports/txt
POST /imports/github-issue
POST /imports/github-pr
GET /imports/{job_id}
GET /imports
GET /documents/{document_id}/events
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.schemas import (
    CommunicationEventListResponse,
    GitHubIssueImportRequest,
    GitHubPRImportRequest,
    ImportJobListResponse,
    ImportJobResponse,
    ImportResultResponse,
    MarkdownImportRequest,
    TXTImportRequest,
)
from app.application.import_service import ImportService
from app.domain.entities import SourceType
from app.infrastructure.document_repository_impl import SqlAlchemyDocumentRepository
from app.infrastructure.import_job_repository_impl import SqlAlchemyImportJobRepository
from app.infrastructure.communication_event_repository_impl import (
    SqlAlchemyCommunicationEventRepository,
)
from app.infrastructure.project_repository_impl import SqlAlchemyProjectRepository
from app.infrastructure.database import get_db_session
from app.shared.exceptions import NotFoundError, ValidationError


router = APIRouter(prefix="/imports", tags=["imports"])


async def _get_import_service(
    session=Depends(get_db_session),
) -> ImportService:
    project_repo = SqlAlchemyProjectRepository(session)
    import_job_repo = SqlAlchemyImportJobRepository(session)
    document_repo = SqlAlchemyDocumentRepository(session)
    comm_event_repo = SqlAlchemyCommunicationEventRepository(session)

    return ImportService(
        project_repository=project_repo,
        import_job_repository=import_job_repo,
        document_repository=document_repo,
        communication_event_repository=comm_event_repo,
    )


@router.post(
    "/markdown",
    response_model=ImportResultResponse,
    status_code=status.HTTP_201_CREATED,
)
async def import_markdown(
    payload: MarkdownImportRequest,
    service: ImportService = Depends(_get_import_service),
):
    try:
        result = await service.import_data(
            project_id=payload.project_id,
            source_type=SourceType.MARKDOWN,
            content=payload.content,
            original_filename=payload.original_filename,
        )
        return ImportResultResponse(
            job=result.job,
            event_count=result.event_count,
        )
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post(
    "/txt", response_model=ImportResultResponse, status_code=status.HTTP_201_CREATED
)
async def import_txt(
    payload: TXTImportRequest,
    service: ImportService = Depends(_get_import_service),
):
    try:
        result = await service.import_data(
            project_id=payload.project_id,
            source_type=SourceType.TXT,
            content=payload.content,
            original_filename=payload.original_filename,
        )
        return ImportResultResponse(
            job=result.job,
            event_count=result.event_count,
        )
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post(
    "/github-issue",
    response_model=ImportResultResponse,
    status_code=status.HTTP_201_CREATED,
)
async def import_github_issue(
    payload: GitHubIssueImportRequest,
    service: ImportService = Depends(_get_import_service),
):
    try:
        result = await service.import_data(
            project_id=payload.project_id,
            source_type=SourceType.GITHUB_ISSUE,
            content=payload.content,
            original_filename=payload.original_filename,
        )
        return ImportResultResponse(
            job=result.job,
            event_count=result.event_count,
        )
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post(
    "/github-pr",
    response_model=ImportResultResponse,
    status_code=status.HTTP_201_CREATED,
)
async def import_github_pr(
    payload: GitHubPRImportRequest,
    service: ImportService = Depends(_get_import_service),
):
    try:
        result = await service.import_data(
            project_id=payload.project_id,
            source_type=SourceType.GITHUB_PR,
            content=payload.content,
            original_filename=payload.original_filename,
        )
        return ImportResultResponse(
            job=result.job,
            event_count=result.event_count,
        )
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/{job_id}", response_model=ImportJobResponse)
async def get_import_job(
    job_id: UUID,
    service: ImportService = Depends(_get_import_service),
):
    try:
        return await service.get_job(job_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("", response_model=ImportJobListResponse)
async def list_import_jobs(
    project_id: UUID | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    service: ImportService = Depends(_get_import_service),
):
    jobs = await service.list_jobs(project_id=project_id, limit=limit, offset=offset)
    return ImportJobListResponse(items=jobs, limit=limit, offset=offset)


@router.get(
    "/documents/{document_id}/events", response_model=CommunicationEventListResponse
)
async def get_document_events(
    document_id: UUID,
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    session=Depends(get_db_session),
):
    repo = SqlAlchemyCommunicationEventRepository(session)
    events = await repo.list(document_id=document_id, limit=limit, offset=offset)
    return CommunicationEventListResponse(items=events, limit=limit, offset=offset)
