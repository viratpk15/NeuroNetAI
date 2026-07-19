from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from app.domain.entities import ImportJobStatus, ProjectStatus, SourceType


class ProjectCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str = Field(default="", max_length=2000)


class ProjectRenameRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)


class ProjectResponse(BaseModel):
    id: UUID
    name: str
    description: str
    status: ProjectStatus
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProjectListResponse(BaseModel):
    items: list[ProjectResponse]
    limit: int
    offset: int


# Import Schemas
class ImportCreateRequest(BaseModel):
    project_id: UUID = Field(description="ID of the project to import data into")
    original_filename: str | None = Field(default=None, max_length=255)


class MarkdownImportRequest(ImportCreateRequest):
    content: str = Field(min_length=1, description="Markdown content to import")


class TXTImportRequest(ImportCreateRequest):
    content: str = Field(min_length=1, description="TXT content to import")


class GitHubIssueImportRequest(ImportCreateRequest):
    content: str = Field(min_length=1, description="GitHub issue JSON to import")


class GitHubPRImportRequest(ImportCreateRequest):
    content: str = Field(min_length=1, description="GitHub PR JSON to import")


class ImportJobResponse(BaseModel):
    id: UUID
    project_id: UUID
    source_type: SourceType
    original_filename: str | None = None
    status: ImportJobStatus
    created_at: datetime
    completed_at: datetime | None = None
    error_message: str | None = None
    document_count: int

    model_config = {"from_attributes": True}


class ImportJobListResponse(BaseModel):
    items: list[ImportJobResponse]
    limit: int
    offset: int


class ImportResultResponse(BaseModel):
    job: ImportJobResponse
    event_count: int


class CommunicationEventResponse(BaseModel):
    id: UUID
    document_id: UUID
    content: str
    timestamp: datetime
    source: str
    author: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime

    model_config = {"from_attributes": True}


class CommunicationEventListResponse(BaseModel):
    items: list[CommunicationEventResponse]
    limit: int
    offset: int


# Analysis Schemas

class TaskResponse(BaseModel):
    id: UUID
    project_id: UUID
    agent_run_id: UUID
    title: str
    description: str
    assignee: str | None = None
    priority: str
    status: str
    due_date: datetime | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class TaskListResponse(BaseModel):
    items: list[TaskResponse]
    limit: int
    offset: int


class SentimentResponse(BaseModel):
    id: UUID
    project_id: UUID
    agent_run_id: UUID
    overall_sentiment: str
    positivity_score: float
    stress_score: float
    confidence_score: float
    created_at: datetime

    model_config = {"from_attributes": True}


class EntityResponse(BaseModel):
    id: UUID
    project_id: UUID
    agent_run_id: UUID
    entity_type: str
    name: str
    context: str
    confidence: float
    created_at: datetime

    model_config = {"from_attributes": True}


class EntityListResponse(BaseModel):
    items: list[EntityResponse]
    limit: int
    offset: int


class ConversationSummaryResponse(BaseModel):
    id: UUID
    project_id: UUID
    agent_run_id: UUID
    summary: str
    topics: list[str]
    decisions: list[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class AnalysisResponse(BaseModel):
    agent_run_id: UUID
    status: str
    summary: str
    topics: list[str]
    decisions: list[str]
    tasks: list[TaskResponse]
    sentiment: SentimentResponse | None
    entities: list[EntityResponse]

    model_config = {"from_attributes": True}
