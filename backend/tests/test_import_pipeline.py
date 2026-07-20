"""
Tests for the data import pipeline (Phase 2 Batch 1).

Tests:
- MarkdownParser
- TXTParser
- GitHubIssueParser
- GitHubPRParser
- ImportService
"""
import pytest
from uuid import UUID, uuid4

from app.domain.entities import Document, ImportJob, ImportJobStatus, SourceType
from app.domain.repositories import (
    CommunicationEventRepository,
    DocumentRepository,
    ImportJobRepository,
    ProjectRepository,
)
from app.application.import_service import ImportService, ImportResult
from app.infrastructure.parsers import (
    MarkdownParser,
    MarkdownParseError,
    TXTParser,
    TXTParseError,
    GitHubIssueParser,
    GitHubIssueParseError,
    GitHubPRParser,
    GitHubPRParseError,
)


# Sample test data
MARKDOWN_SAMPLE = """## 2024-01-15 09:30 - @alice

Hello team, how's the progress on the authentication feature?

## 2024-01-15 09:35 - @bob

Making good progress! Should be ready for review by end of day.

## 2024-01-15 10:00 - @charlie

I found an issue with the database migration. We need to update the schema.
"""

TXT_SLACK_SAMPLE = """[2024-01-15 09:30:00] <@alice>
Hey everyone, starting on the API integration now

[2024-01-15 09:35:00] <@bob>
Great! Let me know if you need the auth tokens

[2024-01-15 09:40:00] <@alice>
Got them, thanks!
"""

TXT_SIMPLE_SAMPLE = """2024-01-15 09:30 alice:
Let's discuss the roadmap for Q1

2024-01-15 09:35 bob:
Agreed. I'll draft something today.
"""

GITHUB_ISSUE_SAMPLE = """{
  "id": 123456,
  "number": 42,
  "title": "User login fails with valid credentials",
  "body": "When a user tries to log in with valid credentials, the API returns a 500 error. This started happening after yesterday's deployment.",
  "user": {"login": "reporter"},
  "created_at": "2024-01-15T09:30:00Z",
  "comments": [
    {
      "id": 789,
      "user": {"login": "developer"},
      "body": "I can reproduce this. It looks like a database connection issue.",
      "created_at": "2024-01-15T10:15:00Z"
    },
    {
      "id": 790,
      "user": {"login": "reporter"},
      "body": "Thanks for the quick response! Any ETA for the fix?",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ]
}"""

GITHUB_PR_SAMPLE = """{
  "id": 789012,
  "number": 17,
  "title": "Add user session management",
  "body": "This PR adds session management with automatic refresh tokens and secure cookie handling.",
  "user": {"login": "contributor"},
  "created_at": "2024-01-15T09:00:00Z",
  "comments": [
    {
      "id": 500,
      "user": {"login": "reviewer"},
      "body": "Looks good overall, but can we add more error handling?",
      "created_at": "2024-01-15T11:00:00Z"
    }
  ],
  "review_comments": [
    {
      "id": 501,
      "user": {"login": "reviewer"},
      "body": "Consider renaming this variable for clarity",
      "created_at": "2024-01-15T11:15:00Z",
      "diff_hunk": "@@ -42,7 +42,7 @@ def create_session"
    }
  ],
  "commits": [
    {
      "sha": "abc123def456",
      "commit": {
        "author": {"name": "contributor", "date": "2024-01-15T09:30:00Z"},
        "message": "feat: add session management endpoints"
      }
    },
    {
      "sha": "def789ghi012",
      "commit": {
        "author": {"name": "contributor", "date": "2024-01-15T10:00:00Z"},
        "message": "fix: handle expired tokens gracefully"
      }
    }
  ]
}"""


# Fake repositories for testing
class FakeProjectRepository(ProjectRepository):
    def __init__(self):
        self._store: dict[UUID, str] = {}

    async def create(self, project):
        self._store[project.id] = project
        return project

    async def get(self, project_id):
        return self._store.get(project_id)

    async def list(self, limit=50, offset=0):
        return list(self._store.values())[offset : offset + limit]

    async def update(self, project):
        self._store[project.id] = project
        return project

    async def delete(self, project_id):
        return self._store.pop(project_id, None) is not None


class FakeImportJobRepository(ImportJobRepository):
    def __init__(self):
        self._store: dict[UUID, ImportJob] = {}

    async def create(self, job: ImportJob) -> ImportJob:
        self._store[job.id] = job
        return job

    async def get(self, job_id: UUID) -> ImportJob | None:
        return self._store.get(job_id)

    async def list(self, project_id=None, limit=50, offset=0) -> list[ImportJob]:
        return list(self._store.values())[offset : offset + limit]

    async def update(self, job: ImportJob) -> ImportJob:
        self._store[job.id] = job
        return job


