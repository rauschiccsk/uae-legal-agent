"""ChromaDB vector database - EPHEMERAL with minimal metadata (no HNSW)."""

import chromadb
from chromadb.config import Settings
from typing import Dict, List, Optional
import os
from pathlib import Path

from config import settings
from utils.logger import get_logger

logger = get_logger(__name__)


class VectorStore:
    """ChromaDB vector store - EPHEMERAL + NO HNSW."""

    def __init__(self, collection_name: str = None):
        """Initialize VectorStore with collection name."""
        self.collection_name = collection_name or settings.CHROMA_COLLECTION_NAME
        self.client = None
        self.collection = None

    def initialize_db(self) -> bool:
        """Create ephemeral ChromaDB without HNSW index."""
        try:
            logger.info("Initializing EPHEMERAL ChromaDB (in-memory, no HNSW)")

            # Use ephemeral client
            self.client = chromadb.EphemeralClient(
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )

            # Get or create collection with minimal metadata (no HNSW)
            logger.info("Creating collection without HNSW index...")
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description": "UAE legal documents"}
            )

            logger.info(f"EPHEMERAL collection '{self.collection_name}' ready (no HNSW)")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            return False

    def add_document(
        self,
        text: str,
        embedding: List[float],
        metadata: Optional[Dict] = None,
        doc_id: Optional[str] = None
    ) -> Optional[str]:
        """Add document with embeddings to collection."""
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

            logger.debug(f"Document added: {doc_id}")
            return doc_id

        except Exception as e:
            logger.error(f"Failed to add document: {e}")
            return None

    def search(self, query: str, top_k: int = 5, n_results: int = None) -> List[Dict]:
        """Perform semantic search."""
        n_results = n_results or top_k

        try:
            if not self.collection:
                logger.error("Collection not initialized")
                return []

            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )

            formatted = []
            if results and results['documents']:
                for i in range(len(results['documents'][0])):
                    formatted.append({
                        'id': results['ids'][0][i],
                        'text': results['documents'][0][i],
                        'document': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                        'distance': results['distances'][0][i] if results.get('distances') else None
                    })

            return formatted

        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    def get_collection_stats(self) -> Dict:
        """Get collection statistics."""
        try:
            if not self.collection:
                return {}

            count = self.collection.count()

            return {
                'collection_name': self.collection_name,
                'document_count': count,
                'mode': 'ephemeral (no HNSW)'
            }

        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {}

    def clear_collection(self) -> bool:
        """Clear all documents."""
        try:
            if not self.collection:
                return False

            self.client.delete_collection(name=self.collection_name)
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "UAE legal documents"}
            )

            logger.info(f"Collection cleared")
            return True

        except Exception as e:
            logger.error(f"Failed to clear: {e}")
            return False


# Backward compatibility
VectorDB = VectorStore