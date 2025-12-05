"""
Embeddings service for the G3TI RTCC-UIP Backend.

This service provides text embedding generation for semantic search
and similarity matching. The service is designed to support multiple
embedding providers (OpenAI, local models, etc.).

Current implementation provides the interface and foundation.
Model integration will be added in future phases.
"""

from abc import ABC, abstractmethod

from app.core.logging import get_logger

logger = get_logger(__name__)


class EmbeddingProvider(ABC):
    """Abstract base class for embedding providers."""

    @abstractmethod
    async def generate_embedding(self, text: str) -> list[float]:
        """
        Generate embedding vector for text.

        Args:
            text: Text to embed

        Returns:
            list[float]: Embedding vector
        """
        pass

    @abstractmethod
    async def generate_embeddings(self, texts: list[str]) -> list[list[float]]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed

        Returns:
            list[list[float]]: List of embedding vectors
        """
        pass

    @property
    @abstractmethod
    def dimension(self) -> int:
        """Get the embedding dimension."""
        pass


class MockEmbeddingProvider(EmbeddingProvider):
    """
    Mock embedding provider for development and testing.

    Generates deterministic pseudo-embeddings based on text hash.
    Should be replaced with a real provider in production.
    """

    EMBEDDING_DIM = 384  # Common dimension for sentence transformers

    async def generate_embedding(self, text: str) -> list[float]:
        """Generate a mock embedding based on text hash."""
        import hashlib

        # Create deterministic pseudo-random embedding
        text_hash = hashlib.sha256(text.encode()).hexdigest()

        embedding = []
        for i in range(0, min(len(text_hash), self.EMBEDDING_DIM * 2), 2):
            # Convert hex pairs to float values between -1 and 1
            value = (int(text_hash[i : i + 2], 16) - 128) / 128.0
            embedding.append(value)

        # Pad or truncate to exact dimension
        while len(embedding) < self.EMBEDDING_DIM:
            embedding.append(0.0)

        return embedding[: self.EMBEDDING_DIM]

    async def generate_embeddings(self, texts: list[str]) -> list[list[float]]:
        """Generate mock embeddings for multiple texts."""
        return [await self.generate_embedding(text) for text in texts]

    @property
    def dimension(self) -> int:
        """Get the embedding dimension."""
        return self.EMBEDDING_DIM


class EmbeddingsService:
    """
    Service for generating and managing text embeddings.

    Provides a unified interface for embedding generation with
    support for multiple providers and caching.
    """

    def __init__(self, provider: EmbeddingProvider | None = None) -> None:
        """
        Initialize the embeddings service.

        Args:
            provider: Embedding provider to use (defaults to mock)
        """
        self._provider = provider or MockEmbeddingProvider()
        self._cache: dict[str, list[float]] = {}
        self._cache_enabled = True
        self._max_cache_size = 10000

    async def embed_text(self, text: str, use_cache: bool = True) -> list[float]:
        """
        Generate embedding for text.

        Args:
            text: Text to embed
            use_cache: Whether to use cached embeddings

        Returns:
            list[float]: Embedding vector
        """
        # Normalize text
        text = text.strip()
        if not text:
            return [0.0] * self._provider.dimension

        # Check cache
        cache_key = self._get_cache_key(text)
        if use_cache and self._cache_enabled and cache_key in self._cache:
            return self._cache[cache_key]

        # Generate embedding
        embedding = await self._provider.generate_embedding(text)

        # Cache result
        if use_cache and self._cache_enabled:
            self._add_to_cache(cache_key, embedding)

        return embedding

    async def embed_texts(self, texts: list[str], use_cache: bool = True) -> list[list[float]]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed
            use_cache: Whether to use cached embeddings

        Returns:
            list[list[float]]: List of embedding vectors
        """
        if not texts:
            return []

        results: list[list[float] | None] = [None] * len(texts)
        texts_to_embed: list[tuple[int, str]] = []

        # Check cache for each text
        for i, text in enumerate(texts):
            text = text.strip()
            if not text:
                results[i] = [0.0] * self._provider.dimension
                continue

            cache_key = self._get_cache_key(text)
            if use_cache and self._cache_enabled and cache_key in self._cache:
                results[i] = self._cache[cache_key]
            else:
                texts_to_embed.append((i, text))

        # Generate embeddings for uncached texts
        if texts_to_embed:
            indices, uncached_texts = zip(*texts_to_embed, strict=False)
            embeddings = await self._provider.generate_embeddings(list(uncached_texts))

            for idx, text, embedding in zip(indices, uncached_texts, embeddings, strict=False):
                results[idx] = embedding
                if use_cache and self._cache_enabled:
                    cache_key = self._get_cache_key(text)
                    self._add_to_cache(cache_key, embedding)

        return [r for r in results if r is not None]

    async def compute_similarity(self, text1: str, text2: str) -> float:
        """
        Compute cosine similarity between two texts.

        Args:
            text1: First text
            text2: Second text

        Returns:
            float: Cosine similarity score (0-1)
        """
        emb1 = await self.embed_text(text1)
        emb2 = await self.embed_text(text2)

        return self._cosine_similarity(emb1, emb2)

    async def find_similar(
        self, query_text: str, candidate_texts: list[str], top_k: int = 10, threshold: float = 0.0
    ) -> list[tuple[int, float]]:
        """
        Find most similar texts to a query.

        Args:
            query_text: Query text
            candidate_texts: List of candidate texts
            top_k: Number of results to return
            threshold: Minimum similarity threshold

        Returns:
            list[tuple[int, float]]: List of (index, similarity) tuples
        """
        query_embedding = await self.embed_text(query_text)
        candidate_embeddings = await self.embed_texts(candidate_texts)

        similarities: list[tuple[int, float]] = []
        for i, candidate_emb in enumerate(candidate_embeddings):
            sim = self._cosine_similarity(query_embedding, candidate_emb)
            if sim >= threshold:
                similarities.append((i, sim))

        # Sort by similarity descending
        similarities.sort(key=lambda x: x[1], reverse=True)

        return similarities[:top_k]

    @property
    def dimension(self) -> int:
        """Get the embedding dimension."""
        return self._provider.dimension

    def clear_cache(self) -> None:
        """Clear the embedding cache."""
        self._cache.clear()
        logger.info("embedding_cache_cleared")

    def _get_cache_key(self, text: str) -> str:
        """Generate cache key for text."""
        import hashlib

        return hashlib.md5(text.encode()).hexdigest()

    def _add_to_cache(self, key: str, embedding: list[float]) -> None:
        """Add embedding to cache with size limit."""
        if len(self._cache) >= self._max_cache_size:
            # Remove oldest entries (simple FIFO)
            keys_to_remove = list(self._cache.keys())[:1000]
            for k in keys_to_remove:
                del self._cache[k]

        self._cache[key] = embedding

    @staticmethod
    def _cosine_similarity(vec1: list[float], vec2: list[float]) -> float:
        """Compute cosine similarity between two vectors."""
        import math

        if len(vec1) != len(vec2):
            raise ValueError("Vectors must have same dimension")

        dot_product = sum(a * b for a, b in zip(vec1, vec2, strict=False))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)


# Global embeddings service instance
_embeddings_service: EmbeddingsService | None = None


def get_embeddings_service() -> EmbeddingsService:
    """Get the embeddings service instance."""
    global _embeddings_service
    if _embeddings_service is None:
        _embeddings_service = EmbeddingsService()
    return _embeddings_service
