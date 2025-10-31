"""ChromaDB vector database management for semantic search."""

import chromadb
from chromadb.config import Settings
from typing import Dict, List, Optional
import os
from pathlib import Path

from config import settings
from utils.logger import get_logger

logger = get_logger(__name__)


class VectorStore:
    """ChromaDB vector store manager for document embeddings."""

    def __init__(self, collection_name: str = None):
        """Initialize VectorStore with collection name."""
        self.collection_name = collection_name or settings.CHROMA_COLLECTION_NAME
        self.client = None
        self.collection = None

    def initialize_db(self) -> bool:
        """Create or connect to ChromaDB database."""
        try:
            # Create persistence directory
            persist_dir = Path(settings.CHROMA_PERSIST_DIRECTORY)
            persist_dir.mkdir(parents=True, exist_ok=True)

            logger.info(f"Initializing ChromaDB at {persist_dir}")

            # Initialize ChromaDB client with persistence
            self.client = chromadb.PersistentClient(
                path=str(persist_dir),
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )

            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )

            logger.info(f"ChromaDB collection '{self.collection_name}' ready")
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

            # Generate ID if not provided
            if not doc_id:
                import uuid
                doc_id = str(uuid.uuid4())

            # Add document with embedding
            self.collection.add(
                documents=[text],
                embeddings=[embedding],
                metadatas=[metadata or {}],
                ids=[doc_id]
            )

            logger.info(f"Document added with ID: {doc_id}")
            return doc_id

        except Exception as e:
            logger.error(f"Failed to add document: {e}")
            return None

    def search(self, query: str, top_k: int = 5, n_results: int = None) -> List[Dict]:
        """Perform semantic search in collection."""
        # Handle both parameter names for compatibility
        n_results = n_results or top_k

        try:
            if not self.collection:
                logger.error("Collection not initialized")
                return []

            # Query collection
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )

            # Format results
            formatted_results = []
            if results and results['documents']:
                for i in range(len(results['documents'][0])):
                    formatted_results.append({
                        'id': results['ids'][0][i],
                        'text': results['documents'][0][i],
                        'document': results['documents'][0][i],  # Alias for compatibility
                        'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                        'distance': results['distances'][0][i] if results.get('distances') else None,
                        'embedding': results['embeddings'][0][i] if results.get('embeddings') else None
                    })

            logger.info(f"Search returned {len(formatted_results)} results")
            return formatted_results

        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    def delete_document(self, doc_id: str) -> bool:
        """Delete document from collection."""
        try:
            if not self.collection:
                logger.error("Collection not initialized")
                return False

            self.collection.delete(ids=[doc_id])
            logger.info(f"Document {doc_id} deleted")
            return True

        except Exception as e:
            logger.error(f"Failed to delete document: {e}")
            return False

    def get_collection_stats(self) -> Dict:
        """Get collection statistics."""
        try:
            if not self.collection:
                logger.error("Collection not initialized")
                return {}

            count = self.collection.count()

            stats = {
                'collection_name': self.collection_name,
                'document_count': count,
                'persist_directory': settings.CHROMA_PERSIST_DIRECTORY
            }

            logger.info(f"Collection stats: {count} documents")
            return stats

        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {}

    def clear_collection(self) -> bool:
        """Clear all documents from collection."""
        try:
            if not self.collection:
                logger.error("Collection not initialized")
                return False

            # Delete collection and recreate
            self.client.delete_collection(name=self.collection_name)
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )

            logger.info(f"Collection '{self.collection_name}' cleared")
            return True

        except Exception as e:
            logger.error(f"Failed to clear collection: {e}")
            return False


# Backward compatibility alias
VectorDB = VectorStore