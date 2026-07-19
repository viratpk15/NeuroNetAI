"""Executive intelligence report service."""
from typing import Any

from pydantic import BaseModel, Field


class ReportSection(BaseModel):
    """A section of the executive report."""

    title: str
    content: str
    items: list[dict[str, Any]] = Field(default_factory=list)


class ExecutiveReport(BaseModel):
    """Complete executive report."""

    project_id: str
    project_name: str
    generated_at: str
    health_score: float = 0.0
    sections: list[ReportSection] = Field(default_factory=list)


class ExecutiveReportService:
    """Generates comprehensive AI executive reports."""

    def __init__(self):
        pass

    def generate_report(
        self,
        project_id: str,
        project_name: str,
        conversation_data: dict[str, Any],
        task_data: dict[str, Any],
        entity_data: dict[str, Any],
        sentiment_data: dict[str, Any],
    ) -> ExecutiveReport:
        """Generate executive report from AI outputs.

        Args:
            project_id: Project identifier
            project_name: Project name
            conversation_data: Output from ConversationAgent
            task_data: Output from TaskAgent
            entity_data: Output from EntityAgent
            sentiment_data: Output from SentimentAgent

        Returns:
            Complete ExecutiveReport
        """
        from datetime import datetime

        # Calculate health score
        health_score = self._calculate_health_score(task_data, sentiment_data)

        # Build sections
        sections = [
            self._build_executive_summary(conversation_data, task_data, sentiment_data),
            self._build_project_health(health_score),
            self._build_delivery_risk(sentiment_data),
            self._build_engineering_risks(sentiment_data),
            self._build_key_decisions(conversation_data),
            self._build_action_items(task_data),
            self._build_completed_tasks(task_data),
            self._build_contributors(entity_data),
            self._build_technology_stack(entity_data),
            self._build_important_entities(entity_data),
            self._build_timeline_summary(conversation_data),
            self._build_recommendations(sentiment_data, task_data),
        ]

        return ExecutiveReport(
            project_id=project_id,
            project_name=project_name,
            generated_at=datetime.now().isoformat(),
            health_score=health_score,
            sections=sections,
        )

    def _calculate_health_score(
        self,
        task_data: dict[str, Any],
        sentiment_data: dict[str, Any],
    ) -> float:
        """Calculate project health score 0-100."""
        tasks = task_data.get("tasks", [])
        completed = sum(1 for t in tasks if t.get("status") == "done")
        total = len(tasks) or 1

        delivery_risk = sentiment_data.get("delivery_risk", "low")
        risk_scores = {"low": 20, "medium": 40, "high": 60, "critical": 80}
        risk_penalty = risk_scores.get(delivery_risk, 20)

        # Base score on completion rate - risk penalty
        score = (completed / total) * 100 - risk_penalty
        return max(0, min(100, score))

    def _build_executive_summary(
        self,
        conversation: dict[str, Any],
        tasks: dict[str, Any],
        sentiment: dict[str, Any],
    ) -> ReportSection:
        """Build executive summary section."""
        risk = sentiment.get("delivery_risk", "unknown")
        morale = sentiment.get("team_morale", "medium")
        task_count = len(tasks.get("tasks", []))

        return ReportSection(
            title="Executive Summary",
            content=f"Project shows {risk} delivery risk with {morale} team morale. "
            f"Total of {task_count} tasks tracked.",
            items=[
                {"risk_level": risk},
                {"morale": morale},
                {"task_count": task_count},
            ],
        )

    def _build_project_health(self, health_score: float) -> ReportSection:
        """Build project health section."""
        status = "healthy" if health_score > 70 else "needs attention" if health_score > 40 else "at risk"
        return ReportSection(
            title="Project Health Score",
            content=f"Health Score: {health_score:.0f}/100 - Project is {status}",
            items=[{"score": health_score}],
        )

    def _build_delivery_risk(self, sentiment: dict[str, Any]) -> ReportSection:
        """Build delivery risk section."""
        risk = sentiment.get("delivery_risk", "low")
        timeline = sentiment.get("timeline_signals", [])
        return ReportSection(
            title="Delivery Risk",
            content=f"Current delivery risk level: {risk}",
            items=[{"risk": risk, "timeline_signals": timeline}],
        )

    def _build_engineering_risks(self, sentiment: dict[str, Any]) -> ReportSection:
        """Build engineering risks section."""
        burnout = sentiment.get("burnout_probability", 0)
        blockers = sentiment.get("blockers", [])
        conflicts = sentiment.get("conflicts", [])

        items = []
        if burnout > 0:
            items.append({"risk": "burnout", "probability": burnout})
        if blockers:
            for b in blockers:
                items.append({"risk": "blocker", "detail": b})
        if conflicts:
            for c in conflicts:
                items.append({"risk": "conflict", "detail": c})

        return ReportSection(
            title="Engineering Risks",
            content=f"Burnout probability: {burnout:.0%}",
            items=items,
        )

    def _build_key_decisions(self, conversation: dict[str, Any]) -> ReportSection:
        """Build key decisions section."""
        decisions = conversation.get("important_decisions", [])
        return ReportSection(
            title="Key Decisions",
            content=f"{len(decisions)} important decisions documented",
            items=[{"decision": d} for d in decisions],
        )

    def _build_action_items(self, tasks: dict[str, Any]) -> ReportSection:
        """Build open action items section."""
        open_tasks = [
            t
            for t in tasks.get("tasks", [])
            if t.get("status") in ("todo", "in_progress", "pending")
        ]
        return ReportSection(
            title="Open Action Items",
            content=f"{len(open_tasks)} open action items",
            items=open_tasks,
        )

    def _build_completed_tasks(self, tasks: dict[str, Any]) -> ReportSection:
        """Build completed tasks section."""
        done_tasks = [t for t in tasks.get("tasks", []) if t.get("status") == "done"]
        return ReportSection(
            title="Completed Tasks",
            content=f"{len(done_tasks)} tasks completed",
            items=done_tasks,
        )

    def _build_contributors(self, entities: dict[str, Any]) -> ReportSection:
        """Build contributors section."""
        people = [
            e
            for e in entities.get("entities", [])
            if e.get("entity_type") == "person"
        ]
        return ReportSection(
            title="Contributors",
            content=f"{len(people)} contributors identified",
            items=people,
        )

    def _build_technology_stack(self, entities: dict[str, Any]) -> ReportSection:
        """Build technology stack section."""
        tech_types = ["technology", "framework", "language", "library", "database"]
        tech = [
            e
            for e in entities.get("entities", [])
            if e.get("entity_type") in tech_types
        ]
        return ReportSection(
            title="Technology Stack",
            content=f"{len(tech)} technologies identified",
            items=tech,
        )

    def _build_important_entities(self, entities: dict[str, Any]) -> ReportSection:
        """Build important entities section."""
        important = entities.get("entities", [])[:10]
        return ReportSection(
            title="Important Entities",
            content=f"{len(important)} key entities extracted",
            items=important,
        )

    def _build_timeline_summary(self, conversation: dict[str, Any]) -> ReportSection:
        """Build timeline summary section."""
        topics = conversation.get("discussion_topics", [])
        return ReportSection(
            title="Timeline Summary",
            content=f"{len(topics)} discussion topics identified",
            items=[{"topic": t} for t in topics],
        )

    def _build_recommendations(
        self,
        sentiment: dict[str, Any],
        tasks: dict[str, Any],
    ) -> ReportSection:
        """Build recommendations section."""
        recommendations = []

        # Risk-based recommendations
        if sentiment.get("delivery_risk") in ("high", "critical"):
            recommendations.append("Prioritize unblocking critical issues")

        if sentiment.get("burnout_probability", 0) > 0.5:
            recommendations.append("Consider team capacity rebalancing")

        # Task-based recommendations
        pending = [t for t in tasks.get("tasks", []) if t.get("status") == "todo"]
        if len(pending) > 10:
            recommendations.append("Review backlog prioritization")

        return ReportSection(
            title="Recommendations",
            content=f"{len(recommendations)} actionable recommendations",
            items=[{"recommendation": r} for r in recommendations],
        )

    def to_markdown(self, report: ExecutiveReport) -> str:
        """Export report as markdown."""
        md = f"# Executive Report: {report.project_name}\n\n"
        md += f"**Health Score:** {report.health_score:.0f}/100\n\n"

        for section in report.sections:
            md += f"## {section.title}\n\n"
            md += f"{section.content}\n\n"
            if section.items:
                for item in section.items:
                    md += f"- {item}\n"
                md += "\n"

        return md