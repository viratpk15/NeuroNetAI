"""Task Extraction Agent for identifying tasks from communication events."""
import logging
import re
from typing import Any

from app.domain.entities import CommunicationEvent
from app.application.agents.base import BaseAgent

logger = logging.getLogger(__name__)


class TaskAgent(BaseAgent):
    """Extracts tasks from communication events.
    
    This implementation uses deterministic rule-based analysis.
    When LLM providers are available, this can be replaced with LLM-powered analysis.
    """

    # Task-indicating patterns
    TASK_PATTERNS = [
        r"(?:TODO|TODO:|task:|need to|need to|should|will|going to|plan to|assign|take on|work on|implement|fix|create|build|design|review|test|deploy|setup|configure|add|remove|update|delete|investigate|look into|research|document|write|draft|finalize|complete|finish)[\s:]+(.{10,100})",
        r"@(\w+).*?(?:to|will|should)\s+(.{10,80})",
        r"(?:assigned? to|reassign|for)\s+@?(\w+)[\s:]+(.{10,80})",
    ]

    async def process(self, events: list[CommunicationEvent]) -> dict[str, Any]:
        """Process communication events to extract tasks.
        
        Args:
            events: List of communication events to analyze
            
        Returns:
            Dictionary with 'tasks' key containing list of task dictionaries
        """
        tasks = []
        seen_tasks = set()

        for event in events:
            for pattern in self.TASK_PATTERNS:
                matches = re.findall(pattern, event.content, re.IGNORECASE)
                for match in matches:
                    if isinstance(match, tuple) and len(match) == 2:
                        # Pattern with assignee
                        assignee = match[0] if match[0].startswith("@") else f"@{match[0]}"
                        title = match[1].strip()
                    else:
                        # Pattern without assignee
                        assignee = None
                        title = match.strip() if isinstance(match, str) else match[0].strip()

                    # Normalize title
                    title = re.sub(r'\s+', ' ', title).strip()
                    if len(title) < 5:
                        continue

                    # Create unique key for deduplication
                    task_key = title.lower()[:50]
                    if task_key not in seen_tasks:
                        seen_tasks.add(task_key)
                        tasks.append({
                            "title": title[:200],  # Limit title length
                            "description": f"From {event.author or 'unknown'}: {event.content[:100]}...",
                            "assignee": assignee,
                            "priority": self._infer_priority(event.content),
                            "status": "open",
                            "due_date": None,  # Would extract from content with LLM
                        })

        # Limit to reasonable number of tasks
        tasks = tasks[:20]

        logger.info(f"TaskAgent found {len(tasks)} tasks")

        return {"tasks": tasks}

    def _infer_priority(self, content: str) -> str:
        """Infer task priority from content keywords."""
        content_lower = content.lower()
        if any(kw in content_lower for kw in ["urgent", "critical", "asap", "priority", "high"]):
            return "high"
        elif any(kw in content_lower for kw in ["low", "nice to have", "optional"]):
            return "low"
        return "medium"