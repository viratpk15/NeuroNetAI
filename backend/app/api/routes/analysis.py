"""API routes for AI Intelligence Engine analysis."""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from starlette.status import HTTP_404_NOT_FOUND, HTTP_400_BAD_REQUEST

from app.api.schemas import (
    AnalysisResponse,
    EntityListResponse,
    TaskListResponse,
    SentimentResponse,
)
from app.application.analysis_service import AnalysisService
from app.shared.exceptions import NotFoundError

router = APIRouter(prefix="/analysis", tags=["analysis"])


# Dependency injection - will be set up in main.py
_analysis_service: AnalysisService | None = None


def get_analysis_service() -> AnalysisService:
    if _analysis_service is None:
        raise RuntimeError("Analysis service not initialized")
    return _analysis_service


def set_analysis_service(service: AnalysisService) -> None:
    global _analysis_service
    _analysis_service = service


@router.post("/{project_id}", response_model=AnalysisResponse)
async def run_analysis(
    project_id: UUID,
    service: AnalysisService = Depends(get_analysis_service),
) -> AnalysisResponse:
    """Run AI analysis on a project's communication events.
    
    This triggers the full analysis pipeline:
    - Conversation summarization
    - Task extraction
    - Sentiment analysis
    - Entity extraction
    """
    analysis = await service.analyze_project(project_id, [])
    return AnalysisResponse(
        agent_run_id=analysis.agent_run.id,
        status=analysis.agent_run.status,
        summary=analysis.summary,
        topics=[],  # Will be populated from repository
        decisions=[],
        tasks=analysis.tasks,
        sentiment=analysis.sentiment,
        entities=analysis.entities,
    )


@router.get("/{project_id}", response_model=AnalysisResponse)
async def get_analysis(
    project_id: UUID,
    service: AnalysisService = Depends(get_analysis_service),
) -> AnalysisResponse:
    """Get the latest analysis results for a project."""
    analysis = await service.get_analysis(project_id)
    if not analysis:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail=f"No analysis found for project {project_id}"
        )
    return AnalysisResponse(**analysis)


@router.get("/{project_id}/tasks", response_model=TaskListResponse)
async def get_tasks(
    project_id: UUID,
    limit: int = 100,
    offset: int = 0,
    service: AnalysisService = Depends(get_analysis_service),
) -> TaskListResponse:
    """Get extracted tasks for a project."""
    # Get latest analysis and return tasks
    analysis = await service.get_analysis(project_id)
    if not analysis:
        return TaskListResponse(items=[], limit=limit, offset=offset)
    
    return TaskListResponse(
        items=analysis.get("tasks", []),
        limit=limit,
        offset=offset,
    )


@router.get("/{project_id}/sentiment", response_model=SentimentResponse)
async def get_sentiment(
    project_id: UUID,
    service: AnalysisService = Depends(get_analysis_service),
) -> SentimentResponse:
    """Get sentiment analysis for a project."""
    analysis = await service.get_analysis(project_id)
    if not analysis:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail=f"No sentiment analysis found for project {project_id}"
        )
    sentiment = analysis.get("sentiment", {})
    return SentimentResponse(
        id=UUID("00000000-0000-0000-0000-000000000000"),  # Placeholder
        project_id=project_id,
        agent_run_id=analysis.get("agent_run_id", UUID("00000000-0000-0000-0000-000000000000")),
        overall_sentiment=sentiment.get("overall_sentiment", "neutral"),
        positivity_score=sentiment.get("positivity_score", 0.0),
        stress_score=sentiment.get("stress_score", 0.0),
        confidence_score=sentiment.get("confidence_score", 0.0),
        created_at=None,
    )


@router.get("/{project_id}/entities", response_model=EntityListResponse)
async def get_entities(
    project_id: UUID,
    limit: int = 100,
    offset: int = 0,
    service: AnalysisService = Depends(get_analysis_service),
) -> EntityListResponse:
    """Get extracted entities for a project."""
    analysis = await service.get_analysis(project_id)
    if not analysis:
        return EntityListResponse(items=[], limit=limit, offset=offset)
    
    return EntityListResponse(
        items=analysis.get("entities", []),
        limit=limit,
        offset=offset,
    )