#!/usr/bin/env python3
"""Quick search test for simple vector store."""

import sys
from pathlib import Path

# Add project root to path
script_dir = Path(__file__).resolve().parent
project_root = script_dir.parent
sys.path.insert(0, str(project_root))

from utils.vector_store_simple import VectorStore
from utils.embeddings import EmbeddingsClient


def main():
    """Test search functionality."""
    print("Loading vector store...")
    store = VectorStore()
    store.initialize_db()

    stats = store.get_collection_stats()
    print(f"\nStore Stats:")
    print(f"  Documents: {stats['document_count']}")
    print(f"  Embedding Dim: {stats['embedding_dimension']}")
    print(f"  Mode: {stats['mode']}")

    # Test search
    query = "criminal law punishment penalty"
    print(f"\nSearching for: '{query}'")

    embeddings_client = EmbeddingsClient()
    query_emb = embeddings_client.generate_embedding(query)

    results = store.collection.query(
        query_embeddings=[query_emb],
        n_results=5
    )

    print(f"\nTop 5 Results:")
    for i, (doc, meta, dist) in enumerate(zip(
            results['documents'][0],
            results['metadatas'][0],
            results['distances'][0]
    ), 1):
        print(f"\n{i}. {meta['source']} (page {meta['page']})")
        print(f"   Distance: {dist:.4f}")
        print(f"   Text: {doc[:150]}...")


if __name__ == "__main__":
    main()