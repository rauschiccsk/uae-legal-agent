"""Text embedding generation using OpenAI API with caching and retry logic."""

import time
import hashlib
from typing import List, Dict, Optional, Any
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential
from utils.logger import logger
from utils.config import settings


class EmbeddingsClient:
    """Client for generating text embeddings with OpenAI API.
    
    Features:
    - Single and batch text processing
    - Response caching for efficiency
    - Automatic retry logic with exponential backoff
    - Usage tracking (tokens and API calls)
    """

    def __init__(self, model_name: str = "text-embedding-3-small"):
        """
        Initialize embeddings client.

        Args:
            model_name: OpenAI embedding model name
        """
        self.model_name = model_name
        self._client = None
        self._cache: Dict[str, List[float]] = {}
        self._usage_stats = {
            "total_tokens": 0,
            "total_requests": 0,
            "cache_hits": 0,
            "cache_misses": 0
        }
        logger.info(f"EmbeddingsClient initialized with model: {self.model_name}")

    @property
    def client(self) -> OpenAI:
        """Lazy loading OpenAI client - created on first use."""
        if self._client is None:
            logger.info("Initializing OpenAI client")
            self._client = OpenAI(api_key=settings.openai_api_key)
            logger.info("OpenAI client successfully initialized")
        return self._client

    def _get_cache_key(self, text: str) -> str:
        """Generate cache key for text.
        
        Args:
            text: Input text
            
        Returns:
            Cache key (hash)
        """
        return hashlib.md5(f"{self.model_name}:{text}".encode()).hexdigest()

    def _get_from_cache(self, text: str) -> Optional[List[float]]:
        """Get embedding from cache if available.
        
        Args:
            text: Input text
            
        Returns:
            Cached embedding or None
        """
        cache_key = self._get_cache_key(text)
        if cache_key in self._cache:
            self._usage_stats["cache_hits"] += 1
            logger.debug(f"Cache hit for text: {text[:50]}...")
            return self._cache[cache_key]
        
        self._usage_stats["cache_misses"] += 1
        return None

    def _add_to_cache(self, text: str, embedding: List[float]) -> None:
        """Add embedding to cache.
        
        Args:
            text: Input text
            embedding: Generated embedding
        """
        cache_key = self._get_cache_key(text)
        self._cache[cache_key] = embedding

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    def _call_api(self, texts: List[str]) -> Any:
        """Call OpenAI API with retry logic.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            API response
        """
        self._usage_stats["total_requests"] += 1
        response = self.client.embeddings.create(
            model=self.model_name,
            input=texts
        )
        self._usage_stats["total_tokens"] += response.usage.total_tokens
        return response

    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for single text with caching.

        Args:
            text: Text to embed

        Returns:
            Embedding vector (normalized)
        """
        if not text or not text.strip():
            logger.warning("Empty text for embedding")
            return []

        # Check cache first
        cached = self._get_from_cache(text)
        if cached is not None:
            return cached

        logger.info(f"Generating embedding for text: '{text[:50]}...'")

        try:
            response = self._call_api([text])
            embedding = response.data[0].embedding
            
            # Cache result
            self._add_to_cache(text, embedding)
            
            logger.info("Embedding successfully generated")
            return embedding

        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise

    def generate_embeddings(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """
        Generate embeddings for list of texts with batch processing and caching.

        Args:
            texts: List of texts to embed
            batch_size: Batch size for processing

        Returns:
            List of embedding vectors (normalized for cosine similarity)
        """
        if not texts:
            logger.warning("Empty text list for embeddings")
            return []

        logger.info(f"Generating embeddings for {len(texts)} texts (batch_size={batch_size})")

        all_embeddings = []
        texts_to_process = []
        indices_to_process = []

        # Check cache for each text
        for idx, text in enumerate(texts):
            cached = self._get_from_cache(text)
            if cached is not None:
                all_embeddings.append((idx, cached))
            else:
                texts_to_process.append(text)
                indices_to_process.append(idx)

        # Process uncached texts in batches
        if texts_to_process:
            try:
                for i in range(0, len(texts_to_process), batch_size):
                    batch = texts_to_process[i:i + batch_size]
                    batch_indices = indices_to_process[i:i + batch_size]
                    
                    response = self._call_api(batch)
                    
                    batch_embeddings = [item.embedding for item in response.data]
                    
                    # Cache and collect results
                    for text, embedding, original_idx in zip(batch, batch_embeddings, batch_indices):
                        self._add_to_cache(text, embedding)
                        all_embeddings.append((original_idx, embedding))
                    
                    logger.info(f"Processed batch {i//batch_size + 1}/{(len(texts_to_process)-1)//batch_size + 1}")

            except Exception as e:
                logger.error(f"Error generating embeddings: {e}")
                raise

        # Sort by original index and extract embeddings
        all_embeddings.sort(key=lambda x: x[0])
        result = [emb for _, emb in all_embeddings]

        logger.info(f"Embeddings successfully generated: {len(result)} vectors")
        return result

    def generate_query_embedding(self, query: str) -> List[float]:
        """
        Generate embedding for search query.

        Args:
            query: Search query text

        Returns:
            Embedding vector (normalized)
        """
        return self.generate_embedding(query)

    def get_embedding_dimension(self) -> int:
        """
        Get embedding vector dimension.

        Returns:
            Number of dimensions (1536 for text-embedding-3-small)
        """
        return 1536

    def get_usage_stats(self) -> Dict[str, int]:
        """Get usage statistics.
        
        Returns:
            Dictionary with usage stats
        """
        return self._usage_stats.copy()

    def clear_cache(self) -> None:
        """Clear embedding cache."""
        cache_size = len(self._cache)
        self._cache.clear()
        logger.info(f"Cache cleared: {cache_size} entries removed")

    def get_cache_size(self) -> int:
        """Get current cache size.
        
        Returns:
            Number of cached embeddings
        """
        return len(self._cache)