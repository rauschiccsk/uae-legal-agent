"""
Embedding Manager Module
Generates text embeddings using SentenceTransformer for RAG pipeline.
Supports multilingual embeddings (Arabic/English/Slovak).
Uses paraphrase-multilingual-MiniLM-L12-v2 model with lazy loading.
"""

from typing import List, Union, Optional
import numpy as np


class EmbeddingManager:
    """
    Manages text embeddings generation for the RAG pipeline.
    Uses SentenceTransformer with multilingual support.
    Implements lazy loading of the model.
    """
    
    def __init__(self, model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"):
        """
        Initialize the embedding manager with SentenceTransformer.
        
        Args:
            model_name: Name of the SentenceTransformer model to use.
                       Default uses paraphrase-multilingual-MiniLM-L12-v2.
        """
        self.model_name = model_name
        self._model: Optional['SentenceTransformer'] = None
        self.embedding_dimension = 384  # paraphrase-multilingual-MiniLM-L12-v2 dimension
    
    @property
    def model(self):
        """
        Lazy loading property for the SentenceTransformer model.
        Model is only loaded when first accessed.
        
        Returns:
            Loaded SentenceTransformer model instance
        """
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.model_name)
            # Update embedding dimension from actual model
            self.embedding_dimension = self._model.get_sentence_embedding_dimension()
        return self._model
    
    def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for a list of text chunks.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            numpy array of shape (len(texts), embedding_dimension)
            
        Raises:
            ValueError: If texts list is empty
        """
        if not texts:
            raise ValueError("Cannot generate embeddings for empty text list")
        
        # Generate embeddings using SentenceTransformer
        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
            show_progress_bar=False
        )
        
        return embeddings
    
    def generate_query_embedding(self, query: str) -> np.ndarray:
        """
        Generate embedding for a single query string.
        
        Args:
            query: Query text to embed
            
        Returns:
            numpy array of shape (embedding_dimension,)
            
        Raises:
            ValueError: If query is empty
        """
        if not query or not query.strip():
            raise ValueError("Cannot generate embedding for empty query")
        
        # Generate single embedding using SentenceTransformer
        embedding = self.model.encode(
            query,
            convert_to_numpy=True,
            show_progress_bar=False
        )
        
        return embedding
    
    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of the embeddings produced by this model.
        
        Returns:
            Integer dimension of embedding vectors
        """
        return self.embedding_dimension
    
    def get_model_info(self) -> dict:
        """
        Get information about the current embedding model.
        
        Returns:
            Dictionary containing model information
        """
        return {
            "model_name": self.model_name,
            "embedding_dimension": self.embedding_dimension,
            "max_sequence_length": 128,  # paraphrase-multilingual-MiniLM-L12-v2 max tokens
            "supports_languages": ["Arabic", "English", "Slovak", "50+ others"]
        }