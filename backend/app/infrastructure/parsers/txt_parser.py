"""TXT parser for extracting communication events from plain text chat logs."""
import re
from datetime import datetime
from uuid import UUID

from app.domain.entities import CommunicationEvent


class TXTParseError(Exception):
    """Raised when txt parsing fails."""
    pass


class TXTParser:
    """Parses plain text files with chat/message format.

    Expected format (Slack-like):
    ```
    [2024-01-15 09:30:00] <@alice>
    Hello team, how's the progress?

    [2024-01-15 09:35:00] <@bob>
    Making good progress on the frontend.
    ```

    Or simple format:
    ```
    2024-01-15 09:30 alice:
    Hello team
    ```

    Or plain text (any non-empty content):
    ```
    Hello world
    ```
    """

    # Pattern for timestamp and author in brackets: [YYYY-MM-DD HH:MM:SS] <@author>
    SLACK_PATTERN = re.compile(r"^\[(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\]\s*<@([^>]+)>\s*$")

    # Pattern for simple format: YYYY-MM-DD HH:MM author:
    SIMPLE_PATTERN = re.compile(r"^(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2})[:\s]+([^:]+):\s*$")

    def validate(self, content: str) -> bool:
        """Validate that content has meaningful text content.

        Accepts:
        - Slack-style formatted messages with timestamps and authors
        - Simple formatted messages with timestamps and authors
        - Plain text content (any non-empty, non-whitespace-only text)

        Rejects:
        - Empty strings
        - Whitespace-only strings
        """
        stripped = content.strip() if content else ""
        if not stripped:
            return False

        lines = stripped.split("\n")
        # Check if any line matches structured format
        has_structured = any(self.SLACK_PATTERN.match(line) or self.SIMPLE_PATTERN.match(line) for line in lines)
        # Accept if we have structured format OR any content with actual text
        return has_structured or bool(stripped)

    def parse(self, document_id: UUID, content: str) -> list[CommunicationEvent]:
        """Parse txt content and extract communication events."""
        if not self.validate(content):
            raise TXTParseError("Invalid txt format: no message headers found")

        events: list[CommunicationEvent] = []
        lines = content.strip().split("\n")

        current_author: str | None = None
        current_timestamp: datetime | None = None
        current_message_lines: list[str] = []

        for line in lines:
            slack_match = self.SLACK_PATTERN.match(line)
            simple_match = self.SIMPLE_PATTERN.match(line) if not slack_match else None

            match = slack_match or simple_match
            if match:
                # Save previous message if exists
                if current_timestamp and current_message_lines:
                    event = self._create_event(document_id, current_timestamp, current_author, current_message_lines)
                    events.append(event)

                # Start new message
                timestamp_str = match.group(1)
                current_author = match.group(2).strip()
                try:
                    fmt = "%Y-%m-%d %H:%M:%S" if slack_match else "%Y-%m-%d %H:%M"
                    current_timestamp = datetime.strptime(timestamp_str, fmt)
                except ValueError:
                    current_timestamp = datetime.utcnow()
                current_message_lines = []
            elif current_timestamp is not None:
                if line.strip():
                    current_message_lines.append(line)

        # Save last message
        if current_timestamp and current_message_lines:
            event = self._create_event(document_id, current_timestamp, current_author, current_message_lines)
            events.append(event)

        # If no structured messages were found, treat entire content as one event
        if not events and content.strip():
            event = self._create_event(document_id, datetime.utcnow(), None, [content.strip()])
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
            source="txt_message",
            author=author,
        )