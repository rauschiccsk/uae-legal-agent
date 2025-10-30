"""
Embedding Manager Module
Generates text embeddings using sentence-transformers for RAG pipeline.
Supports multilingual embeddings (Arabic/English/Slovak).
"""

from typing import List, Union
import numpy as np
from sentence_transformers import SentenceTransformer


class EmbeddingManager:
    """
    Manages text embeddings generation for the RAG pipeline.
    Supports multilingual embeddings for Arabic, English, and Slovak.
    """
    
    def __init__(self, model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"):
        """
        Initialize the embedding manager with a multilingual model.
        
        Args:
            model_name: Name of the sentence-transformer model to use.
                       Default uses multilingual model supporting 50+ languages
                       including Arabic, English, and Slovak.
        """
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
        self.embedding_dimension = self.model.get_sentence_embedding_dimension()
    
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
        
        # Generate embeddings
        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
            show_progress_bar=True,
            batch_size=32
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
        
        # Generate single embedding
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
            "max_sequence_length": self.model.max_seq_length,
            "supports_languages": ["Arabic", "English", "Slovak", "50+ others"]
        }