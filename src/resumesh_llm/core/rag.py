import asyncio
import re
from typing import Any


class AsyncRAGPipeline:
    """An asynchronous RAG pipeline that processes documents (e.g. ATS rules, job regulations)

    and retrieves relevant context chunks asynchronously.
    """

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 100):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.documents: dict[str, str] = {}
        self.chunks: list[dict[str, Any]] = []

    async def add_document(
        self, doc_id: str, content: str, metadata: dict[str, Any] | None = None
    ) -> None:
        """Asynchronously processes and indexes a document."""
        await asyncio.sleep(0)  # Yield execution to keep it non-blocking
        self.documents[doc_id] = content

        # Split content into overlapping chunks
        words = content.split()
        doc_chunks = []
        i = 0
        while i < len(words):
            chunk_words = words[i : i + self.chunk_size]
            chunk_text = " ".join(chunk_words)
            doc_chunks.append(
                {
                    "doc_id": doc_id,
                    "text": chunk_text,
                    "metadata": metadata or {},
                }
            )
            if len(chunk_words) < self.chunk_size:
                break
            i += self.chunk_size - self.chunk_overlap

        self.chunks.extend(doc_chunks)

    async def retrieve(self, query: str, top_k: int = 3) -> list[dict[str, Any]]:
        """Asynchronously retrieves the top_k relevant chunks using keyword relevance scoring."""
        await asyncio.sleep(0)  # Yield execution
        if not self.chunks:
            return []

        # Tokenize query
        query_words = set(re.findall(r"\w+", query.lower()))
        if not query_words:
            return self.chunks[:top_k]

        scored_chunks = []
        for chunk in self.chunks:
            chunk_words = re.findall(r"\w+", chunk["text"].lower())
            # Simple TF (term frequency) style scoring
            score = sum(chunk_words.count(qw) for qw in query_words)
            scored_chunks.append((score, chunk))

        # Sort by score descending
        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        return [chunk for score, chunk in scored_chunks[:top_k]]
