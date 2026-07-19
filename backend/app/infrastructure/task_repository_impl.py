from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import Task
from app.domain.repositories import TaskRepository
from app.infrastructure.models import TaskModel


def _to_entity(row: TaskModel) -> Task:
    return Task(
        id=row.id,
        project_id=row.project_id,
        agent_run_id=row.agent_run_id,
        title=row.title,
        description=row.description,
        assignee=row.assignee,
        priority=row.priority,
        status=row.status,
        due_date=row.due_date,
        created_at=row.created_at,
    )


def _to_model(entity: Task) -> TaskModel:
    return TaskModel(
        id=entity.id,
        project_id=entity.project_id,
        agent_run_id=entity.agent_run_id,
        title=entity.title,
        description=entity.description,
        assignee=entity.assignee,
        priority=entity.priority,
        status=entity.status,
        due_date=entity.due_date,
        created_at=entity.created_at,
    )


class SqlAlchemyTaskRepository(TaskRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, task: Task) -> Task:
        row = _to_model(task)
        self._session.add(row)
        await self._session.commit()
        await self._session.refresh(row)
        return _to_entity(row)

    async def list(
        self,
        project_id: UUID,
        agent_run_id: UUID | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Task]:
        stmt = select(TaskModel).where(TaskModel.project_id == project_id)
        if agent_run_id:
            stmt = stmt.where(TaskModel.agent_run_id == agent_run_id)
        stmt = stmt.order_by(TaskModel.created_at.desc()).limit(limit).offset(offset)
        result = await self._session.execute(stmt)
        return [_to_entity(row) for row in result.scalars().all()]

    async def get(self, task_id: UUID) -> Task | None:
        result = await self._session.execute(select(TaskModel).where(TaskModel.id == task_id))
        row = result.scalar_one_or_none()
        return _to_entity(row) if row else None