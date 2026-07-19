"""Import service: orchestrates the data import workflow.

Workflow: Upload → Validation → Parsing → Normalize Communication Events →
Store Documents → Store Communication Events → Update Import Job → Return Result
"""
import logging
from uuid import UUID

from app.domain.entities import (
    CommunicationEvent,
    Document,
    ImportJob,
    ImportJobStatus,
    SourceType,
)
from app.domain.repositories import (
    CommunicationEventRepository,
    DocumentRepository,
    ImportJobRepository,
    ProjectRepository,
)
from app.shared.exceptions import NotFoundError, ValidationError
from app.infrastructure.parsers import (
    GitHubIssueParser,
    GitHubPRParser,
    MarkdownParser,
    TXTParser,
)


logger = logging.getLogger(__name__)


class ImportResult:
    """Result of an import operation."""
    def __init__(self, job: ImportJob, event_count: int):
        self.job = job
        self.event_count = event_count


class ImportService:
    def __init__(
        self,
        project_repository: ProjectRepository,
        import_job_repository: ImportJobRepository,
        document_repository: DocumentRepository,
        communication_event_repository: CommunicationEventRepository,
    ):
        self._project_repository = project_repository
        self._import_job_repository = import_job_repository
        self._document_repository = document_repository
        self._communication_event_repository = communication_event_repository

    def _get_parser(self, source_type: SourceType):
        """Get the appropriate parser for the source type."""
        match source_type:
            case SourceType.MARKDOWN:
                return MarkdownParser()
            case SourceType.TXT:
                return TXTParser()
            case SourceType.GITHUB_ISSUE:
                return GitHubIssueParser()
            case SourceType.GITHUB_PR:
                return GitHubPRParser()
            case _:
                raise ValidationError(f"Unsupported source type: {source_type}")

    async def import_data(
        self,
        project_id: UUID,
        source_type: SourceType,
        content: str,
        original_filename: str | None = None,
    ) -> ImportResult:
        # Validate project exists
        project = await self._project_repository.get(project_id)
        if project is None:
            raise NotFoundError("Project", str(project_id))

        # Create import job
        job = ImportJob(
            project_id=project_id,
            source_type=source_type,
            original_filename=original_filename,
            status=ImportJobStatus.PENDING,
        )
        job = await self._import_job_repository.create(job)

        try:
            # Mark as processing
            job.mark_processing()
            job = await self._import_job_repository.update(job)

            # Validate content
            parser = self._get_parser(source_type)
            if not parser.validate(content):
                raise ValidationError("Invalid content format for the specified source type")

            # Create document and store
            document = Document(
                project_id=project_id,
                source_type=source_type,
                raw_content=content,
                import_job_id=job.id,
            )
            document = await self._document_repository.create(document)

            # Parse and extract communication events
            events = parser.parse(document.id, content)
            logger.info(f"Parsed {len(events)} communication events from {source_type}")

            # Store communication events
            for event in events:
                await self._communication_event_repository.create(event)

            # Update job as completed
            job.mark_completed(document_count=1)
            job = await self._import_job_repository.update(job)

            logger.info(f"Import completed: job {job.id}, {len(events)} events")
            return ImportResult(job=job, event_count=len(events))

        except ValidationError:
            job.mark_failed(f"Validation error for {source_type} import")
            await self._import_job_repository.update(job)
            raise
        except Exception as e:
            error_msg = str(e) if str(e) else "Unknown error during import"
            job.mark_failed(error_msg)
            await self._import_job_repository.update(job)
            logger.error(f"Import failed: job {job.id}, error: {error_msg}")
            raise

    async def get_job(self, job_id: UUID) -> ImportJob:
        job = await self._import_job_repository.get(job_id)
        if job is None:
            raise NotFoundError("ImportJob", str(job_id))
        return job

    async def list_jobs(self, project_id: UUID | None = None, limit: int = 50, offset: int = 0) -> list[ImportJob]:
        return await self._import_job_repository.list(project_id=project_id, limit=limit, offset=offset)