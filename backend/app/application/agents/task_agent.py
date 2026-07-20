"""Task Extraction Agent for identifying tasks from communication events."""
import logging
import re
import time
from typing import Any

from pydantic import BaseModel, Field

from app.domain.entities import CommunicationEvent
from app.application.agents.base import BaseAgent
from app.infrastructure.ai_providers.factory import ProviderFactory
from app.infrastructure.ai_providers.base import AIProvider
from app.prompts.prompt_builder import PromptBuilder

logger = logging.getLogger(__name__)


class TaskItem(BaseModel):
    """Pydantic model for a single extracted task."""

    title: str = Field(default="", description="Task title")
    description: str = Field(default="", description="Task description")
    assignee: str | None = Field(default=None, description="Task assignee")
    priority: str = Field(default="medium", description="Task priority")
    status: str = Field(default="todo", description="Task status")
    due_date: str | None = Field(default=None, description="Due date")
    dependencies: list[str] = Field(default_factory=list, description="Task dependencies")
    confidence: float = Field(default=0.5, ge=0.0, le=1.0, description="Extraction confidence")
    evidence: list[str] = Field(default_factory=list, description="Supporting evidence")


class TaskResponse(BaseModel):
    """Pydantic model for validated LLM task extraction response."""

    tasks: list[TaskItem] = Field(default_factory=list, description="List of extracted tasks")


