#!/usr/bin/env python3
"""Deployment script with diagnostics - NO EMOJI for Windows console."""

import os
import sys
import shutil
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, Tuple, Optional
import logging
import time
import uuid

from tqdm import tqdm
from colorama import Fore, Style, init
from dotenv import load_dotenv

init(autoreset=True)

script_dir = Path(__file__).resolve().parent
project_root = script_dir.parent
sys.path.insert(0, str(project_root))

load_dotenv()

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "deployment.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def check_environment() -> Tuple[bool, str]:
    """Verify environment variables."""
    logger.info("Checking environment...")

    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key or not openai_key.strip():
        return False, "OPENAI_API_KEY not set"

    claude_key = os.getenv("CLAUDE_API_KEY")
    if not claude_key:
        return False, "CLAUDE_API_KEY not set"

    try:
        from config import settings
        if not hasattr(settings, 'OPENAI_API_KEY'):
            return False, "settings.OPENAI_API_KEY not available"
    except Exception as e:
        return False, f"Config error: {e}"

    return True, "OK"


def cleanup_old_store() -> bool:
    """Clean up old vector stores."""
    logger.info("Cleaning up old stores...")

    try:
        for path in [Path("vector_store"), Path(".chroma"), Path("data/chroma_db")]:
            if path.exists():
                shutil.rmtree(path)
                logger.info(f"Removed {path}")

        print(f"{Fore.YELLOW}Old stores removed{Style.RESET_ALL}")
        return True
    except Exception as e:
        logger.error(f"Cleanup failed: {e}")
        return False


def test_openai_connection() -> Tuple[bool, Dict]:
    """Test OpenAI connection."""
    logger.info("Testing OpenAI...")

    try:
        from utils.embeddings import EmbeddingsClient

        client = EmbeddingsClient(model_name="text-embedding-3-small")
        start_time = time.time()
        result = client.generate_embedding("Test UAE legal document")
        response_time = time.time() - start_time

        if not isinstance(result, list) or len(result) != 1536:
            return False, {"error": "Invalid result"}

        print(f"{Fore.GREEN}OpenAI OK ({response_time:.3f}s){Style.RESET_ALL}")
        return True, {"dimension": 1536, "response_time": round(response_time, 3)}
    except Exception as e:
        print(f"{Fore.RED}OpenAI failed: {e}{Style.RESET_ALL}")
        return False, {"error": str(e)}


