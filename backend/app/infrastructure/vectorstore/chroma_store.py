"""ChromaDB vector store implementation for RAG."""
import logging
from typing import Any

from app.shared.config import get_settings

logger = logging.getLogger(__name__)


class ChromaVectorStore:
    """ChromaDB vector store for document embeddings."""

    def __init__(self, persist_path: str | None = None):
        settings = get_settings()
        self.persist_path = persist_path or settings.chroma_db_path
        self._client = None
        self._collection = None

    def _get_client(self):
        """Get or create ChromaDB client."""
        import chromadb

        if self._client is None:
            self._client = chromadb.PersistentClient(path=self.persist_path)
        return self._client

    def _get_collection(self):
        """Get or create collection."""
        if self._collection is None:
            client = self._get_client()
            self._collection = client.get_or_create_collection(
                name="neuronet_documents",
                metadata={"hnsw:space": "cosine"},
            )
        return self._collection

    def upsert(
        self,
        ids: list[str],
        embeddings: list[list[float]],
        documents: list[str],
        metadatas: list[dict[str, Any]],
    ) -> None:
        """Upsert document chunks with embeddings.

        Args:
            ids: Chunk IDs
            embeddings: Embedding vectors
            documents: Chunk text content
            metadatas: Metadata for each chunk
        """
        collection = self._get_collection()
        collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
        )
        logger.info(f"Upserted {len(ids)} chunks to vector store")

    def query(
        self,
        query_embedding: list[float],
        top_k: int | None = None,
        score_threshold: float = 0.0,
        project_id: str | None = None,
    ) -> list[dict[str, Any]]:
        """Query for similar chunks.

        Args:
            query_embedding: Query vector
            top_k: Number of results to return
            score_threshold: Minimum similarity score
            project_id: Optional project filter

        Returns:
            List of matched chunks with metadata
        """
        settings = get_settings()
        collection = self._get_collection()
        k = top_k or settings.top_k

        where = None
        if project_id:
            where = {"project_id": project_id}

        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
            where=where,
        )

        # Flatten results
        chunks = []
        for i in range(len(results.get("ids", [[]])[0])):
            chunk = {
                "chunk_id": results["ids"][0][i] if i < len(results["ids"][0]) else None,
                "content": results["documents"][0][i] if i < len(results["documents"][0]) else None,
                "metadata": results["metadatas"][0][i] if i < len(results["metadatas"][0]) else None,
                "distance": results["distances"][0][i] if i < len(results["distances"][0]) else None,
            }
            if chunk["distance"] is not None and chunk["distance"] >= score_threshold:
                chunks.append(chunk)

        logger.info(f"Query returned {len(chunks)} chunks")
        return chunks

    def delete_by_project(self, project_id: str) -> None:
        """Delete all chunks for a project.

        Args:
            project_id: Project ID to delete
        """
        collection = self._get_collection()
        collection.delete(where={"project_id": project_id})
        logger.info(f"Deleted chunks for project {project_id}")