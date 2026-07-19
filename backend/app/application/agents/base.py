"""Base agent class for AI Intelligence Engine."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from app.domain.entities import CommunicationEvent


class BaseAgent(ABC):
    """Abstract base class for all AI agents."""

    @abstractmethod
    async def process(self, events: list[CommunicationEvent]) -> dict[str, Any]:
        """Process communication events and return results.
        
        Args:
            events: List of communication events to analyze
            
        Returns:
            Dictionary with agent-specific outputs
        """
        ...