class FakeDocumentRepository(DocumentRepository):
    def __init__(self):
        self._store: dict[UUID, Document] = {}

    async def create(self, document: Document) -> Document:
        self._store[document.id] = document
        return document

    async def get(self, document_id: UUID) -> Document | None:
        return self._store.get(document_id)

    async def list(self, project_id=None, limit=50, offset=0) -> list[Document]:
        return list(self._store.values())[offset : offset + limit]


class FakeCommunicationEventRepository(CommunicationEventRepository):
    def __init__(self):
        self._events: list = []

    async def create(self, event):
        self._events.append(event)
        return event

    async def list(self, document_id, limit=100, offset=0):
        return self._events[offset : offset + limit]

    async def count(self, document_id):
        return len(self._events)

    async def list_for_project(self, project_id, limit=500, offset=0):
        return [(e, {}) for e in self._events[offset : offset + limit]]


# Parser Tests
class TestMarkdownParser:
    def test_validate_valid_markdown(self):
        parser = MarkdownParser()
        assert parser.validate(MARKDOWN_SAMPLE) is True

    def test_validate_empty_content(self):
        parser = MarkdownParser()
        assert parser.validate("") is False
        assert parser.validate("   ") is False

    def test_validate_no_headers(self):
        parser = MarkdownParser()
        assert parser.validate("Hello world\nNo headers here") is False

    def test_parse_extracts_events(self):
        parser = MarkdownParser()
        events = parser.parse(uuid4(), MARKDOWN_SAMPLE)
        assert len(events) == 3

    def test_parse_event_content(self):
        parser = MarkdownParser()
        events = parser.parse(uuid4(), MARKDOWN_SAMPLE)
        assert "authentication feature" in events[0].content
        assert events[0].author == "alice"
        assert events[0].source == "markdown_message"

    def test_parse_raises_on_invalid(self):
        parser = MarkdownParser()
        with pytest.raises(MarkdownParseError):
            parser.parse(uuid4(), "no valid headers")


class TestTXTParser:
    def test_validate_slack_format(self):
        parser = TXTParser()
        assert parser.validate(TXT_SLACK_SAMPLE) is True

    def test_validate_simple_format(self):
        parser = TXTParser()
        assert parser.validate(TXT_SIMPLE_SAMPLE) is True

    def test_validate_empty_content(self):
        parser = TXTParser()
        assert parser.validate("") is False

    def test_validate_plain_text_accepted(self):
        parser = TXTParser()
        # Plain text without headers should be accepted
        assert parser.validate("Hello world") is True
        assert parser.validate("Alice: ... Bob: ...") is True

    def test_validate_whitespace_only_rejected(self):
        parser = TXTParser()
        assert parser.validate("   ") is False
        assert parser.validate("\n\n\n") is False

    def test_parse_slack_format(self):
        parser = TXTParser()
        events = parser.parse(uuid4(), TXT_SLACK_SAMPLE)
        assert len(events) == 3
        assert events[0].author == "alice"
        assert events[0].source == "txt_message"

    def test_parse_simple_format(self):
        parser = TXTParser()
        events = parser.parse(uuid4(), TXT_SIMPLE_SAMPLE)
        assert len(events) == 2
        assert events[0].author == "alice"

    def test_parse_plain_text(self):
        parser = TXTParser()
        # Plain text should be parsed as a single event
        events = parser.parse(uuid4(), "Hello world")
        assert len(events) == 1
        assert events[0].content == "Hello world"
        assert events[0].author is None
        assert events[0].source == "txt_message"

    def test_parse_multiline_plain_text(self):
        parser = TXTParser()
        # Multiline plain text should be parsed as a single event
        events = parser.parse(uuid4(), "Alice: Let's meet\nBob: OK")
        assert len(events) == 1
        assert "Alice: Let's meet" in events[0].content

    def test_parse_raises_on_empty(self):
        parser = TXTParser()
        with pytest.raises(TXTParseError):
            parser.parse(uuid4(), "")

    def test_parse_raises_on_whitespace_only(self):
        parser = TXTParser()
        with pytest.raises(TXTParseError):
            parser.parse(uuid4(), "   \n\n")


