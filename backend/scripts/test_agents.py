#!/usr/bin/env python3
"""Agent Diagnostic Script for testing all AI agents individually.

DO NOT modify the application.
DO NOT modify the agents.
DO NOT modify the provider.

Only create a standalone diagnostic script.
"""
import asyncio
import sys
import traceback
from datetime import datetime, timezone
from uuid import uuid4

# Add parent directory to path for imports
sys.path.insert(0, "/Users/virat/MyPersonalCloud/neuronet-phase1/backend")

from app.domain.entities import CommunicationEvent
from app.application.agents.conversation_agent import ConversationAgent
from app.application.agents.task_agent import TaskAgent
from app.application.agents.entity_agent import EntityAgent
from app.application.agents.sentiment_agent import SentimentAgent
from app.infrastructure.ai_providers.factory import ProviderFactory
from app.prompts.prompt_builder import PromptBuilder


def create_sample_events():
    """Create 5 realistic CommunicationEvent objects."""
    return [
        CommunicationEvent(
            document_id=uuid4(),
            content="Team discussed implementing the new authentication feature. We decided to use JWT tokens for the session management.",
            timestamp=datetime.now(timezone.utc),
            source="slack_message",
            author="alice",
            metadata={"channel": "engineering"},
        ),
        CommunicationEvent(
            document_id=uuid4(),
            content="I will work on the login endpoint this week. Need to integrate with the PostgreSQL database and make sure it's secure.",
            timestamp=datetime.now(timezone.utc),
            source="slack_message",
            author="bob",
            metadata={"channel": "engineering"},
        ),
        CommunicationEvent(
            document_id=uuid4(),
            content="The GitHub API integration is working great! All tests are passing. Thanks @charlie for the help with the FastAPI integration.",
            timestamp=datetime.now(timezone.utc),
            source="github_comment",
            author="diana",
            metadata={"issue_number": 42},
        ),
        CommunicationEvent(
            document_id=uuid4(),
            content="We need to fix the bug in the user registration flow. It's urgent and blocking the release. Can someone assign this to @eve?",
            timestamp=datetime.now(timezone.utc),
            source="github_issue_body",
            author="reporter",
            metadata={"labels": ["bug", "urgent"]},
        ),
        CommunicationEvent(
            document_id=uuid4(),
            content="Reminder: The sprint deadline is next Friday. We should review the roadmap and make sure all features are on track. The stress deadline pressure is building up.",
            timestamp=datetime.now(timezone.utc),
            source="markdown_message",
            author="product_manager",
            metadata={"document_type": "sprint_notes"},
        ),
    ]


async def test_conversation_agent(events, prompt_builder, provider):
    """Test ConversationAgent and print diagnostics."""
    print("=================================")
    print("ConversationAgent")
    print("=================================")

    # Print selected provider and model
    if provider:
        print(f"Selected Provider: {provider.__class__.__name__}")
        print(f"Selected Model: {getattr(provider, 'model', 'unknown')}")
    else:
        print("Selected Provider: None (fallback will be used)")

    agent = ConversationAgent(project_name="NeuroNet AI")

    try:
        # Build prompt for visibility
        prompt = prompt_builder.build_conversation_prompt(events, "NeuroNet AI")

        print("\n--- FULL PROMPT BEING SENT ---")
        print(prompt)
        print("--- END PROMPT ---\n")

        raw_response = None
        if provider:
            try:
                raw_response = await provider.summarize_conversation(events, "NeuroNet AI")
                print("Raw Ollama Response:")
                print(raw_response)
                print()
            except Exception as provider_error:
                print(f"Provider error (will use agent fallback): {provider_error}")
                traceback.print_exc()
                print()

        result = await agent.process(events)

        print("Raw Result:")
        print(result)
        print()
        print("Summary:")
        print(result.get("conversation_summary", ""))
        print()
        print("Topics:")
        for topic in result.get("discussion_topics", []):
            print(f"  - {topic}")
        print()
        print("Decisions:")
        for decision in result.get("important_decisions", []):
            print(f"  - {decision}")
        print()

    except Exception as e:
        print(f"Error in ConversationAgent: {e}")
        traceback.print_exc()

    print()


