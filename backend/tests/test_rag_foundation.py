"""Tests for RAG foundation services."""
from app.application.services.chunking_service import DocumentChunker


class TestDocumentChunker:
    def test_chunks_empty_content(self):
        chunker = DocumentChunker(chunk_size=100, chunk_overlap=20)
        chunks = chunker.chunk_text("   ", "doc1")
        assert chunks == []

    def test_chunks_short_content(self):
        chunker = DocumentChunker(chunk_size=100, chunk_overlap=20)
        chunks = chunker.chunk_text("Hello world", "doc1")
        assert len(chunks) == 1
        assert chunks[0][0] == "Hello world"
        assert chunks[0][1].chunk_id is not None

    def test_chunks_long_content(self):
        chunker = DocumentChunker(chunk_size=50, chunk_overlap=10)
        content = "This is a longer piece of content that should be split into multiple chunks."
        chunks = chunker.chunk_text(content, "doc1")
        assert len(chunks) > 1

    def test_chunk_metadata_preserved(self):
        chunker = DocumentChunker(chunk_size=100, chunk_overlap=20)
        chunks = chunker.chunk_text("Hello world", "doc1", "proj1", "markdown")
        assert chunks[0][1].document_id == "doc1"
        assert chunks[0][1].project_id == "proj1"
        assert chunks[0][1].source == "markdown"
        assert chunks[0][1].chunk_index == 0

    def test_total_chunks_updated(self):
        chunker = DocumentChunker(chunk_size=50, chunk_overlap=10)
        content = "This is long enough to create multiple chunks for testing."
        chunks = chunker.chunk_text(content, "doc1")
        total = len(chunks)
        for _, meta in chunks:
            assert meta.total_chunks == total

    def test_empty_document(self):
        """Test empty document returns no chunks."""
        chunker = DocumentChunker(chunk_size=100, chunk_overlap=20)
        chunks = chunker.chunk_text("", "doc1")
        assert chunks == []

    def test_document_shorter_than_chunk_size(self):
        """Test document shorter than chunk_size returns single chunk."""
        chunker = DocumentChunker(chunk_size=1000, chunk_overlap=200)
        chunks = chunker.chunk_text("Short text", "doc1")
        assert len(chunks) == 1
        assert chunks[0][0] == "Short text"

    def test_document_exactly_chunk_size(self):
        """Test document exactly chunk_size returns single chunk."""
        chunker = DocumentChunker(chunk_size=10, chunk_overlap=2)
        content = "1234567890"  # Exactly 10 chars
        chunks = chunker.chunk_text(content, "doc1")
        assert len(chunks) == 1

    def test_overlap_larger_than_document(self):
        """Test when overlap is larger than document."""
        chunker = DocumentChunker(chunk_size=100, chunk_overlap=200)
        chunks = chunker.chunk_text("Hi", "doc1")
        assert len(chunks) == 1
        assert chunks[0][0] == "Hi"

    def test_overlap_equal_to_chunk_size(self):
        """Test when overlap equals chunk_size."""
        chunker = DocumentChunker(chunk_size=10, chunk_overlap=10)
        content = "1234567890 1234567890 1234567890"  # 31 chars
        chunks = chunker.chunk_text(content, "doc1")
        assert len(chunks) >= 1  # Should not hang

    def test_very_large_document(self):
        """Test very large document is chunked properly."""
        chunker = DocumentChunker(chunk_size=100, chunk_overlap=20)
        content = "A" * 5000  # 5000 chars
        chunks = chunker.chunk_text(content, "doc1")
        assert len(chunks) > 1
        assert len(chunks) < 100  # Should not create too many chunks

    def test_whitespace_only_document(self):
        """Test whitespace-only document returns no chunks."""
        chunker = DocumentChunker(chunk_size=100, chunk_overlap=20)
        chunks = chunker.chunk_text("   \n\t   ", "doc1")
        assert chunks == []


class TestChunkingServiceIntegration:
    def test_markdown_chunking(self):
        chunker = DocumentChunker(chunk_size=100, chunk_overlap=20)
        chunks = chunker.chunk_markdown("# Title\nContent here", "doc1", "proj1")
        assert len(chunks) >= 1
        assert chunks[0][1].source == "markdown"

    def test_txt_chunking(self):
        chunker = DocumentChunker(chunk_size=100, chunk_overlap=20)
        chunks = chunker.chunk_txt("Plain text content", "doc1")
        assert len(chunks) >= 1
        assert chunks[0][1].source == "txt"

    def test_github_issue_chunking(self):
        chunker = DocumentChunker(chunk_size=100, chunk_overlap=20)
        chunks = chunker.chunk_github_issue("Bug report", "Description of the bug", 123)
        assert len(chunks) >= 1
        assert "Issue #123" in chunks[0][0]

    def test_github_pr_chunking(self):
        chunker = DocumentChunker(chunk_size=100, chunk_overlap=20)
        chunks = chunker.chunk_github_pr("Feature PR", "Description", 456)
        assert len(chunks) >= 1
        assert "PR #456" in chunks[0][0]


class TestEmbeddingService:
    def test_embedding_provider_interface(self):
        """Test embedding service initializes without error."""
        from app.application.services.embedding_service import EmbeddingService
        # Should not raise
        service = EmbeddingService(provider="openai")
        assert service is not None


class TestContextBuilder:
    def test_removes_duplicates(self):
        from app.application.services.retrieval_service import ContextBuilder, RetrievedChunk
        builder = ContextBuilder()
        chunks = [
            RetrievedChunk("Same content", {"source": "a"}, 0.9),
            RetrievedChunk("Same content", {"source": "b"}, 0.8),
        ]
        result = builder.build(chunks)
        assert result.count("Same content") == 1

    def test_sorts_by_score(self):
        from app.application.services.retrieval_service import ContextBuilder, RetrievedChunk
        builder = ContextBuilder()
        chunks = [
            RetrievedChunk("High score", {"source": "a"}, 0.5),
            RetrievedChunk("Medium score", {"source": "b"}, 0.7),
            RetrievedChunk("Low score", {"source": "c"}, 0.3),
        ]
        result = builder.build(chunks)
        # Higher score content should appear first
        assert result.index("Medium score") < result.index("Low score")


class TestChromaVectorStoreInterface:
    def test_vector_store_interface(self):
        """Test ChromaVectorStore has required methods."""
        from app.infrastructure.vectorstore.chroma_store import ChromaVectorStore
        store = ChromaVectorStore(persist_path="./test_chroma")
        assert hasattr(store, "upsert")
        assert hasattr(store, "query")
        assert hasattr(store, "delete_by_project")