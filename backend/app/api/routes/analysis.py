"""API routes for AI Intelligence Engine analysis."""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from starlette.status import HTTP_404_NOT_FOUND

from app.api.dependencies import get_analysis_service
from app.api.schemas import (
    AnalysisResponse,
    EntityListResponse,
    SentimentResponse,
    TaskListResponse,
)
from app.application.analysis_service import AnalysisService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.post("/{project_id}", response_model=AnalysisResponse)
async def run_analysis(
    project_id: str,
    service: AnalysisService = Depends(get_analysis_service),
) -> AnalysisResponse:
    """Run AI analysis on a project's communication events."""

    await service.analyze_project_str(project_id, None)

    logger.info("Analysis completed for project %s", project_id)

    analysis = await service.get_analysis_str(project_id)

    if analysis is None:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail=f"Analysis failed for project {project_id}",
        )

    return AnalysisResponse(**analysis)


@router.get("/{project_id}", response_model=AnalysisResponse)
async def get_analysis(
    project_id: str,
    service: AnalysisService = Depends(get_analysis_service),
) -> AnalysisResponse:
    """Get the latest analysis results for a project."""

    analysis = await service.get_analysis_str(project_id)

    if analysis is None:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail=f"No analysis found for project {project_id}",
        )

    return AnalysisResponse(**analysis)


@router.get("/{project_id}/tasks", response_model=TaskListResponse)
async def get_tasks(
    project_id: str,
    limit: int = 100,
    offset: int = 0,
    service: AnalysisService = Depends(get_analysis_service),
) -> TaskListResponse:
    """Get extracted tasks for a project."""

    analysis = await service.get_analysis_str(project_id)

    if analysis is None:
        return TaskListResponse(
            items=[],
            limit=limit,
            offset=offset,
        )

    return TaskListResponse(
        items=analysis.get("tasks", []),
        limit=limit,
        offset=offset,
    )


@router.get("/{project_id}/sentiment", response_model=SentimentResponse)
async def get_sentiment(
    project_id: str,
    service: AnalysisService = Depends(get_analysis_service),
) -> SentimentResponse:
    """Get sentiment analysis for a project."""

    analysis = await service.get_analysis_str(project_id)

    if analysis is None:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail=f"No sentiment analysis found for project {project_id}",
        )

    sentiment = analysis.get("sentiment", {})

    return SentimentResponse(
        id=UUID(sentiment.get("id", "00000000-0000-0000-0000-000000000000")),
        project_id=UUID(
            sentiment.get(
                "project_id",
                "00000000-0000-0000-0000-000000000000",
            )
        ),
        agent_run_id=UUID(
            sentiment.get(
                "agent_run_id",
                "00000000-0000-0000-0000-000000000000",
            )
        ),
        overall_sentiment=sentiment.get("overall_sentiment", "neutral"),
        positivity_score=sentiment.get("positivity_score", 0.0),
        stress_score=sentiment.get("stress_score", 0.0),
        confidence_score=sentiment.get("confidence_score", 0.0),
        created_at=sentiment.get("created_at"),
    )


@router.get("/{project_id}/entities", response_model=EntityListResponse)
async def get_entities(
    project_id: str,
    limit: int = 100,
    offset: int = 0,
    service: AnalysisService = Depends(get_analysis_service),
) -> EntityListResponse:
    """Get extracted entities for a project."""

    analysis = await service.get_analysis_str(project_id)

    if analysis is None:
        return EntityListResponse(
            items=[],
            limit=limit,
            offset=offset,
        )

    return EntityListResponse(
        items=analysis.get("entities", []),
        limit=limit,
        offset=offset,
    )
