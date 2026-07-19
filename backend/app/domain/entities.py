"""Domain entities: plain Python dataclasses with no dependency on FastAPI,
SQLAlchemy, or Pydantic. This is the innermost layer of the architecture."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4


class ProjectStatus(str, Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class Project:
    name: str
    description: str = ""
    status: ProjectStatus = ProjectStatus.ACTIVE
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=_utc_now)
    updated_at: datetime = field(default_factory=_utc_now)

    def rename(self, new_name: str) -> None:
        if not new_name.strip():
            raise ValueError("Project name cannot be empty")
        self.name = new_name.strip()
        self.updated_at = _utc_now()

    def archive(self) -> None:
        self.status = ProjectStatus.ARCHIVED
        self.updated_at = _utc_now()


class ImportJobStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class SourceType(str, Enum):
    MARKDOWN = "markdown"
    TXT = "txt"
    GITHUB_ISSUE = "github_issue"
    GITHUB_PR = "github_pr"


@dataclass
class Document:
    project_id: UUID
    source_type: SourceType
    raw_content: str
    import_job_id: UUID | None = None
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=_utc_now)


@dataclass
class ImportJob:
    project_id: UUID
    source_type: SourceType
    original_filename: str | None = None
    status: ImportJobStatus = ImportJobStatus.PENDING
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=_utc_now)
    completed_at: datetime | None = None
    error_message: str | None = None
    document_count: int = 0

    def mark_processing(self) -> None:
        self.status = ImportJobStatus.PROCESSING
        self.completed_at = None

    def mark_completed(self, document_count: int = 0) -> None:
        self.status = ImportJobStatus.COMPLETED
        self.completed_at = _utc_now()
        self.document_count = document_count

    def mark_failed(self, error_message: str) -> None:
        self.status = ImportJobStatus.FAILED
        self.error_message = error_message
        self.completed_at = _utc_now()


@dataclass
class CommunicationEvent:
    document_id: UUID
    content: str
    timestamp: datetime
    source: str  # e.g., "slack_message", "github_comment"
    author: str | None = None
    metadata: dict | None = None
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=_utc_now)

    def __post_init__(self) -> None:
        if self.metadata is None:
            self.metadata = {}
