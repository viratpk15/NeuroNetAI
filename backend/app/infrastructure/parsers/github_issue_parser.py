"""GitHub Issue importer for extracting communication events from GitHub issue JSON data."""
import json
from datetime import datetime, timezone
from uuid import UUID

from app.domain.entities import CommunicationEvent


class GitHubIssueParseError(Exception):
    """Raised when GitHub issue parsing fails."""
    pass


class GitHubIssueParser:
    """Parses GitHub issue JSON data.

    Expected JSON structure from GitHub API:
    {
      "id": 123,
      "number": 45,
      "title": "...",
      "body": "...",
      "user": {"login": "..."},
      "created_at": "2024-01-15T09:30:00Z",
      "comments": [
        {
          "id": 456,
          "user": {"login": "..."},
          "body": "...",
          "created_at": "2024-01-15T10:00:00Z"
        }
      ]
    }
    """

    def validate(self, content: str) -> bool:
        """Validate that content is valid GitHub issue JSON."""
        if not content or not content.strip():
            return False
        try:
            data = json.loads(content)
            return "id" in data or "number" in data
        except json.JSONDecodeError:
            return False

    def parse(self, document_id: UUID, content: str) -> list[CommunicationEvent]:
        """Parse GitHub issue JSON and extract communication events."""
        try:
            data = json.loads(content)
        except json.JSONDecodeError as e:
            raise GitHubIssueParseError(f"Invalid JSON: {e}") from e

        events: list[CommunicationEvent] = []

        # Parse the main issue body as an event
        issue_created = self._parse_timestamp(data.get("created_at", ""))
        author = data.get("user", {}).get("login")
        body = data.get("body", "")

        if body:
            events.append(CommunicationEvent(
                document_id=document_id,
                content=body,
                timestamp=issue_created,
                source="github_issue_body",
                author=author,
                metadata={"issue_number": data.get("number"), "issue_id": data.get("id")},
            ))

        # Parse comments as events
        comments = data.get("comments", [])
        if isinstance(comments, list):
            for comment in comments:
                comment_created = self._parse_timestamp(comment.get("created_at", ""))
                comment_author = comment.get("user", {}).get("login")
                comment_body = comment.get("body", "")

                if comment_body:
                    events.append(CommunicationEvent(
                        document_id=document_id,
                        content=comment_body,
                        timestamp=comment_created,
                        source="github_comment",
                        author=comment_author,
                        metadata={"comment_id": comment.get("id")},
                    ))

        return events

    def _parse_timestamp(self, ts: str) -> datetime:
        """Parse ISO 8601 timestamp from GitHub API."""
        if not ts:
            return datetime.now(timezone.utc)
        try:
            # Handle both Z suffix and +00:00 format
            ts = ts.replace("Z", "+00:00")
            return datetime.fromisoformat(ts.replace("+00:00", ""))
        except ValueError:
            return datetime.now(timezone.utc)
