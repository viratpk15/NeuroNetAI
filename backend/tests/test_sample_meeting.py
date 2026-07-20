"""Test extraction quality with the sample meeting from Sprint 22.1."""
import pytest
from datetime import datetime, timezone
from uuid import uuid4

from app.domain.entities import CommunicationEvent
from app.application.agents.conversation_agent import ConversationAgent
from app.application.agents.task_agent import TaskAgent
from app.application.agents.entity_agent import EntityAgent
from app.application.agents.sentiment_agent import SentimentAgent


# Sample meeting from Sprint 22.1 requirements
SAMPLE_MEETING_EVENTS = [
    CommunicationEvent(
        document_id=uuid4(),
        content="We need to migrate the backend to FastAPI by Friday.",
        timestamp=datetime.now(timezone.utc),
        source="slack_message",
        author="Alice",
    ),
    CommunicationEvent(
        document_id=uuid4(),
        content="I will finish authentication tomorrow.",
        timestamp=datetime.now(timezone.utc),
        source="slack_message",
        author="Bob",
    ),
    CommunicationEvent(
        document_id=uuid4(),
        content="JWT bug has been fixed.",
        timestamp=datetime.now(timezone.utc),
        source="slack_message",
        author="Charlie",
    ),
    CommunicationEvent(
        document_id=uuid4(),
        content="Use PostgreSQL for production.",
        timestamp=datetime.now(timezone.utc),
        source="slack_message",
        author="Decision",
    ),
    CommunicationEvent(
        document_id=uuid4(),
        content="Bob will deploy staging on Thursday.",
        timestamp=datetime.now(timezone.utc),
        source="slack_message",
        author="Task",
    ),
    CommunicationEvent(
        document_id=uuid4(),
        content="Authentication testing is still pending.",
        timestamp=datetime.now(timezone.utc),
        source="slack_message",
        author="Risk",
    ),
    CommunicationEvent(
        document_id=uuid4(),
        content="I will review deployment after QA.",
        timestamp=datetime.now(timezone.utc),
        source="slack_message",
        author="Sarah",
    ),
]


class TestSampleMeetingQuality:
    """Test extraction quality with sample meeting data."""

    async def test_summary_quality(self):
        """Summary should describe the meeting naturally."""
        agent = ConversationAgent()
        result = await agent.process(SAMPLE_MEETING_EVENTS)
        
        summary = result["conversation_summary"]
        # Should not contain "Unknown:"
        assert "Unknown:" not in summary
        # Should be concise (max 100 words)
        assert len(summary.split()) <= 100
        # Should contain key discussion points
        summary_lower = summary.lower()
        assert "fastapi" in summary_lower or "migration" in summary_lower or "backend" in summary_lower
        
        print(f"\nSummary: {summary}")

    async def test_tasks_have_assignees(self):
        """Tasks should have assignees extracted correctly."""
        agent = TaskAgent()
        result = await agent.process(SAMPLE_MEETING_EVENTS)
        
        tasks = result["tasks"]
        print(f"\nTasks found: {tasks}")
        
        # Should find multiple tasks
        assert len(tasks) >= 2
        
        # Check that Bob has tasks assigned
        bob_tasks = [t for t in tasks if t.get("assignee") and "bob" in t["assignee"].lower()]
        assert len(bob_tasks) >= 1, "Bob should have at least one task assigned"
        
        # Check due dates
        tasks_with_due = [t for t in tasks if t.get("due_date")]
        assert len(tasks_with_due) >= 1, "Should have tasks with due dates (tomorrow, Friday, Thursday)"
        
        # Verify specific expected tasks
        task_titles = [t["title"].lower() for t in tasks]
        assert any("authentication" in title for title in task_titles)
        assert any("deploy" in title and "staging" in title for title in task_titles)

    async def test_entities_categorized_correctly(self):
        """Entities should be categorized into proper types."""
        agent = EntityAgent()
        result = await agent.process(SAMPLE_MEETING_EVENTS)
        
        entities = result["entities"]
        print(f"\nEntities found: {entities}")
        
        # Get entities by type
        people = [e for e in entities if e["entity_type"] == "person"]
        frameworks = [e for e in entities if e["entity_type"] == "framework"]
        databases = [e for e in entities if e["entity_type"] == "database"]
        techs = [e for e in entities if e["entity_type"] == "technology"]
        concepts = [e for e in entities if e["entity_type"] == "concept"]
        
        # People should include Alice, Bob, Charlie, Sarah
        person_names = [p["name"].lower() for p in people]
        assert any("alice" in name for name in person_names), "Should extract Alice"
        assert any("bob" in name for name in person_names), "Should extract Bob"
        assert any("charlie" in name for name in person_names), "Should extract Charlie"
        assert any("sarah" in name for name in person_names), "Should extract Sarah"
        
        # Framework should include FastAPI
        framework_names = [f["name"].lower() for f in frameworks]
        assert any("fastapi" in name for name in framework_names), "Should extract FastAPI as framework"
        
        # Database should include PostgreSQL
        db_names = [d["name"].lower() for d in databases]
        assert any("postgresql" in name for name in db_names), "Should extract PostgreSQL as database"
        
        # Technology should include JWT
        tech_names = [t["name"].lower() for t in techs]
        assert any("jwt" in name for name in tech_names), "Should extract JWT as technology"
        
        # Concept should include authentication, deployment
        concept_names = [c["name"].lower() for c in concepts]
        # Authentication is mentioned multiple times

    async def test_decisions_correct(self):
        """Decisions should be actual engineering decisions, not action items."""
        agent = ConversationAgent()
        result = await agent.process(SAMPLE_MEETING_EVENTS)
        
        decisions = result["important_decisions"]
        print(f"\nDecisions found: {decisions}")
        
        # Should find the PostgreSQL decision
        assert any("postgresql" in d.lower() for d in decisions), "Should extract 'Use PostgreSQL for production'"
        
        # Should NOT include action items as decisions
        for decision in decisions:
            assert "will" not in decision.lower() or "use" in decision.lower(), \
                f"'{decision}' should not be an action item"

    async def test_risks_extracted(self):
        """Risks should be extracted correctly."""
        agent = ConversationAgent()
        result = await agent.process(SAMPLE_MEETING_EVENTS)
        
        risks = result["risks"]
        print(f"\nRisks found: {risks}")
        
        # Should find the authentication testing pending risk
        assert len(risks) >= 1, "Should extract at least one risk"
        risk_text = " ".join(risks).lower()
        assert "pending" in risk_text or "testing" in risk_text, "Should mention 'Authentication testing pending'"

    async def test_no_duplicate_entities(self):
        """Entities should not have duplicates."""
        agent = EntityAgent()
        result = await agent.process(SAMPLE_MEETING_EVENTS)
        
        entities = result["entities"]
        
        # Check for duplicates
        entity_keys = [(e["entity_type"], e["name"].lower()) for e in entities]
        assert len(entity_keys) == len(set(entity_keys)), f"Found duplicate entities: {entities}"

    async def test_sentiment_has_scores(self):
        """Sentiment should return numerical scores."""
        agent = SentimentAgent()
        result = await agent.process(SAMPLE_MEETING_EVENTS)
        
        print(f"\nSentiment result: {result}")
        
        assert "positivity_score" in result
        assert "stress_score" in result
        assert "confidence_score" in result
        assert 0.0 <= result["positivity_score"] <= 1.0
        assert 0.0 <= result["stress_score"] <= 1.0
        assert 0.0 <= result["confidence_score"] <= 1.0