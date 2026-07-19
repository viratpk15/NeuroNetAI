from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.project_service import ProjectService
from app.infrastructure.database import get_db_session
from app.infrastructure.project_repository_impl import SqlAlchemyProjectRepository


async def get_project_service(
    session: AsyncSession = Depends(get_db_session),
) -> AsyncGenerator[ProjectService, None]:
    repository = SqlAlchemyProjectRepository(session)
    yield ProjectService(repository)
