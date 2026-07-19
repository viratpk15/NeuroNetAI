"""Context builder for RAG retrieval results."""
import logging
from typing import Any

logger = logging.getLogger(__name__)


class RetrievedChunk:
    """A retrieved chunk with relevance score."""

    def __init__(
        self,
        content: str,
        metadata: dict[str, Any],
        score: float,
    ):
        self.content = content
        self.metadata = metadata
        self.score = score

    def to_dict(self) -> dict[str, Any]:
        return {
            "content": self.content,
            "metadata": self.metadata,
            "score": self.score,
        }


class ContextBuilder:
    """Builds token-safe context from retrieved chunks."""

    def __init__(self, max_tokens: int = 4000):
        self.max_tokens = max_tokens

    def build(self, chunks: list[RetrievedChunk]) -> str:
        """Build context string from chunks.

        Args:
            chunks: List of retrieved chunks

        Returns:
            Combined context string with source citations
        """
        # Remove duplicate content
        seen_content = set()
        unique_chunks = []
        for chunk in chunks:
            content_hash = hash(chunk.content[:100])
            if content_hash not in seen_content:
                seen_content.add(content_hash)
                unique_chunks.append(chunk)

        # Sort by score descending
        unique_chunks.sort(key=lambda c: c.score, reverse=True)

        # Build context within token limit
        context_parts = []
        total_length = 0

        for chunk in unique_chunks:
            chunk_text = chunk.content
            if total_length + len(chunk_text) > self.max_tokens * 4:  # Rough char/token ratio
                break
            context_parts.append(f"[Source: {chunk.metadata.get('source', 'unknown')}] {chunk_text}")
            total_length += len(chunk_text)

        return "\n\n".join(context_parts)