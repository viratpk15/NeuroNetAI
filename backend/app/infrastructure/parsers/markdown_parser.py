"""Markdown parser for extracting communication events from markdown chat logs."""
import re
from datetime import datetime, timezone
from uuid import UUID

from app.domain.entities import CommunicationEvent


class MarkdownParseError(Exception):
    """Raised when markdown parsing fails."""
    pass


class MarkdownParser:
    """Parses markdown files with chat/message format.

    Expected format:
    ```
    ## 2024-01-15 09:30 - @alice

    Hello team, how's the progress?

    ## 2024-01-15 09:35 - @bob

    Making good progress on the frontend.
    ```
    """

    # Pattern to match message headers: ## YYYY-MM-DD HH:MM - @author
    MESSAGE_HEADER_PATTERN = re.compile(r"^##\s+(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2})(?:\s*-\s*@(.+))?\s*$")

    def validate(self, content: str) -> bool:
        """Validate that content looks like a markdown chat log."""
        if not content or not content.strip():
            return False
        # Check for at least one message header pattern
        lines = content.strip().split("\n")
        return any(self.MESSAGE_HEADER_PATTERN.match(line) for line in lines)

    def parse(self, document_id: UUID, content: str) -> list[CommunicationEvent]:
        """Parse markdown content and extract communication events."""
        if not self.validate(content):
            raise MarkdownParseError("Invalid markdown format: no message headers found")

        events: list[CommunicationEvent] = []
        lines = content.strip().split("\n")

        current_author: str | None = None
        current_timestamp: datetime | None = None
        current_message_lines: list[str] = []

        for line in lines:
            match = self.MESSAGE_HEADER_PATTERN.match(line)
            if match:
                # Save previous message if exists
                if current_timestamp and current_message_lines:
                    event = self._create_event(document_id, current_timestamp, current_author, current_message_lines)
                    events.append(event)

                # Start new message
                timestamp_str = match.group(1)
                current_author = match.group(2)
                try:
                    current_timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M")
                except ValueError:
                    current_timestamp = datetime.utcnow()
                current_message_lines = []
            elif current_timestamp is not None:
                # Accumulate message content
                if line.strip():
                    current_message_lines.append(line)

        # Save last message
        if current_timestamp and current_message_lines:
            event = self._create_event(document_id, current_timestamp, current_author, current_message_lines)
            events.append(event)

        return events

    def _create_event(
        self,
        document_id: UUID,
        timestamp: datetime,
        author: str | None,
        message_lines: list[str],
    ) -> CommunicationEvent:
        content = "\n".join(message_lines).strip()
        return CommunicationEvent(
            document_id=document_id,
            content=content,
            timestamp=timestamp,
            source="markdown_message",
            author=author.strip() if author else None,
        )