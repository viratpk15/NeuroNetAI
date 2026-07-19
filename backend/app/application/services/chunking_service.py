"""Document chunking service for RAG foundation."""
import uuid

from app.shared.config import get_settings


class ChunkMetadata:
    """Metadata for a document chunk."""

    def __init__(
        self,
        chunk_id: str,
        document_id: str,
        project_id: str | None,
        source: str,
        chunk_index: int,
        total_chunks: int,
    ):
        self.chunk_id = chunk_id
        self.document_id = document_id
        self.project_id = project_id
        self.source = source
        self.chunk_index = chunk_index
        self.total_chunks = total_chunks


class DocumentChunker:
    """Chunks documents for embedding and retrieval."""

    def __init__(self, chunk_size: int | None = None, chunk_overlap: int | None = None):
        settings = get_settings()
        self.chunk_size = chunk_size or settings.chunk_size
        self.chunk_overlap = chunk_overlap or settings.chunk_overlap

    def chunk_text(
        self,
        content: str,
        document_id: str,
        project_id: str | None = None,
        source: str = "unknown",
    ) -> list[tuple[str, ChunkMetadata]]:
        """Chunk text content into overlapping segments.

        Args:
            content: Text content to chunk
            document_id: Source document ID
            project_id: Optional project ID
            source: Source type (markdown, txt, github_issue, github_pr)

        Returns:
            List of (chunk_text, metadata) tuples
        """
        if not content.strip():
            return []

        chunks = []
        start = 0
        chunk_index = 0

        while start < len(content):
            end = min(start + self.chunk_size, len(content))

            # If we've reached the end, break
            if end >= len(content):
                chunk_text = content[start:].strip()
                if chunk_text:
                    chunk_id = str(uuid.uuid4())
                    metadata = ChunkMetadata(
                        chunk_id=chunk_id,
                        document_id=document_id,
                        project_id=project_id,
                        source=source,
                        chunk_index=chunk_index,
                        total_chunks=0,
                    )
                    chunks.append((chunk_text, metadata))
                break

            chunk_text = content[start:end].strip()

            if chunk_text:
                chunk_id = str(uuid.uuid4())
                metadata = ChunkMetadata(
                    chunk_id=chunk_id,
                    document_id=document_id,
                    project_id=project_id,
                    source=source,
                    chunk_index=chunk_index,
                    total_chunks=0,
                )
                chunks.append((chunk_text, metadata))
                chunk_index += 1

            # Compute next start with overlap
            next_start = end - self.chunk_overlap

            # Guarantee forward progress
            if next_start <= start:
                next_start = end

            start = next_start

        # Update total_chunks count
        total = len(chunks)
        for _, meta in chunks:
            meta.total_chunks = total

        return chunks

    def chunk_markdown(self, content: str, document_id: str, project_id: str | None = None) -> list[tuple[str, ChunkMetadata]]:
        """Chunk markdown content preserving headers when possible."""
        return self.chunk_text(content, document_id, project_id, "markdown")

    def chunk_txt(self, content: str, document_id: str, project_id: str | None = None) -> list[tuple[str, ChunkMetadata]]:
        """Chunk plain text content."""
        return self.chunk_text(content, document_id, project_id, "txt")

    def chunk_github_issue(self, title: str, body: str, issue_number: int, project_id: str | None = None) -> list[tuple[str, ChunkMetadata]]:
        """Chunk GitHub issue content."""
        combined = f"Issue #{issue_number}: {title}\n\n{body}"
        document_id = f"github_issue_{issue_number}"
        return self.chunk_text(combined, document_id, project_id, "github_issue")

    def chunk_github_pr(self, title: str, body: str, pr_number: int, project_id: str | None = None) -> list[tuple[str, ChunkMetadata]]:
        """Chunk GitHub PR content."""
        combined = f"PR #{pr_number}: {title}\n\n{body}"
        document_id = f"github_pr_{pr_number}"
        return self.chunk_text(combined, document_id, project_id, "github_pr")