"""Text embedding generation using OpenAI API."""

from openai import OpenAI
from typing import List, Optional
from utils.logger import logger
from utils.config import settings


class EmbeddingManager:
    """Manager pre generovanie text embeddings pomocou OpenAI API."""

    def __init__(self, model_name: str = "text-embedding-3-small"):
        """
        Inicializácia embedding managera.

        Args:
            model_name: Názov OpenAI embedding modelu
        """
        self.model_name = model_name
        self._client = None
        logger.info(f"EmbeddingManager inicializovaný s modelom: {self.model_name}")

    @property
    def client(self) -> OpenAI:
        """Lazy loading OpenAI klienta - vytvorí sa pri prvom použití."""
        if self._client is None:
            logger.info("Inicializujem OpenAI klienta")
            self._client = OpenAI(api_key=settings.openai_api_key)
            logger.info("OpenAI klient úspešne inicializovaný")
        return self._client

    def generate_embeddings(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """
        Generuje embeddings pre zoznam textov.

        Args:
            texts: Zoznam textov na embedding
            batch_size: Veľkosť batch pre spracovanie

        Returns:
            Zoznam embedding vektorov (normalizované pre cosine similarity)
        """
        if not texts:
            logger.warning("Prázdny zoznam textov pre embedding")
            return []

        logger.info(f"Generujem embeddings pre {len(texts)} textov (batch_size={batch_size})")

        try:
            all_embeddings = []
            
            # Spracovanie v batch-och
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                
                response = self.client.embeddings.create(
                    model=self.model_name,
                    input=batch
                )
                
                batch_embeddings = [item.embedding for item in response.data]
                all_embeddings.extend(batch_embeddings)
                
                logger.info(f"Spracovaný batch {i//batch_size + 1}/{(len(texts)-1)//batch_size + 1}")

            logger.info(f"Embeddings úspešne vygenerované: {len(all_embeddings)} vektorov")
            return all_embeddings

        except Exception as e:
            logger.error(f"Chyba pri generovaní embeddings: {e}")
            raise

    def generate_query_embedding(self, query: str) -> List[float]:
        """
        Generuje embedding pre search query.

        Args:
            query: Search query text

        Returns:
            Embedding vektor (normalizovaný)
        """
        if not query or not query.strip():
            logger.warning("Prázdny query pre embedding")
            return []

        logger.info(f"Generujem query embedding: '{query[:50]}...'")

        try:
            response = self.client.embeddings.create(
                model=self.model_name,
                input=query
            )
            
            embedding = response.data[0].embedding
            return embedding

        except Exception as e:
            logger.error(f"Chyba pri generovaní query embedding: {e}")
            raise

    def get_embedding_dimension(self) -> int:
        """
        Vráti dimenziu embedding vektora.

        Returns:
            Počet dimenzií (1536 pre text-embedding-3-small)
        """
        return 1536