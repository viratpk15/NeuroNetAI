from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.analysis_service import AnalysisService
from app.application.project_service import ProjectService
from app.infrastructure.database import get_db_session
from app.infrastructure.project_repository_impl import SqlAlchemyProjectRepository
from app.infrastructure.agent_run_repository_impl import SqlAlchemyAgentRunRepository
from app.infrastructure.communication_event_repository_impl import SqlAlchemyCommunicationEventRepository
from app.infrastructure.conversation_summary_repository_impl import SqlAlchemyConversationSummaryRepository
from app.infrastructure.task_repository_impl import SqlAlchemyTaskRepository
from app.infrastructure.sentiment_repository_impl import SqlAlchemySentimentResultRepository
from app.infrastructure.entity_repository_impl import SqlAlchemyEntityRepository


async def get_project_service(
    session: AsyncSession = Depends(get_db_session),
) -> AsyncGenerator[ProjectService, None]:
    repository = SqlAlchemyProjectRepository(session)
    yield ProjectService(repository)


async def get_analysis_service(
    session: AsyncSession = Depends(get_db_session),
) -> AsyncGenerator[AnalysisService, None]:
    yield AnalysisService(
        agent_run_repository=SqlAlchemyAgentRunRepository(session),
        communication_event_repository=SqlAlchemyCommunicationEventRepository(session),
        conversation_summary_repository=SqlAlchemyConversationSummaryRepository(session),
        task_repository=SqlAlchemyTaskRepository(session),
        sentiment_result_repository=SqlAlchemySentimentResultRepository(session),
        entity_repository=SqlAlchemyEntityRepository(session),
    )
