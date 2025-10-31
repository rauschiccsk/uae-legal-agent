"""Pure-Python vector store - NO external dependencies (stdlib only)."""

import pickle
import math
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class SimpleVectorStore:
    """In-memory vector store with cosine similarity search."""

    def __init__(self, persist_path: Optional[str] = None):
        """Initialize simple vector store.

        Args:
            persist_path: Path to pickle file for persistence (optional)
        """
        self.documents: List[str] = []
        self.embeddings: List[List[float]] = []
        self.metadatas: List[Dict] = []
        self.ids: List[str] = []
        self.persist_path = Path(persist_path) if persist_path else None

        # Try to load existing data
        if self.persist_path and self.persist_path.exists():
            self._load()

    def add(
            self,
            documents: List[str],
            embeddings: List[List[float]],
            metadatas: List[Dict],
            ids: List[str]
    ) -> None:
        """Add documents with embeddings.

        Args:
            documents: List of text documents
            embeddings: List of embedding vectors
            metadatas: List of metadata dicts
            ids: List of document IDs
        """
        if not (len(documents) == len(embeddings) == len(metadatas) == len(ids)):
            raise ValueError("All lists must have same length")

        # Validate embeddings dimension
        if self.embeddings and embeddings:
            expected_dim = len(self.embeddings[0])
            for emb in embeddings:
                if len(emb) != expected_dim:
                    raise ValueError(f"Embedding dimension mismatch: expected {expected_dim}, got {len(emb)}")

        # Add to storage
        self.documents.extend(documents)
        self.embeddings.extend(embeddings)
        self.metadatas.extend(metadatas)
        self.ids.extend(ids)

        logger.debug(f"Added {len(documents)} documents (total: {len(self.documents)})")

    def query(
            self,
            query_embeddings: List[List[float]],
            n_results: int = 5
    ) -> Dict:
        """Query with embeddings using cosine similarity.

        Args:
            query_embeddings: List of query embedding vectors
            n_results: Number of results to return

        Returns:
            Dict with 'ids', 'documents', 'metadatas', 'distances'
        """
        if not self.embeddings:
            return {
                'ids': [[]],
                'documents': [[]],
                'metadatas': [[]],
                'distances': [[]]
            }

        query_emb = query_embeddings[0]  # Take first query

        # Calculate cosine similarity for all documents
        similarities = []
        for idx, doc_emb in enumerate(self.embeddings):
            sim = self._cosine_similarity(query_emb, doc_emb)
            similarities.append((idx, sim))

        # Sort by similarity (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)

        # Take top N results
        top_indices = [idx for idx, _ in similarities[:n_results]]

        # Format results
        result_ids = [self.ids[i] for i in top_indices]
        result_docs = [self.documents[i] for i in top_indices]
        result_meta = [self.metadatas[i] for i in top_indices]
        result_dist = [1.0 - similarities[i][1] for i in range(len(top_indices))]  # Convert similarity to distance

        return {
            'ids': [result_ids],
            'documents': [result_docs],
            'metadatas': [result_meta],
            'distances': [result_dist]
        }

    def count(self) -> int:
        """Get number of documents."""
        return len(self.documents)

    def clear(self) -> None:
        """Clear all data."""
        self.documents.clear()
        self.embeddings.clear()
        self.metadatas.clear()
        self.ids.clear()
        logger.info("Store cleared")

    def save(self) -> bool:
        """Save store to disk using pickle.

        Returns:
            True if successful, False otherwise
        """
        if not self.persist_path:
            logger.warning("No persist_path configured")
            return False

        try:
            # Create directory if needed
            self.persist_path.parent.mkdir(parents=True, exist_ok=True)

            # Save data
            data = {
                'documents': self.documents,
                'embeddings': self.embeddings,
                'metadatas': self.metadatas,
                'ids': self.ids
            }

            with open(self.persist_path, 'wb') as f:
                pickle.dump(data, f)

            logger.info(f"Store saved to {self.persist_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to save store: {e}")
            return False

    def _load(self) -> bool:
        """Load store from disk.

        Returns:
            True if successful, False otherwise
        """
        try:
            with open(self.persist_path, 'rb') as f:
                data = pickle.load(f)

            self.documents = data['documents']
            self.embeddings = data['embeddings']
            self.metadatas = data['metadatas']
            self.ids = data['ids']

            logger.info(f"Store loaded from {self.persist_path} ({len(self.documents)} docs)")
            return True

        except Exception as e:
            logger.error(f"Failed to load store: {e}")
            return False

    @staticmethod
    def _cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors.

        Args:
            vec1: First vector
            vec2: Second vector

        Returns:
            Cosine similarity (0 to 1)
        """
        if len(vec1) != len(vec2):
            raise ValueError(f"Vector dimension mismatch: {len(vec1)} vs {len(vec2)}")

        # Dot product
        dot_product = sum(a * b for a, b in zip(vec1, vec2))

        # Magnitudes
        mag1 = math.sqrt(sum(a * a for a in vec1))
        mag2 = math.sqrt(sum(b * b for b in vec2))

        # Avoid division by zero
        if mag1 == 0 or mag2 == 0:
            return 0.0

        return dot_product / (mag1 * mag2)

    def get_stats(self) -> Dict:
        """Get store statistics.

        Returns:
            Dict with store statistics
        """
        return {
            'document_count': len(self.documents),
            'embedding_dimension': len(self.embeddings[0]) if self.embeddings else 0,
            'persist_path': str(self.persist_path) if self.persist_path else None,
            'mode': 'in-memory (pure-Python)'
        }


class VectorStore:
    """Wrapper class for backward compatibility with ChromaDB interface."""

    def __init__(self, collection_name: str = None):
        """Initialize VectorStore wrapper.

        Args:
            collection_name: Collection name (used for persist filename)
        """
        self.collection_name = collection_name or "uae_legal_docs"
        self.collection = None

    def initialize_db(self) -> bool:
        """Initialize simple vector store.

        Returns:
            True if successful
        """
        try:
            persist_dir = Path("data/simple_vector_store")
            persist_path = persist_dir / f"{self.collection_name}.pkl"

            self.collection = SimpleVectorStore(persist_path=str(persist_path))

            logger.info(f"Simple vector store initialized: {self.collection_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize store: {e}")
            return False

    def add_document(
            self,
            text: str,
            embedding: List[float],
            metadata: Optional[Dict] = None,
            doc_id: Optional[str] = None
    ) -> Optional[str]:
        """Add single document (compatibility method).

        Args:
            text: Document text
            embedding: Embedding vector
            metadata: Metadata dict
            doc_id: Document ID

        Returns:
            Document ID if successful, None otherwise
        """
        try:
            if not self.collection:
                logger.error("Collection not initialized")
                return None

            if not doc_id:
                import uuid
                doc_id = str(uuid.uuid4())

            self.collection.add(
                documents=[text],
                embeddings=[embedding],
                metadatas=[metadata or {}],
                ids=[doc_id]
            )

            return doc_id

        except Exception as e:
            logger.error(f"Failed to add document: {e}")
            return None

    def search(
            self,
            query: str,
            top_k: int = 5,
            n_results: int = None
    ) -> List[Dict]:
        """Semantic search (compatibility method).

        Note: This method signature expects a text query, but SimpleVectorStore
        needs embeddings. This is a compatibility shim - actual usage should
        provide embeddings directly to collection.query().

        Args:
            query: Query text (needs embedding first!)
            top_k: Number of results
            n_results: Alternative parameter for number of results

        Returns:
            List of result dicts
        """
        n_results = n_results or top_k

        logger.warning("search() called with text query - needs embedding first!")
        logger.warning("Use collection.query() with embeddings directly")

        return []

    def get_collection_stats(self) -> Dict:
        """Get collection statistics.

        Returns:
            Dict with statistics
        """
        if not self.collection:
            return {}

        stats = self.collection.get_stats()
        stats['collection_name'] = self.collection_name
        return stats

    def clear_collection(self) -> bool:
        """Clear collection.

        Returns:
            True if successful
        """
        try:
            if not self.collection:
                return False

            self.collection.clear()
            logger.info("Collection cleared")
            return True

        except Exception as e:
            logger.error(f"Failed to clear collection: {e}")
            return False


# Backward compatibility
VectorDB = VectorStore