async def test_task_agent(events, prompt_builder, provider):
    """Test TaskAgent and print diagnostics."""
    print("=================================")
    print("TaskAgent")
    print("=================================")

    # Print selected provider and model
    if provider:
        print(f"Selected Provider: {provider.__class__.__name__}")
        print(f"Selected Model: {getattr(provider, 'model', 'unknown')}")
    else:
        print("Selected Provider: None (fallback will be used)")

    agent = TaskAgent(project_name="NeuroNet AI")

    try:
        # Build prompt for visibility
        prompt = prompt_builder.build_task_prompt(events, "NeuroNet AI")

        print("\n--- FULL PROMPT BEING SENT ---")
        print(prompt)
        print("--- END PROMPT ---\n")

        raw_response = None
        if provider:
            try:
                raw_response = await provider.extract_tasks(events, "NeuroNet AI")
                print("Raw Ollama Response:")
                print(raw_response)
                print()
            except Exception as provider_error:
                print(f"Provider error (will use agent fallback): {provider_error}")
                traceback.print_exc()
                print()

        result = await agent.process(events)

        print("Raw Result:")
        print(result)
        print()
        print("Tasks:")
        for task in result.get("tasks", []):
            print(f"  - {task.get('title', '')} (assignee: {task.get('assignee', 'unassigned')}, priority: {task.get('priority', 'medium')})")
        print()

    except Exception as e:
        print(f"Error in TaskAgent: {e}")
        traceback.print_exc()

    print()


async def test_entity_agent(events, prompt_builder, provider):
    """Test EntityAgent and print diagnostics."""
    print("=================================")
    print("EntityAgent")
    print("=================================")

    # Print selected provider and model
    if provider:
        print(f"Selected Provider: {provider.__class__.__name__}")
        print(f"Selected Model: {getattr(provider, 'model', 'unknown')}")
    else:
        print("Selected Provider: None (fallback will be used)")

    agent = EntityAgent(project_name="NeuroNet AI")

    try:
        # Build prompt for visibility
        prompt = prompt_builder.build_entity_prompt(events, "NeuroNet AI")

        print("\n--- FULL PROMPT BEING SENT ---")
        print(prompt)
        print("--- END PROMPT ---\n")

        raw_response = None
        if provider:
            try:
                raw_response = await provider.extract_entities(events, "NeuroNet AI")
                print("Raw Ollama Response:")
                print(raw_response)
                print()
            except Exception as provider_error:
                print(f"Provider error (will use agent fallback): {provider_error}")
                traceback.print_exc()
                print()

        result = await agent.process(events)

        print("Raw Result:")
        print(result)
        print()
        print("Entities:")
        for entity in result.get("entities", []):
            print(f"  - [{entity.get('entity_type', 'unknown')}] {entity.get('name', '')} (confidence: {entity.get('confidence', 0)})")
        print()

    except Exception as e:
        print(f"Error in EntityAgent: {e}")
        traceback.print_exc()

    print()


async def test_sentiment_agent(events, prompt_builder, provider):
    """Test SentimentAgent and print diagnostics."""
    print("=================================")
    print("SentimentAgent")
    print("=================================")

    # Print selected provider and model
    if provider:
        print(f"Selected Provider: {provider.__class__.__name__}")
        print(f"Selected Model: {getattr(provider, 'model', 'unknown')}")
    else:
        print("Selected Provider: None (fallback will be used)")

    agent = SentimentAgent(project_name="NeuroNet AI")

    try:
        # Build prompt for visibility
        prompt = prompt_builder.build_sentiment_prompt(events, "NeuroNet AI")

        print("\n--- FULL PROMPT BEING SENT ---")
        print(prompt)
        print("--- END PROMPT ---\n")

        raw_response = None
        if provider:
            try:
                raw_response = await provider.analyze_sentiment(events, "NeuroNet AI")
                print("Raw Ollama Response:")
                print(raw_response)
                print()
            except Exception as provider_error:
                print(f"Provider error (will use agent fallback): {provider_error}")
                traceback.print_exc()
                print()

        result = await agent.process(events)

        print("Raw Result:")
        print(result)
        print()
        print("Sentiment:")
        print(f"  Overall: {result.get('overall_sentiment', 'unknown')}")
        print(f"  Team Morale: {result.get('team_morale', 'unknown')}")
        print(f"  Delivery Risk: {result.get('delivery_risk', 'unknown')}")
        print(f"  Burnout Probability: {result.get('burnout_probability', 0)}")
        print()

    except Exception as e:
        print(f"Error in SentimentAgent: {e}")
        traceback.print_exc()

    print()


async def main():
    """Main entry point for the diagnostic script."""
    # Reset provider factory to get fresh instance
    ProviderFactory.reset()

    # Create sample events
    events = create_sample_events()

    # Initialize prompt builder
    prompt_builder = PromptBuilder()

    # Get provider (may be None if not configured)
    provider = ProviderFactory.get_provider()

    # Test each agent individually - exceptions are caught so script continues
    await test_conversation_agent(events, prompt_builder, provider)
    await test_task_agent(events, prompt_builder, provider)
    await test_entity_agent(events, prompt_builder, provider)
    await test_sentiment_agent(events, prompt_builder, provider)

    print("=================================")
    print("All agent tests completed")
    print("=================================")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Fatal error: {e}")
        traceback.print_exc()
        # Still exit with code 0 as per requirements
    sys.exit(0)