class TaskAgent(BaseAgent):
    """Extracts tasks from communication events.

    Uses LLM provider (Ollama/Gemini) when available, falls back to rule-based analysis.
    """

    # Task-indicating patterns for rule-based fallback
    TASK_PATTERNS = [
        r"(?:TODO|TODO:|task:|need to|should|will|going to|plan to|assign|take on|work on|implement|fix|create|build|design|review|test|deploy|setup|configure|add|remove|update|delete|investigate|look into|research|document|write|draft|finalize|complete|finish)[\s:]+(.{10,100})",
        r"@(\w+).*?(?:to|will|should)\s+(.{10,80})",
        r"(?:assigned? to|reassign|for)\s+@?(\w+)[\s:]+(.{10,80})",
    ]

    def __init__(self, project_name: str | None = None):
        self._project_name = project_name
        self._prompt_builder = PromptBuilder()

    async def process(self, events: list[CommunicationEvent]) -> dict[str, Any]:
        """Process communication events to extract tasks.

        Uses LLM provider when available, falls back to rule-based analysis.

        Args:
            events: List of communication events to analyze

        Returns:
            Dictionary with 'tasks' key containing list of task dictionaries
        """
        if not events:
            return {"tasks": []}

        # Try LLM provider first
        provider = ProviderFactory.get_provider()
        if provider:
            try:
                result = await self._llm_process(events, provider)
                if result is not None:
                    return result
            except Exception as e:
                logger.warning(f"LLM provider failed, falling back to rule-based: {e}")

        # Fallback to rule-based analysis
        logger.info("Using rule-based fallback for TaskAgent")
        return self._rule_based_process(events)

    async def _llm_process(
        self,
        events: list[CommunicationEvent],
        provider: AIProvider,
    ) -> dict[str, Any] | None:
        """Process using LLM provider with logging.

        Args:
            events: Communication events to analyze
            provider: AI provider to use

        Returns:
            Structured response or None on failure
        """
        start_time = time.time()
        prompt = self._prompt_builder.build_task_prompt(events, self._project_name)

        logger.info(
            f"LLM request - provider: {provider.__class__.__name__}, "
            f"model: {getattr(provider, 'model', 'unknown')}, "
            f"prompt_size: {len(prompt)} chars",
        )

        response = await provider.extract_tasks(events, self._project_name)

        latency_ms = int((time.time() - start_time) * 1000)

        # Validate response with Pydantic
        try:
            validated = TaskResponse(**response)
            tasks = [task.model_dump() for task in validated.tasks]

            logger.info(
                f"LLM response - latency: {latency_ms}ms, "
                f"task_count: {len(tasks)}",
            )

            return {"tasks": tasks}
        except Exception as e:
            logger.warning(f"Failed to validate LLM response, falling back: {e}")
            return None

    def _rule_based_process(self, events: list[CommunicationEvent]) -> dict[str, Any]:
        """Rule-based analysis fallback.

        Args:
            events: List of communication events to analyze

        Returns:
            Dictionary with analysis results
        """
        tasks = []
        seen_tasks = set()

        for event in events:
            content = event.content
            author = event.author
            
            # Pattern 1: "I will X" or "I'll X" (author is the assignee)
            will_match = re.search(r"(?:i\s+will|i'll)\s+(.+?)(?:\s*(?:\.|,|;|$))", content, re.IGNORECASE)
            if will_match:
                task_text = will_match.group(1).strip()
                if len(task_text) >= 5:
                    due_date = self._extract_due_date(content)
                    task_key = task_text.lower()[:50]
                    if task_key not in seen_tasks:
                        seen_tasks.add(task_key)
                        tasks.append({
                            "title": task_text[:200],
                            "description": f"From {author or 'unknown'}: {content[:100]}...",
                            "assignee": author if author else None,
                            "priority": self._infer_priority(content),
                            "status": self._infer_status(content),
                            "due_date": due_date,
                            "dependencies": [],
                            "confidence": 0.7,
                            "evidence": [content[:150]],
                        })

            # Pattern 2: "@username will X"
            at_match = re.search(r"@(\w+)\s+(?:will|should|need to)\s+(.+?)(?:\s*(?:\.|,|;|$))", content, re.IGNORECASE)
            if at_match:
                assignee = at_match.group(1)
                task_text = at_match.group(2).strip()
                if len(task_text) >= 5:
                    due_date = self._extract_due_date(content)
                    task_key = f"{assignee}:{task_text.lower()[:40]}"
                    if task_key not in seen_tasks:
                        seen_tasks.add(task_key)
                        tasks.append({
                            "title": task_text[:200],
                            "description": f"Mentioned for @{assignee}: {content[:100]}...",
                            "assignee": assignee,
                            "priority": self._infer_priority(content),
                            "status": self._infer_status(content),
                            "due_date": due_date,
                            "dependencies": [],
                            "confidence": 0.7,
                            "evidence": [content[:150]],
                        })

            # Pattern 3: "Name will X" (third-party assignment, e.g., "Bob will deploy staging")
            # Match when author is "Task" or similar and content has "Name will action"
            if author and author.lower() in ["task", "tasks"]:
                name_will_match = re.search(r"(\w+)\s+will\s+(.+?)(?:\s*(?:\.|,|;|$))", content, re.IGNORECASE)
                if name_will_match:
                    assignee = name_will_match.group(1)
                    task_text = name_will_match.group(2).strip()
                    if len(task_text) >= 5:
                        due_date = self._extract_due_date(content)
                        task_key = f"{assignee}:{task_text.lower()[:40]}"
                        if task_key not in seen_tasks:
                            seen_tasks.add(task_key)
                            tasks.append({
                                "title": task_text[:200],
                                "description": f"Task mentioned: {content[:100]}...",
                                "assignee": assignee,
                                "priority": self._infer_priority(content),
                                "status": self._infer_status(content),
                                "due_date": due_date,
                                "dependencies": [],
                                "confidence": 0.7,
                                "evidence": [content[:150]],
                            })

            # Pattern 4: "Task: X" or "TODO: X"
            task_label_match = re.search(r"(?:task|todo)[:\s]+(.+?)(?:\s*(?:\.|,|;|$))", content, re.IGNORECASE)
            if task_label_match:
                task_text = task_label_match.group(1).strip()
                if len(task_text) >= 5:
                    due_date = self._extract_due_date(content)
                    task_key = task_text.lower()[:50]
                    if task_key not in seen_tasks:
                        seen_tasks.add(task_key)
                        tasks.append({
                            "title": task_text[:200],
                            "description": content[:150],
                            "assignee": author if author else None,
                            "priority": self._infer_priority(content),
                            "status": self._infer_status(content),
                            "due_date": due_date,
                            "dependencies": [],
                            "confidence": 0.7,
                            "evidence": [content[:150]],
                        })

        # Limit to reasonable number of tasks
        tasks = tasks[:20]

        logger.info(f"TaskAgent rule-based found {len(tasks)} tasks")

        return {"tasks": tasks}

    def _infer_priority(self, content: str) -> str:
        """Infer task priority from content keywords."""
        content_lower = content.lower()
        if "critical" in content_lower or "asap" in content_lower:
            return "critical"
        elif any(kw in content_lower for kw in ["urgent", "priority", "high"]):
            return "high"
        elif any(kw in content_lower for kw in ["low", "nice to have", "optional"]):
            return "low"
        return "medium"

    def _infer_status(self, content: str) -> str:
        """Infer task status from content keywords."""
        content_lower = content.lower()
        if any(kw in content_lower for kw in ["done", "completed", "finished", "closed"]):
            return "done"
        elif any(kw in content_lower for kw in ["blocked", "blocked on", "waiting", "stuck"]):
            return "blocked"
        elif any(kw in content_lower for kw in ["in progress", "working on", "started"]):
            return "in_progress"
        return "todo"

    def _extract_due_date(self, content: str) -> str | None:
        """Extract due date from content.

        Looks for relative dates (tomorrow, Friday) and absolute dates (2024-01-15).
        """
        content_lower = content.lower()
        
        # Relative dates
        if "tomorrow" in content_lower:
            return "tomorrow"
        elif "today" in content_lower:
            return "today"
        
        # Day of week patterns
        days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        for day in days:
            if day in content_lower:
                return day.title()
        
        # "next week" pattern
        if "next week" in content_lower:
            return "next week"
        
        # Absolute date pattern (YYYY-MM-DD)
        date_match = re.search(r"\b(\d{4}-\d{2}-\d{2})\b", content)
        if date_match:
            return date_match.group(1)
        
        # "by Friday" or "on Thursday" patterns
        by_date_match = re.search(r"\b(?:by|on|for)\s+(?:next\s+)?(monday|tuesday|wednesday|thursday|friday|saturday|sunday|\d{4}-\d{2}-\d{2})\b", content_lower)
        if by_date_match:
            date_str = by_date_match.group(1)
            if len(date_str) == 10:  # Absolute date
                return date_str
            return date_str.title()
        
        return None
