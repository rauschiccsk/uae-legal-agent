"""
Embedding Manager Module
Generates text embeddings using OpenAI API for RAG pipeline.
Supports multilingual embeddings (Arabic/English/Slovak).
Uses text-embedding-3-small model (1536 dimensions, cost-effective).
Resolves 32-bit Python compatibility issue (torch not available for 32-bit).
"""

from typing import List, Union
import numpy as np
from openai import OpenAI
from config import settings


class EmbeddingManager:
    """
    Manages text embeddings generation for the RAG pipeline.
    Uses OpenAI text-embedding-3-small model for multilingual support.
    """
    
    def __init__(self, model_name: str = "text-embedding-3-small"):
        """
        Initialize the embedding manager with OpenAI API.
        
        Args:
            model_name: Name of the OpenAI embedding model to use.
                       Default uses text-embedding-3-small (1536 dimensions).
        """
        self.model_name = model_name
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.embedding_dimension = 1536  # text-embedding-3-small dimension
    
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
        
        # Generate embeddings using OpenAI API
        response = self.client.embeddings.create(
            model=self.model_name,
            input=texts
        )
        
        # Extract embeddings from response
        embeddings = np.array([item.embedding for item in response.data])
        
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
        
        # Generate single embedding using OpenAI API
        response = self.client.embeddings.create(
            model=self.model_name,
            input=query
        )
        
        embedding = np.array(response.data[0].embedding)
        
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
            "max_sequence_length": 8191,  # text-embedding-3-small max tokens
            "supports_languages": ["Arabic", "English", "Slovak", "100+ others"]
        }