class TestGitHubIssueParser:
    def test_validate_valid_json(self):
        parser = GitHubIssueParser()
        assert parser.validate(GITHUB_ISSUE_SAMPLE) is True

    def test_validate_empty_content(self):
        parser = GitHubIssueParser()
        assert parser.validate("") is False

    def test_validate_no_id_field(self):
        parser = GitHubIssueParser()
        assert parser.validate('{"title": "test"}') is False

    def test_validate_invalid_json(self):
        parser = GitHubIssueParser()
        assert parser.validate("not json") is False

    def test_parse_extracts_events(self):
        parser = GitHubIssueParser()
        events = parser.parse(uuid4(), GITHUB_ISSUE_SAMPLE)
        assert len(events) == 3  # 1 body + 2 comments

    def test_parse_body_as_event(self):
        parser = GitHubIssueParser()
        events = parser.parse(uuid4(), GITHUB_ISSUE_SAMPLE)
        body_event = [e for e in events if e.source == "github_issue_body"][0]
        assert body_event.author == "reporter"
        assert "500 error" in body_event.content

    def test_parse_comments_as_events(self):
        parser = GitHubIssueParser()
        events = parser.parse(uuid4(), GITHUB_ISSUE_SAMPLE)
        comment_events = [e for e in events if e.source == "github_comment"]
        assert len(comment_events) == 2

    def test_parse_raises_on_invalid_json(self):
        parser = GitHubIssueParser()
        with pytest.raises(GitHubIssueParseError):
            parser.parse(uuid4(), "not valid json")


class TestGitHubPRParser:
    def test_validate_valid_json(self):
        parser = GitHubPRParser()
        assert parser.validate(GITHUB_PR_SAMPLE) is True

    def test_validate_empty_content(self):
        parser = GitHubPRParser()
        assert parser.validate("") is False

    def test_validate_invalid_json(self):
        parser = GitHubPRParser()
        assert parser.validate("not json") is False

    def test_parse_extracts_all_event_types(self):
        parser = GitHubPRParser()
        events = parser.parse(uuid4(), GITHUB_PR_SAMPLE)
        assert len(events) == 5  # 1 body + 1 comment + 1 review + 2 commits

    def test_parse_body_as_event(self):
        parser = GitHubPRParser()
        events = parser.parse(uuid4(), GITHUB_PR_SAMPLE)
        body_event = [e for e in events if e.source == "github_pr_body"][0]
        assert body_event.author == "contributor"

    def test_parse_review_comments(self):
        parser = GitHubPRParser()
        events = parser.parse(uuid4(), GITHUB_PR_SAMPLE)
        review_events = [e for e in events if e.source == "github_pr_review_comment"]
        assert len(review_events) == 1

    def test_parse_commits(self):
        parser = GitHubPRParser()
        events = parser.parse(uuid4(), GITHUB_PR_SAMPLE)
        commit_events = [e for e in events if e.source == "github_pr_commit"]
        assert len(commit_events) == 2

    def test_parse_raises_on_invalid_json(self):
        parser = GitHubPRParser()
        with pytest.raises(GitHubPRParseError):
            parser.parse(uuid4(), "not valid json")


# ImportService Tests
class TestImportService:
    @pytest.fixture
    def service(self):
        fake_project_repo = FakeProjectRepository()
        fake_job_repo = FakeImportJobRepository()
        fake_doc_repo = FakeDocumentRepository()
        fake_event_repo = FakeCommunicationEventRepository()

        # Create a test project
        from app.domain.entities import Project
        test_project = Project(id=uuid4(), name="Test Project")
        fake_project_repo._store[test_project.id] = test_project

        return ImportService(
            project_repository=fake_project_repo,
            import_job_repository=fake_job_repo,
            document_repository=fake_doc_repo,
            communication_event_repository=fake_event_repo,
        ), fake_project_repo, fake_job_repo, fake_doc_repo, fake_event_repo

    async def test_import_markdown_creates_job_and_events(
        self, service
    ):
        svc, project_repo, job_repo, doc_repo, event_repo = service
        project = list(project_repo._store.values())[0]

        result = await svc.import_data(
            project_id=project.id,
            source_type=SourceType.MARKDOWN,
            content=MARKDOWN_SAMPLE,
            original_filename="test.md",
        )

        assert isinstance(result, ImportResult)
        assert result.event_count == 3
        assert result.job.status == ImportJobStatus.COMPLETED
        assert result.job.source_type == SourceType.MARKDOWN
        assert result.job.original_filename == "test.md"

    async def test_import_txt_creates_job_and_events(
        self, service
    ):
        svc, project_repo, job_repo, doc_repo, event_repo = service
        project = list(project_repo._store.values())[0]

        result = await svc.import_data(
            project_id=project.id,
            source_type=SourceType.TXT,
            content=TXT_SLACK_SAMPLE,
        )

        assert result.event_count == 3
        assert result.job.status == ImportJobStatus.COMPLETED

    async def test_import_txt_plain_text(
        self, service
    ):
        svc, project_repo, job_repo, doc_repo, event_repo = service
        project = list(project_repo._store.values())[0]

        result = await svc.import_data(
            project_id=project.id,
            source_type=SourceType.TXT,
            content="Hello world",
        )

        assert result.event_count == 1
        assert result.job.status == ImportJobStatus.COMPLETED

    async def test_import_github_issue_creates_job_and_events(
        self, service
    ):
        svc, project_repo, job_repo, doc_repo, event_repo = service
        project = list(project_repo._store.values())[0]

        result = await svc.import_data(
            project_id=project.id,
            source_type=SourceType.GITHUB_ISSUE,
            content=GITHUB_ISSUE_SAMPLE.replace("\n", ""),
        )

        assert result.event_count == 3
        assert result.job.status == ImportJobStatus.COMPLETED

    async def test_import_github_pr_creates_job_and_events(
        self, service
    ):
        svc, project_repo, job_repo, doc_repo, event_repo = service
        project = list(project_repo._store.values())[0]

        result = await svc.import_data(
            project_id=project.id,
            source_type=SourceType.GITHUB_PR,
            content=GITHUB_PR_SAMPLE.replace("\n", ""),
        )

        assert result.event_count == 5  # 1 body + 1 comment + 1 review + 2 commits
        assert result.job.status == ImportJobStatus.COMPLETED

    async def test_get_nonexistent_project_raises(
        self, service
    ):
        svc, project_repo, job_repo, doc_repo, event_repo = service
        from app.shared.exceptions import NotFoundError

        with pytest.raises(NotFoundError):
            await svc.import_data(
                project_id=uuid4(),
                source_type=SourceType.MARKDOWN,
                content=MARKDOWN_SAMPLE,
            )

    async def test_get_job_after_creation(
        self, service
    ):
        svc, project_repo, job_repo, doc_repo, event_repo = service
        project = list(project_repo._store.values())[0]

        result = await svc.import_data(
            project_id=project.id,
            source_type=SourceType.MARKDOWN,
            content=MARKDOWN_SAMPLE,
        )

        job = await svc.get_job(result.job.id)
        assert job.id == result.job.id
        assert job.status == ImportJobStatus.COMPLETED

    async def test_list_jobs(
        self, service
    ):
        svc, project_repo, job_repo, doc_repo, event_repo = service
        project = list(project_repo._store.values())[0]

        await svc.import_data(
            project_id=project.id,
            source_type=SourceType.MARKDOWN,
            content=MARKDOWN_SAMPLE,
        )
        await svc.import_data(
            project_id=project.id,
            source_type=SourceType.TXT,
            content=TXT_SLACK_SAMPLE,
        )

        jobs = await svc.list_jobs(project_id=project.id)
        assert len(jobs) == 2


