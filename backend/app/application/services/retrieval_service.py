"""Retrieval service for RAG foundation."""
import logging

from app.application.services.context_builder import ContextBuilder, RetrievedChunk
from app.application.services.embedding_service import EmbeddingService
from app.application.services.chunking_service import DocumentChunker
from app.infrastructure.vectorstore.chroma_store import ChromaVectorStore
from app.shared.config import get_settings

logger = logging.getLogger(__name__)


class RetrievalService:
    """Service for retrieving relevant document chunks."""

    def __init__(self, top_k: int | None = None, score_threshold: float = 0.0):
        settings = get_settings()
        self._embedding_service = EmbeddingService()
        self._vector_store = ChromaVectorStore()
        self._context_builder = ContextBuilder()
        self.top_k = top_k or settings.top_k
        self.score_threshold = score_threshold

    def retrieve(
        self,
        query: str,
        project_id: str | None = None,
    ) -> list[RetrievedChunk]:
        """Retrieve relevant chunks for a query.

        Args:
            query: Query text
            project_id: Optional project filter

        Returns:
            List of retrieved chunks with scores
        """
        # Generate query embedding
        embeddings = self._embedding_service.embed([query])
        query_embedding = embeddings[0] if embeddings else []

        # Query vector store
        results = self._vector_store.query(
            query_embedding=query_embedding,
            top_k=self.top_k,
            score_threshold=self.score_threshold,
            project_id=project_id,
        )

        # Convert to RetrievedChunk
        chunks = [
            RetrievedChunk(
                content=r["content"] or "",
                metadata=r["metadata"] or {},
                score=r["distance"] or 0.0,
            )
            for r in results
        ]

        logger.info(f"Retrieved {len(chunks)} chunks for query")
        return chunks

    def build_context(
        self,
        query: str,
        project_id: str | None = None,
    ) -> str:
        """Build context string for a query.

        Args:
            query: Query text
            project_id: Optional project filter

        Returns:
            Combined context string
        """
        chunks = self.retrieve(query, project_id)
        return self._context_builder.build(chunks)

    def index_document(
        self,
        content: str,
        document_id: str,
        project_id: str | None = None,
        source: str = "unknown",
    ) -> int:
        """Index a document for retrieval.

        Args:
            content: Document content
            document_id: Document ID
            project_id: Optional project ID
            source: Source type

        Returns:
            Number of chunks indexed
        """
        # Chunk document
        chunker = DocumentChunker()
        chunks = chunker.chunk_text(content, document_id, project_id, source)

        if not chunks:
            return 0

        # Get embeddings
        texts = [c[0] for c in chunks]
        embeddings = self._embedding_service.embed(texts)

        # Upsert to vector store
        ids = [m.chunk_id for _, m in chunks]
        documents = [c[0] for c in chunks]
        metadatas = [
            {
                "document_id": m.document_id,
                "project_id": m.project_id or "",
                "source": m.source,
                "chunk_index": m.chunk_index,
                "total_chunks": m.total_chunks,
            }
            for _, m in chunks
        ]

        self._vector_store.upsert(ids, embeddings, documents, metadatas)
        return len(chunks)