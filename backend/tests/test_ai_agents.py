"""Tests for AI Intelligence Engine agents and analysis service."""
import pytest
from uuid import UUID, uuid4

from app.domain.entities import CommunicationEvent
from app.application.agents.conversation_agent import ConversationAgent
from app.application.agents.task_agent import TaskAgent
from app.application.agents.sentiment_agent import SentimentAgent
from app.application.agents.entity_agent import EntityAgent


# Sample test events
SAMPLE_EVENTS = [
    CommunicationEvent(
        document_id=uuid4(),
        content="Team discussed implementing the new authentication feature. We decided to use JWT tokens.",
        timestamp=None,
        source="slack_message",
        author="alice",
    ),
    CommunicationEvent(
        document_id=uuid4(),
        content="I will work on the login endpoint this week. Need to integrate with the database.",
        timestamp=None,
        source="slack_message",
        author="bob",
    ),
    CommunicationEvent(
        document_id=uuid4(),
        content="The GitHub API integration is working great! All tests are passing.",
        timestamp=None,
        source="github_comment",
        author="charlie",
    ),
    CommunicationEvent(
        document_id=uuid4(),
        content="We need to fix the bug in the user registration flow. It's urgent.",
        timestamp=None,
        source="github_issue_body",
        author="reporter",
    ),
]


class TestConversationAgent:
    async def test_process_returns_summary_and_topics(self):
        agent = ConversationAgent()
        result = await agent.process(SAMPLE_EVENTS)

        assert "conversation_summary" in result
        assert "discussion_topics" in result
        assert "important_decisions" in result

    async def test_extracts_topics(self):
        agent = ConversationAgent()
        result = await agent.process(SAMPLE_EVENTS)

        topics = result["discussion_topics"]
        assert isinstance(topics, list)
        assert len(topics) > 0

    async def test_extracts_decisions(self):
        agent = ConversationAgent()
        result = await agent.process(SAMPLE_EVENTS)

        decisions = result["important_decisions"]
        assert isinstance(decisions, list)

    async def test_handles_empty_events(self):
        agent = ConversationAgent()
        result = await agent.process([])

        assert result["conversation_summary"] == ""
        assert result["discussion_topics"] == []
        assert result["important_decisions"] == []


class TestTaskAgent:
    async def test_process_returns_tasks(self):
        agent = TaskAgent()
        result = await agent.process(SAMPLE_EVENTS)

        assert "tasks" in result
        assert isinstance(result["tasks"], list)

    async def test_extracts_task_from_actionable_content(self):
        agent = TaskAgent()
        result = await agent.process(SAMPLE_EVENTS)

        tasks = result["tasks"]
        assert len(tasks) >= 1

        # Check task structure
        for task in tasks:
            assert "title" in task
            assert "description" in task
            assert "priority" in task
            assert task["priority"] in ("low", "medium", "high")

    async def test_handles_empty_events(self):
        agent = TaskAgent()
        result = await agent.process([])

        assert result["tasks"] == []


class TestSentimentAgent:
    async def test_process_returns_sentiment(self):
        agent = SentimentAgent()
        result = await agent.process(SAMPLE_EVENTS)

        assert "overall_sentiment" in result
        assert "positivity_score" in result
        assert "stress_score" in result
        assert "confidence_score" in result

    async def test_detects_positive_sentiment(self):
        positive_events = [
            CommunicationEvent(
                document_id=uuid4(),
                content="Great work everyone! Everything is working perfectly.",
                timestamp=None,
                source="slack_message",
                author="manager",
            )
        ]
        agent = SentimentAgent()
        result = await agent.process(positive_events)

        assert result["overall_sentiment"] == "positive"
        assert result["positivity_score"] > 0

    async def test_detects_stress_indicators(self):
        stress_events = [
            CommunicationEvent(
                document_id=uuid4(),
                content="This is urgent! We're behind schedule and need overtime.",
                timestamp=None,
                source="slack_message",
                author="manager",
            )
        ]
        agent = SentimentAgent()
        result = await agent.process(stress_events)

        assert result["stress_score"] > 0

    async def test_handles_empty_events(self):
        agent = SentimentAgent()
        result = await agent.process([])

        assert result["overall_sentiment"] == "neutral"
        assert result["positivity_score"] == 0.0


class TestEntityAgent:
    async def test_process_returns_entities(self):
        agent = EntityAgent()
        result = await agent.process(SAMPLE_EVENTS)

        assert "entities" in result
        assert isinstance(result["entities"], list)

    async def test_extracts_person_mentions(self):
        entities_events = [
            CommunicationEvent(
                document_id=uuid4(),
                content="Thanks @alice and @bob for the help with the FastAPI integration.",
                timestamp=None,
                source="slack_message",
                author="charlie",
            )
        ]
        agent = EntityAgent()
        result = await agent.process(entities_events)

        entities = result["entities"]
        person_entities = [e for e in entities if e["entity_type"] == "person"]
        assert len(person_entities) >= 2

    async def test_extracts_technology_mentions(self):
        tech_events = [
            CommunicationEvent(
                document_id=uuid4(),
                content="Using Python with FastAPI and PostgreSQL for the backend.",
                timestamp=None,
                source="markdown_message",
                author="dev",
            )
        ]
        agent = EntityAgent()
        result = await agent.process(tech_events)

        entities = result["entities"]
        tech_entities = [e for e in entities if e["entity_type"] == "technology"]
        assert len(tech_entities) >= 1

    async def test_handles_empty_events(self):
        agent = EntityAgent()
        result = await agent.process([])

        assert result["entities"] == []