def reindex_documents(dry_run: bool = False) -> Dict:
    """Reindex documents with diagnostics."""
    logger.info("Starting reindex...")

    data_path = Path("data/uae_laws")
    if not data_path.exists():
        data_path = Path("data")

    pdf_files = list(data_path.rglob("*.pdf"))
    print(f"\n{Fore.CYAN}Found {len(pdf_files)} documents{Style.RESET_ALL}")

    if dry_run:
        return {"dry_run": True, "count": len(pdf_files)}

    try:
        from utils.pdf_processor import PDFProcessor
        from utils.embeddings import EmbeddingsClient
        from utils.vector_store import VectorStore

        pdf_processor = PDFProcessor()
        embeddings_client = EmbeddingsClient()
        vector_store = VectorStore()

        logger.info("Initializing ChromaDB...")
        if not vector_store.initialize_db():
            raise RuntimeError("ChromaDB init failed")
        logger.info("ChromaDB initialized")

        total_chunks = 0
        start_time = time.time()

        for pdf_path in tqdm(pdf_files, desc="Indexing"):
            try:
                logger.info(f"Processing {pdf_path.name}...")
                chunks = pdf_processor.process_pdf(str(pdf_path))
                logger.info(f"Extracted {len(chunks)} chunks")

                logger.info("Generating embeddings...")
                embeddings = embeddings_client.generate_embeddings(
                    [chunk['text'] for chunk in chunks]
                )
                logger.info(f"Generated {len(embeddings)} embeddings")

                doc_name = pdf_path.stem
                logger.info(f"Testing ChromaDB write for {doc_name}...")

                count = vector_store.collection.count()
                logger.info(f"Collection count before write: {count}")

                logger.info("DIAGNOSTIC: Writing test chunk...")
                test_chunk = chunks[0]
                test_embedding = embeddings[0]
                test_id = str(uuid.uuid4())

                logger.info(f"Text len: {len(test_chunk['text'])}")
                logger.info(f"Embedding type: {type(test_embedding)}, len: {len(test_embedding)}")

                if not isinstance(test_embedding, list):
                    raise TypeError(f"Embedding not list: {type(test_embedding)}")

                if len(test_embedding) != 1536:
                    raise ValueError(f"Wrong dimension: {len(test_embedding)}")

                logger.info("Calling collection.add() for 1 chunk...")
                logger.info(f"ID: {test_id}")
                logger.info(f"Metadata: {{'source': '{doc_name}', 'page': {test_chunk.get('page', 0)}}}")

                vector_store.collection.add(
                    documents=[test_chunk['text']],
                    embeddings=[test_embedding],
                    metadatas=[{"source": doc_name, "page": test_chunk.get('page', 0)}],
                    ids=[test_id]
                )

                logger.info("Single chunk write SUCCESS!")
                total_chunks += 1

                # Continue with rest (mini-batches)
                batch_size = 50
                for i in range(1, len(chunks), batch_size):
                    batch_end = min(i + batch_size, len(chunks))
                    batch_chunks = chunks[i:batch_end]
                    batch_embeddings = embeddings[i:batch_end]

                    batch_texts = [c['text'] for c in batch_chunks]
                    batch_meta = [{"source": doc_name, "page": c.get('page', 0)} for c in batch_chunks]
                    batch_ids = [str(uuid.uuid4()) for _ in batch_chunks]

                    logger.info(f"Writing batch {i}-{batch_end} ({len(batch_chunks)} chunks)...")
                    vector_store.collection.add(
                        documents=batch_texts,
                        embeddings=batch_embeddings,
                        metadatas=batch_meta,
                        ids=batch_ids
                    )
                    total_chunks += len(batch_chunks)
                    logger.info(f"Batch written")

                logger.info(f"Completed {doc_name}: {len(chunks)} chunks")

            except Exception as e:
                logger.error(f"Failed {pdf_path}: {e}", exc_info=True)
                continue

        duration = time.time() - start_time
        usage = embeddings_client.get_usage_stats()

        return {
            "documents": len(pdf_files),
            "total_chunks": total_chunks,
            "total_tokens": usage.get('total_tokens', 0),
            "duration": round(duration, 2)
        }

    except Exception as e:
        logger.error(f"Reindex failed: {e}", exc_info=True)
        raise


def verify_migration() -> Tuple[bool, str]:
    """Verify migration."""
    try:
        from utils.vector_store import VectorStore

        store = VectorStore()
        store.initialize_db()

        results = store.search("federal law UAE", top_k=3)

        if not results:
            return False, "No results"

        print(f"{Fore.GREEN}Verification OK ({len(results)} results){Style.RESET_ALL}")
        return True, "OK"
    except Exception as e:
        return False, str(e)


def main():
    """Main deployment."""
    parser = argparse.ArgumentParser()
    parser.add_argument('--force', action='store_true')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()

    try:
        print(f"\n{Fore.CYAN}{'=' * 70}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}OpenAI Embeddings Deployment{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'=' * 70}{Style.RESET_ALL}\n")

        success, msg = check_environment()
        if not success:
            print(f"{Fore.RED}{msg}{Style.RESET_ALL}")
            sys.exit(1)
        print(f"{Fore.GREEN}Environment OK{Style.RESET_ALL}\n")

        success, _ = test_openai_connection()
        if not success:
            sys.exit(1)
        print()

        if not args.dry_run:
            cleanup_old_store()
            print()

        result = reindex_documents(dry_run=args.dry_run)
        print(f"\n{Fore.GREEN}Reindex complete:{Style.RESET_ALL}")
        print(f"   Chunks: {result.get('total_chunks', 0)}")
        print(f"   Duration: {result.get('duration', 0)}s\n")

        if not args.dry_run:
            success, msg = verify_migration()
            if not success:
                print(f"{Fore.RED}Verification failed: {msg}{Style.RESET_ALL}")

        print(f"{Fore.GREEN}{'=' * 70}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}DEPLOYMENT COMPLETE{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{'=' * 70}{Style.RESET_ALL}\n")

    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Interrupted{Style.RESET_ALL}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Fore.RED}Failed: {e}{Style.RESET_ALL}")
        logger.error(f"Deployment failed", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()