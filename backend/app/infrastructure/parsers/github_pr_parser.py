"""GitHub PR importer for extracting communication events from GitHub PR JSON data."""
import json
from datetime import datetime, timezone
from uuid import UUID

from app.domain.entities import CommunicationEvent


class GitHubPRParseError(Exception):
    """Raised when GitHub PR parsing fails."""
    pass


class GitHubPRParser:
    """Parses GitHub PR JSON data.

    Expected JSON structure from GitHub API:
    {
      "id": 123,
      "number": 45,
      "title": "...",
      "body": "...",
      "user": {"login": "..."},
      "created_at": "2024-01-15T09:30:00Z",
      "comments": [...],
      "review_comments": [...],
      "commits": [...]
    }
    """

    def validate(self, content: str) -> bool:
        """Validate that content is valid GitHub PR JSON."""
        if not content or not content.strip():
            return False
        try:
            data = json.loads(content)
            return "id" in data or "number" in data
        except json.JSONDecodeError:
            return False

    def parse(self, document_id: UUID, content: str) -> list[CommunicationEvent]:
        """Parse GitHub PR JSON and extract communication events."""
        try:
            data = json.loads(content)
        except json.JSONDecodeError as e:
            raise GitHubPRParseError(f"Invalid JSON: {e}") from e

        events: list[CommunicationEvent] = []

        # Parse the main PR body as an event
        pr_created = self._parse_timestamp(data.get("created_at", ""))
        author = data.get("user", {}).get("login")
        body = data.get("body", "")

        if body:
            events.append(CommunicationEvent(
                document_id=document_id,
                content=body,
                timestamp=pr_created,
                source="github_pr_body",
                author=author,
                metadata={"pr_number": data.get("number"), "pr_id": data.get("id")},
            ))

        # Parse regular comments
        self._parse_comments(data.get("comments", []), document_id, events)

        # Parse review comments
        self._parse_review_comments(data.get("review_comments", []), document_id, events)

        # Parse commit messages
        self._parse_commits(data.get("commits", []), document_id, events)

        return events

    def _parse_comments(self, comments: list, document_id: UUID, events: list[CommunicationEvent]) -> None:
        """Parse PR comments."""
        if not isinstance(comments, list):
            return
        for comment in comments:
            created = self._parse_timestamp(comment.get("created_at", ""))
            author = comment.get("user", {}).get("login")
            body = comment.get("body", "")
            if body:
                events.append(CommunicationEvent(
                    document_id=document_id,
                    content=body,
                    timestamp=created,
                    source="github_pr_comment",
                    author=author,
                    metadata={"comment_id": comment.get("id")},
                ))

    def _parse_review_comments(
        self, review_comments: list, document_id: UUID, events: list[CommunicationEvent]
    ) -> None:
        """Parse PR review comments."""
        if not isinstance(review_comments, list):
            return
        for comment in review_comments:
            created = self._parse_timestamp(comment.get("created_at", ""))
            author = comment.get("user", {}).get("login")
            body = comment.get("body", "")
            if body:
                events.append(CommunicationEvent(
                    document_id=document_id,
                    content=body,
                    timestamp=created,
                    source="github_pr_review_comment",
                    author=author,
                    metadata={"comment_id": comment.get("id"), "diff_hunk": comment.get("diff_hunk", "")[:100]},
                ))

    def _parse_commits(self, commits: list, document_id: UUID, events: list[CommunicationEvent]) -> None:
        """Parse PR commits."""
        if not isinstance(commits, list):
            return
        for commit in commits:
            commit_data = commit.get("commit", {}) if isinstance(commit, dict) else {}
            created = self._parse_timestamp(commit_data.get("author", {}).get("date", ""))
            author = commit_data.get("author", {}).get("name")
            message = commit_data.get("message", "")
            if message:
                # Split multiline commit messages, take first line
                first_line = message.split("\n")[0].strip()
                events.append(CommunicationEvent(
                    document_id=document_id,
                    content=first_line,
                    timestamp=created,
                    source="github_pr_commit",
                    author=author,
                    metadata={"commit_sha": commit.get("sha")},
                ))

    def _parse_timestamp(self, ts: str) -> datetime:
        """Parse ISO 8601 timestamp from GitHub API."""
        if not ts:
            return datetime.now(timezone.utc)
        try:
            ts = ts.replace("Z", "+00:00")
            return datetime.fromisoformat(ts.replace("+00:00", ""))
        except ValueError:
            return datetime.now(timezone.utc)
