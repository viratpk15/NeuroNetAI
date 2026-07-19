"""Chat service for RAG-powered conversations."""
import logging
import time

from pydantic import BaseModel, Field

from app.application.services.retrieval_service import RetrievalService, RetrievedChunk
from app.prompts.prompt_builder import PromptBuilder
from app.infrastructure.ai_providers.factory import ProviderFactory

logger = logging.getLogger(__name__)


class ChatResponse(BaseModel):
    """Response model for chat service."""

    answer: str = Field(default="", description="Chat response")
    sources: list[dict[str, str]] = Field(default_factory=list, description="Source references")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Response confidence")
    retrieved_chunks: int = Field(default=0, description="Number of chunks retrieved")


class ChatService:
    """Project-aware AI chat service using RAG."""

    def __init__(self):
        self._retrieval_service = RetrievalService()
        self._prompt_builder = PromptBuilder()

    async def chat(
        self,
        query: str,
        project_id: str | None = None,
    ) -> ChatResponse:
        """Answer questions using project knowledge.

        Args:
            query: User question
            project_id: Optional project ID to scope retrieval

        Returns:
            ChatResponse with answer and sources
        """
        if not query.strip():
            return ChatResponse(answer="Please ask a question.")

        # Retrieve relevant context
        chunks = self._retrieval_service.retrieve(query, project_id)

        if not chunks:
            return ChatResponse(
                answer="I don't have that information in the project knowledge.",
                retrieved_chunks=0,
            )

        # Build context
        context = self._context_to_string(chunks)

        # Generate answer
        answer = await self._generate_answer(query, context)

        # Extract sources
        sources = [
            {
                "document_id": chunk.metadata.get("document_id", ""),
                "chunk_id": chunk.metadata.get("chunk_id", ""),
                "source": chunk.metadata.get("source", "unknown"),
            }
            for chunk in chunks
        ]

        # Calculate confidence based on retrieval scores
        avg_score = sum(c.score for c in chunks) / len(chunks) if chunks else 0.0
        confidence = min(avg_score * 2, 1.0)  # Normalize to 0-1

        logger.info(
            f"Chat completed - query: '{query[:50]}...', "
            f"chunks: {len(chunks)}, confidence: {confidence:.2f}",
        )

        return ChatResponse(
            answer=answer,
            sources=sources,
            confidence=confidence,
            retrieved_chunks=len(chunks),
        )

    def _context_to_string(self, chunks: list[RetrievedChunk]) -> str:
        """Convert retrieved chunks to context string."""
        return "\n\n".join(
            f"{chunk.content}"
            for chunk in sorted(chunks, key=lambda c: c.score, reverse=True)
        )

    async def _generate_answer(self, query: str, context: str) -> str:
        """Generate answer using AI provider."""
        provider = ProviderFactory.get_provider()
        if not provider:
            return "I'm unable to answer right now. Please try again later."

        start_time = time.time()
        prompt = self._prompt_builder._load_template("chat.md")
        prompt = prompt.replace("{context}", context).replace("{query}", query)

        try:
            response = await provider.chat(
                [{"role": "user", "content": prompt}],
            )
            latency_ms = int((time.time() - start_time) * 1000)

            logger.info(
                f"LLM chat response - provider: {provider.__class__.__name__}, "
                f"latency: {latency_ms}ms",
            )

            return response.get("response", "I couldn't generate an answer.")
        except Exception as e:
            logger.warning(f"LLM chat failed: {e}")
            return f"Error generating response: {e}"