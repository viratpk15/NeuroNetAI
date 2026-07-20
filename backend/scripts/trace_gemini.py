#!/usr/bin/env python3
"""Instrumented trace script for Gemini execution end-to-end.

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
from app.infrastructure.ai_providers.factory import ProviderFactory
from app.infrastructure.ai_providers.base import AIProvider


def create_sample_events():
    """Create sample CommunicationEvent objects."""
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


async def trace_full_pipeline(events):
    """Trace the full analysis pipeline with detailed logging."""
    from app.shared.config import get_settings
    
    # Reset caches
    get_settings.cache_clear()
    ProviderFactory.reset()
    
    print("========================")
    print("ProviderFactory")
    print("========================")
    
    settings = get_settings()
    print(f"MODEL_PROVIDER config: {settings.model_provider}")
    print(f"GEMINI_API_KEY configured: {bool(settings.gemini_api_key)}")
    print(f"GEMINI_MODEL config: {settings.gemini_model}")
    
    provider = ProviderFactory.get_provider()
    
    print(f"\nSelected provider: {provider.__class__.__name__ if provider else None}")
    if provider:
        print(f"Selected model: {getattr(provider, 'model', 'unknown')}")
        print(f"Provider type: {type(provider).__name__}")
    
    if not provider:
        print("\nNo provider available - would use rule-based fallback only")
        return
    
    print("\n========================")
    print("ConversationAgent")
    print("========================")
    
    from app.prompts.prompt_builder import PromptBuilder
    prompt_builder = PromptBuilder()
    
    prompt = prompt_builder.build_conversation_prompt(events, "NeuroNet AI")
    print(f"Prompt (first 500 chars): {prompt[:500]}...")
    
    try:
        print("Provider.summarize_conversation() called? YES")
        raw_response = await provider.summarize_conversation(events, "NeuroNet AI")
        print(f"Raw response: {raw_response}")
        print(f"Parsed JSON: {raw_response}")
    except Exception as e:
        print(f"Provider.summarize_conversation() called? YES - EXCEPTION RAISED")
        print(f"EXCEPTION TYPE: {type(e).__name__}")
        print(f"EXCEPTION MESSAGE: {e}")
        traceback.print_exc()
    
    print("\n========================")
    print("TaskAgent")
    print("========================")
    
    prompt = prompt_builder.build_task_prompt(events, "NeuroNet AI")
    print(f"Prompt (first 500 chars): {prompt[:500]}...")
    
    try:
        print("Provider.extract_tasks() called? YES")
        raw_response = await provider.extract_tasks(events, "NeuroNet AI")
        print(f"Raw response: {raw_response}")
        print(f"Parsed tasks: {raw_response.get('tasks', [])}")
    except Exception as e:
        print(f"Provider.extract_tasks() called? YES - EXCEPTION RAISED")
        print(f"EXCEPTION TYPE: {type(e).__name__}")
        print(f"EXCEPTION MESSAGE: {e}")
        traceback.print_exc()
    
    print("\n========================")
    print("EntityAgent")
    print("========================")
    
    prompt = prompt_builder.build_entity_prompt(events, "NeuroNet AI")
    print(f"Prompt (first 500 chars): {prompt[:500]}...")
    
    try:
        print("Provider.extract_entities() called? YES")
        raw_response = await provider.extract_entities(events, "NeuroNet AI")
        print(f"Raw response: {raw_response}")
        print(f"Parsed entities: {raw_response.get('entities', [])}")
    except Exception as e:
        print(f"Provider.extract_entities() called? YES - EXCEPTION RAISED")
        print(f"EXCEPTION TYPE: {type(e).__name__}")
        print(f"EXCEPTION MESSAGE: {e}")
        traceback.print_exc()
    
    print("\n========================")
    print("SentimentAgent")
    print("========================")
    
    prompt = prompt_builder.build_sentiment_prompt(events, "NeuroNet AI")
    print(f"Prompt (first 500 chars): {prompt[:500]}...")
    
    try:
        print("Provider.analyze_sentiment() called? YES")
        raw_response = await provider.analyze_sentiment(events, "NeuroNet AI")
        print(f"Raw response: {raw_response}")
        print(f"Parsed sentiment: {raw_response}")
    except Exception as e:
        print(f"Provider.analyze_sentiment() called? YES - EXCEPTION RAISED")
        print(f"EXCEPTION TYPE: {type(e).__name__}")
        print(f"EXCEPTION MESSAGE: {e}")
        traceback.print_exc()
    
    print("\n========================")
    print("GeminiProvider Internal Trace")
    print("========================")
    
    # Now let's trace the internal _generate_content call
    if hasattr(provider, '_generate_content'):
        print("Provider has _generate_content method")
        try:
            print("_generate_content called...")
            response = await provider._generate_content(prompt)
            print(f"_generate_content returned: {response[:200] if response else 'empty'}")
        except Exception as e:
            print(f"_generate_content exception: {type(e).__name__}: {e}")
            traceback.print_exc()


async def main():
    """Main entry point."""
    events = create_sample_events()
    await trace_full_pipeline(events)


if __name__ == "__main__":
    asyncio.run(main())