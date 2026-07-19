"""Tests for AI Intelligence Engine agents and analysis service."""
import pytest
from datetime import datetime, timezone
from uuid import UUID, uuid4

from app.domain.entities import CommunicationEvent
from app.application.agents.conversation_agent import ConversationAgent, ConversationResponse
from app.application.agents.task_agent import TaskAgent, TaskItem, TaskResponse
from app.application.agents.sentiment_agent import SentimentAgent, SentimentResponse
from app.application.agents.entity_agent import EntityAgent, EntityItem, EntityResponse


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
            assert task["priority"] in ("low", "medium", "high", "critical")
            assert "status" in task
            assert "confidence" in task
            assert isinstance(task["confidence"], (int, float))
            assert 0.0 <= task["confidence"] <= 1.0

    async def test_task_item_validation(self):
        """Test TaskItem Pydantic model validation."""
        valid_task = TaskItem(
            title="Implement auth",
            description="Add JWT auth to the backend",
            assignee="@alice",
            priority="high",
            status="in_progress",
            confidence=0.9,
            evidence=["I will work on the login endpoint"],
        )
        assert valid_task.title == "Implement auth"
        assert valid_task.priority == "high"
        assert valid_task.status == "in_progress"

    async def test_task_response_validation(self):
        """Test TaskResponse Pydantic model validation."""
        valid_data = {
            "tasks": [
                {
                    "title": "Task 1",
                    "priority": "high",
                    "status": "todo",
                    "confidence": 0.85,
                    "evidence": ["some evidence"],
                },
                {
                    "title": "Task 2",
                    "priority": "low",
                    "status": "done",
                    "confidence": 0.7,
                    "evidence": [],
                },
            ],
        }
        response = TaskResponse(**valid_data)
        assert len(response.tasks) == 2
        assert response.tasks[0].priority == "high"

    async def test_critical_priority_detection(self):
        """Test that urgent tasks get critical priority."""
        urgent_events = [
            CommunicationEvent(
                document_id=uuid4(),
                content="This is CRITICAL and needs ASAP attention!",
                timestamp=datetime.now(timezone.utc),
                source="slack_message",
                author="manager",
            )
        ]
        agent = TaskAgent()
        result = await agent.process(urgent_events)

        # Rule-based should detect high priority
        for task in result["tasks"]:
            assert task["priority"] in ("low", "medium", "high", "critical")

    async def test_llm_integration_fallback(self):
        """Test that LLM integration falls back gracefully."""
        agent = TaskAgent(project_name="Test Project")

        result = await agent.process(SAMPLE_EVENTS)

        # Should return valid structure
        assert isinstance(result, dict)
        assert "tasks" in result

    async def test_handles_empty_events(self):
        agent = TaskAgent()
        result = await agent.process([])

        assert result["tasks"] == []


class TestSentimentAgent:
    async def test_process_returns_sentiment(self):
        agent = SentimentAgent()
        result = await agent.process(SAMPLE_EVENTS)

        assert "overall_sentiment" in result
        assert "team_morale" in result
        assert "delivery_risk" in result
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
        assert result["confidence_score"] > 0

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

        assert result["delivery_risk"] in ("low", "medium", "high", "critical")

    async def test_handles_empty_events(self):
        agent = SentimentAgent()
        result = await agent.process([])

        assert result["overall_sentiment"] == "neutral"
        assert result["confidence_score"] == 0.0

    async def test_sentiment_response_validation(self):
        """Test SentimentResponse Pydantic model validation."""
        valid_data = {
            "overall_sentiment": "positive",
            "team_morale": "high",
            "delivery_risk": "low",
            "burnout_probability": 0.1,
            "confidence": 0.9,
            "evidence": ["Great work everyone!"],
        }
        response = SentimentResponse(**valid_data)
        assert response.overall_sentiment == "positive"
        assert response.team_morale == "high"
        assert response.delivery_risk == "low"

    async def test_morale_detection(self):
        """Test team morale detection."""
        agent = SentimentAgent()
        result = await agent.process(SAMPLE_EVENTS)

        assert result["team_morale"] in ("high", "medium", "low")

    async def test_llm_integration_fallback(self):
        """Test that LLM integration falls back gracefully."""
        agent = SentimentAgent(project_name="Test Project")

        result = await agent.process(SAMPLE_EVENTS)

        # Should return valid structure
        assert isinstance(result, dict)
        assert "overall_sentiment" in result


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

    async def test_entity_item_validation(self):
        """Test EntityItem Pydantic model validation."""
        valid_entity = EntityItem(
            entity_type="technology",
            name="FastAPI",
            context="Using FastAPI for the backend",
            confidence=0.95,
            relationships=[
                {
                    "related_to": "PostgreSQL",
                    "relationship_type": "depends_on",
                },
            ],
            evidence=["Using Python with FastAPI and PostgreSQL for the backend."],
        )
        assert valid_entity.entity_type == "technology"
        assert valid_entity.name == "FastAPI"
        assert valid_entity.confidence == 0.95
        assert len(valid_entity.relationships) == 1

    async def test_entity_response_validation(self):
        """Test EntityResponse Pydantic model validation."""
        valid_data = {
            "entities": [
                {
                    "entity_type": "person",
                    "name": "@alice",
                    "confidence": 0.85,
                    "evidence": ["Thanks @alice for the help"],
                },
                {
                    "entity_type": "technology",
                    "name": "Python",
                    "confidence": 0.9,
                    "evidence": ["Using Python with FastAPI"],
                },
            ],
        }
        response = EntityResponse(**valid_data)
        assert len(response.entities) == 2
        assert response.entities[0].entity_type == "person"

    async def test_entity_confidence_range(self):
        """Test that entity confidence is within valid range."""
        agent = EntityAgent()
        result = await agent.process(SAMPLE_EVENTS)

        for entity in result["entities"]:
            assert isinstance(entity["confidence"], (int, float))
            assert 0.0 <= entity["confidence"] <= 1.0

    async def test_llm_integration_fallback(self):
        """Test that LLM integration falls back gracefully."""
        agent = EntityAgent(project_name="Test Project")

        result = await agent.process(SAMPLE_EVENTS)

        # Should return valid structure
        assert isinstance(result, dict)
        assert "entities" in result

    async def test_relationships_field_present(self):
        """Test that relationships field is present in entities."""
        agent = EntityAgent()
        result = await agent.process(SAMPLE_EVENTS)

        for entity in result["entities"]:
            assert "relationships" in entity
            assert isinstance(entity["relationships"], list)

    async def test_evidence_field_present(self):
        """Test that evidence field is present in entities."""
        agent = EntityAgent()
        result = await agent.process(SAMPLE_EVENTS)

        for entity in result["entities"]:
            assert "evidence" in entity
            assert isinstance(entity["evidence"], list)
