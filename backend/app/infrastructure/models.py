import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, JSON, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.entities import ImportJobStatus, ProjectStatus, SourceType
from app.infrastructure.database import Base


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
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    documents: Mapped[list["DocumentModel"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
    import_jobs: Mapped[list["ImportJobModel"]] = relationship(
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
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

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
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
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
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    document: Mapped[DocumentModel] = relationship(
        back_populates="communication_events"
    )
