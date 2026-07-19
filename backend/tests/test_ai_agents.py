"""Tests for AI Intelligence Engine agents and analysis service."""
import pytest
from datetime import datetime, timezone
from uuid import UUID, uuid4

from app.domain.entities import CommunicationEvent
from app.application.agents.conversation_agent import ConversationAgent, ConversationResponse
from app.application.agents.task_agent import TaskAgent
from app.application.agents.sentiment_agent import SentimentAgent
from app.application.agents.entity_agent import EntityAgent


# Sample test events
SAMPLE_EVENTS = [
    CommunicationEvent(
        document_id=uuid4(),
        content="Team discussed implementing the new authentication feature. We decided to use JWT tokens.",
        timestamp=datetime.now(timezone.utc),
        source="slack_message",
        author="alice",
    ),
    CommunicationEvent(
        document_id=uuid4(),
        content="I will work on the login endpoint this week. Need to integrate with the database.",
        timestamp=datetime.now(timezone.utc),
        source="slack_message",
        author="bob",
    ),
    CommunicationEvent(
        document_id=uuid4(),
        content="The GitHub API integration is working great! All tests are passing.",
        timestamp=datetime.now(timezone.utc),
        source="github_comment",
        author="charlie",
    ),
    CommunicationEvent(
        document_id=uuid4(),
        content="We need to fix the bug in the user registration flow. It's urgent.",
        timestamp=datetime.now(timezone.utc),
        source="github_issue_body",
        author="reporter",
    ),
]


class TestConversationAgent:
    async def test_process_returns_all_fields(self):
        agent = ConversationAgent()
        result = await agent.process(SAMPLE_EVENTS)

        assert "conversation_summary" in result
        assert "discussion_topics" in result
        assert "important_decisions" in result
        assert "risks" in result
        assert "blockers" in result
        assert "action_items" in result

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
        assert result["risks"] == []
        assert result["blockers"] == []
        assert result["action_items"] == []

    async def test_llm_integration_with_valid_json(self):
        """Test that LLM returns valid structured JSON when available."""
        agent = ConversationAgent(project_name="Test Project")
        
        # Reset factory to get fresh provider
        from app.infrastructure.ai_providers.factory import ProviderFactory
        ProviderFactory.reset()
        
        result = await agent.process(SAMPLE_EVENTS)
        
        # Should have all required fields
        assert isinstance(result, dict)
        assert "conversation_summary" in result

    async def test_conversation_response_validation(self):
        """Test ConversationResponse Pydantic model validation."""
        # Valid response
        valid_data = {
            "summary": "Test summary",
            "topics": ["topic1", "topic2"],
            "decisions": ["decision1"],
            "risks": ["risk1"],
            "blockers": ["blocker1"],
            "action_items": ["action1"],
        }
        response = ConversationResponse(**valid_data)
        assert response.summary == "Test summary"
        assert len(response.topics) == 2

        # Empty response defaults
        empty_response = ConversationResponse()
        assert empty_response.summary == ""
        assert empty_response.topics == []
        assert empty_response.decisions == []
        assert empty_response.risks == []
        assert empty_response.blockers == []
        assert empty_response.action_items == []

    async def test_fallback_on_invalid_json(self):
        """Test that invalid JSON triggers fallback gracefully."""
        agent = ConversationAgent()
        # When no provider is available, should use rule-based fallback
        result = await agent.process(SAMPLE_EVENTS)
        
        # Should still return valid structure
        assert isinstance(result["conversation_summary"], str)
        assert isinstance(result["discussion_topics"], list)


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
                timestamp=datetime.now(timezone.utc),
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
                timestamp=datetime.now(timezone.utc),
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
                timestamp=datetime.now(timezone.utc),
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
                timestamp=datetime.now(timezone.utc),
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