# Regression Tests for Timezone-Aware Timestamp Bug
class TestTimestampNaiveUTC:
    """Regression tests ensuring CommunicationEvent.timestamp is naive UTC before persistence.

    PostgreSQL TIMESTAMP WITHOUT TIME ZONE column cannot accept timezone-aware datetimes.
    All parsers must return naive datetime objects (tzinfo=None).
    """

    def test_txt_parser_timestamp_is_naive(self):
        parser = TXTParser()
        events = parser.parse(uuid4(), TXT_SLACK_SAMPLE)
        for event in events:
            assert event.timestamp.tzinfo is None, \
                f"TXT parser returned timezone-aware timestamp: {event.timestamp}"

    def test_txt_parser_fallback_timestamp_is_naive(self):
        parser = TXTParser()
        # Invalid timestamp format should fallback to utcnow()
        events = parser.parse(uuid4(), "Hello world")
        assert len(events) == 1
        assert events[0].timestamp.tzinfo is None, \
            "TXT parser fallback timestamp should be naive UTC"

    def test_markdown_parser_timestamp_is_naive(self):
        parser = MarkdownParser()
        events = parser.parse(uuid4(), MARKDOWN_SAMPLE)
        for event in events:
            assert event.timestamp.tzinfo is None, \
                f"Markdown parser returned timezone-aware timestamp: {event.timestamp}"

    def test_github_issue_parser_timestamp_is_naive(self):
        parser = GitHubIssueParser()
        events = parser.parse(uuid4(), GITHUB_ISSUE_SAMPLE.replace("\n", ""))
        for event in events:
            assert event.timestamp.tzinfo is None, \
                f"GitHub Issue parser returned timezone-aware timestamp: {event.timestamp}"

    def test_github_pr_parser_timestamp_is_naive(self):
        parser = GitHubPRParser()
        events = parser.parse(uuid4(), GITHUB_PR_SAMPLE.replace("\n", ""))
        for event in events:
            assert event.timestamp.tzinfo is None, \
                f"GitHub PR parser returned timezone-aware timestamp: {event.timestamp}"

    def test_txt_parser_parsed_timestamp_is_naive(self):
        """Test that parsed timestamps from strptime are naive."""
        parser = TXTParser()
        # Valid timestamp parsing
        events = parser.parse(uuid4(), "[2024-01-15 09:30:00] <@alice>\nHello")
        assert len(events) == 1
        assert events[0].timestamp.tzinfo is None, \
            "TXT parser parsed timestamp should be naive"
