import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, ForeignKey, JSON, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.entities import (
    AgentStatus,
    ImportJobStatus,
    ProjectStatus,
    SourceType,
)
from app.infrastructure.database import Base


def _utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class ProjectModel(Base):
    __tablename__ = "projects"

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[ProjectStatus] = mapped_column(
        Enum(ProjectStatus, name="project_status"), default=ProjectStatus.ACTIVE
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=_utc_now, onupdate=_utc_now
    )

    documents: Mapped[list["DocumentModel"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
    import_jobs: Mapped[list["ImportJobModel"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
    agent_runs: Mapped[list["AgentRunModel"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )


class DocumentModel(Base):
    """Raw imported source data (Slack export, GitHub issue thread, etc.)
    Phase 2 (data import + agents) populates and reads this table."""

    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("projects.id"), nullable=False
    )
    import_job_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("import_jobs.id"), nullable=True
    )
    source_type: Mapped[str] = mapped_column(String(50))
    raw_content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utc_now)

    project: Mapped[ProjectModel] = relationship(back_populates="documents")
    import_job: Mapped["ImportJobModel"] = relationship(
        back_populates="documents"
    )
    communication_events: Mapped[list["CommunicationEventModel"]] = relationship(
        back_populates="document", cascade="all, delete-orphan"
    )


class ImportJobModel(Base):
    """Import job tracking: tracks the status of data imports for a project."""

    __tablename__ = "import_jobs"

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("projects.id"), nullable=False
    )
    source_type: Mapped[SourceType] = mapped_column(
        Enum(SourceType, name="source_type"), nullable=False
    )
    original_filename: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[ImportJobStatus] = mapped_column(
        Enum(ImportJobStatus, name="import_job_status"), default=ImportJobStatus.PENDING
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utc_now)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    document_count: Mapped[int] = mapped_column(default=0)

    project: Mapped[ProjectModel] = relationship(back_populates="import_jobs")
    documents: Mapped[list[DocumentModel]] = relationship(back_populates="import_job")


class CommunicationEventModel(Base):
    """Normalized communication events extracted from imported documents."""

    __tablename__ = "communication_events"

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    document_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("documents.id"), nullable=False
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    source: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # e.g., "slack_message", "github_comment"
    author: Mapped[str | None] = mapped_column(String(255), nullable=True)
    metadata_json: Mapped[dict | None] = mapped_column(
        JSON, nullable=True, default=None
    )  # SQLAlchemy JSON type
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utc_now)

    document: Mapped[DocumentModel] = relationship(
        back_populates="communication_events"
    )


# AI Intelligence Engine Models

class AgentRunModel(Base):
    """Tracks AI agent pipeline runs for a project."""

    __tablename__ = "agent_runs"

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("projects.id"), nullable=False
    )
    status: Mapped[AgentStatus] = mapped_column(
        Enum(AgentStatus, name="agent_status"), default=AgentStatus.PENDING
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utc_now)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[dict | None] = mapped_column(JSON, nullable=True, default=None)

    project: Mapped[ProjectModel] = relationship(back_populates="agent_runs")


# Add relationship to ProjectModel
# Note: Will be added in separate edit to avoid forward reference issues


class ConversationSummaryModel(Base):
    """Conversation summaries generated by AI agents."""

    __tablename__ = "conversation_summaries"

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("projects.id"), nullable=False
    )
    agent_run_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("agent_runs.id"), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    topics: Mapped[list[str]] = mapped_column(JSON, nullable=True, default=lambda: [])
    decisions: Mapped[list[str]] = mapped_column(JSON, nullable=True, default=lambda: [])
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utc_now)


class TaskModel(Base):
    """Extracted tasks from communication events."""

    __tablename__ = "tasks"

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("projects.id"), nullable=False
    )
    agent_run_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("agent_runs.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    assignee: Mapped[str | None] = mapped_column(String(255), nullable=True)
    priority: Mapped[str] = mapped_column(String(20), default="medium")
    status: Mapped[str] = mapped_column(String(20), default="open")
    due_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utc_now)


class SentimentResultModel(Base):
    """Sentiment analysis results."""

    __tablename__ = "sentiment_results"

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("projects.id"), nullable=False
    )
    agent_run_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("agent_runs.id"), nullable=False)
    overall_sentiment: Mapped[str] = mapped_column(String(20), nullable=False)
    positivity_score: Mapped[float] = mapped_column(default=0.0)
    stress_score: Mapped[float] = mapped_column(default=0.0)
    confidence_score: Mapped[float] = mapped_column(default=0.0)
    delivery_risk: Mapped[str] = mapped_column(String(20), default="unknown")
    team_morale: Mapped[str] = mapped_column(String(20), default="unknown")
    burnout_probability: Mapped[float] = mapped_column(default=0.0)
    timeline_signals: Mapped[list[str]] = mapped_column(JSON, nullable=True, default=lambda: [])
    blockers: Mapped[list[str]] = mapped_column(JSON, nullable=True, default=lambda: [])
    conflicts: Mapped[list[str]] = mapped_column(JSON, nullable=True, default=lambda: [])
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utc_now)


class EntityModel(Base):
    """Extracted entities from communication events."""

    __tablename__ = "entities"

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("projects.id"), nullable=False
    )
    agent_run_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("agent_runs.id"), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    context: Mapped[str] = mapped_column(Text, default="")
    confidence: Mapped[float] = mapped_column(default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utc_now)
