#!/usr/bin/env python3
"""Deployment script with SIMPLE vector store (no ChromaDB)."""

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
        # Remove old ChromaDB stores
        for path in [Path("vector_store"), Path(".chroma"), Path("data/chroma_db")]:
            if path.exists():
                shutil.rmtree(path)
                logger.info(f"Removed {path}")

        # Remove old simple store
        simple_store_path = Path("data/simple_vector_store")
        if simple_store_path.exists():
            shutil.rmtree(simple_store_path)
            logger.info(f"Removed {simple_store_path}")

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
    """Reindex documents with simple vector store."""
    logger.info("Starting reindex with SIMPLE vector store...")

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
        from utils.vector_store_simple import VectorStore

        pdf_processor = PDFProcessor()
        embeddings_client = EmbeddingsClient()
        vector_store = VectorStore()

        logger.info("Initializing SIMPLE vector store...")
        if not vector_store.initialize_db():
            raise RuntimeError("Vector store init failed")
        logger.info(f"Simple vector store initialized (pure-Python)")

        total_chunks = 0
        start_time = time.time()

        for pdf_path in tqdm(pdf_files, desc="Indexing"):
            try:
                logger.info(f"Processing {pdf_path.name}...")
                chunks = pdf_processor.process_pdf(str(pdf_path))
                logger.info(f"Extracted {len(chunks)} chunks")

                if not chunks:
                    logger.warning(f"No chunks extracted from {pdf_path.name}")
                    continue

                logger.info("Generating embeddings...")
                embeddings = embeddings_client.generate_embeddings(
                    [chunk['text'] for chunk in chunks]
                )
                logger.info(f"Generated {len(embeddings)} embeddings")

                if len(embeddings) != len(chunks):
                    raise ValueError(f"Embedding count mismatch: {len(embeddings)} vs {len(chunks)}")

                doc_name = pdf_path.stem

                # Prepare batch data
                batch_texts = [chunk['text'] for chunk in chunks]
                batch_meta = [{"source": doc_name, "page": chunk.get('page', 0)} for chunk in chunks]
                batch_ids = [str(uuid.uuid4()) for _ in chunks]

                logger.info(f"Writing {len(chunks)} chunks to simple store...")

                # Write to simple store (all at once - no ChromaDB freezing!)
                vector_store.collection.add(
                    documents=batch_texts,
                    embeddings=embeddings,
                    metadatas=batch_meta,
                    ids=batch_ids
                )

                total_chunks += len(chunks)
                logger.info(f"✓ {doc_name}: {len(chunks)} chunks written")

            except Exception as e:
                logger.error(f"Failed {pdf_path.name}: {e}", exc_info=True)
                continue

        # Save store to disk
        logger.info("Saving store to disk...")
        if vector_store.collection.save():
            logger.info("Store saved successfully")
        else:
            logger.warning("Store save failed (but data is in memory)")

        duration = time.time() - start_time
        usage = embeddings_client.get_usage_stats()

        # Get final stats
        stats = vector_store.get_collection_stats()
        logger.info(f"Final store stats: {stats}")

        return {
            "documents": len(pdf_files),
            "total_chunks": total_chunks,
            "total_tokens": usage.get('total_tokens', 0),
            "duration": round(duration, 2),
            "store_stats": stats
        }

    except Exception as e:
        logger.error(f"Reindex failed: {e}", exc_info=True)
        raise


def verify_migration() -> Tuple[bool, str]:
    """Verify migration by searching."""
    try:
        from utils.vector_store_simple import VectorStore
        from utils.embeddings import EmbeddingsClient

        logger.info("Verifying migration...")

        store = VectorStore()
        store.initialize_db()

        if store.collection.count() == 0:
            return False, "Store is empty"

        # Generate query embedding
        embeddings_client = EmbeddingsClient()
        query_text = "federal law UAE"
        query_emb = embeddings_client.generate_embedding(query_text)

        # Search
        results = store.collection.query(
            query_embeddings=[query_emb],
            n_results=3
        )

        if not results['documents'][0]:
            return False, "No search results"

        result_count = len(results['documents'][0])
        print(f"{Fore.GREEN}Verification OK ({result_count} results){Style.RESET_ALL}")

        # Show sample result
        if results['documents'][0]:
            sample = results['documents'][0][0][:100]
            logger.info(f"Sample result: {sample}...")

        return True, "OK"
    except Exception as e:
        logger.error(f"Verification failed: {e}", exc_info=True)
        return False, str(e)


def main():
    """Main deployment."""
    parser = argparse.ArgumentParser()
    parser.add_argument('--force', action='store_true', help='Force reindex')
    parser.add_argument('--dry-run', action='store_true', help='Dry run (no actual processing)')
    args = parser.parse_args()

    try:
        print(f"\n{Fore.CYAN}{'=' * 70}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}OpenAI Embeddings Deployment (SIMPLE Vector Store){Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'=' * 70}{Style.RESET_ALL}\n")

        # Step 1: Environment check
        print(f"{Fore.CYAN}Step 1: Environment check{Style.RESET_ALL}")
        success, msg = check_environment()
        if not success:
            print(f"{Fore.RED}✗ {msg}{Style.RESET_ALL}")
            sys.exit(1)
        print(f"{Fore.GREEN}✓ Environment OK{Style.RESET_ALL}\n")

        # Step 2: OpenAI connection test
        print(f"{Fore.CYAN}Step 2: OpenAI connection test{Style.RESET_ALL}")
        success, info = test_openai_connection()
        if not success:
            print(f"{Fore.RED}✗ OpenAI connection failed{Style.RESET_ALL}")
            sys.exit(1)
        print(f"{Fore.GREEN}✓ OpenAI connected (dim={info['dimension']}){Style.RESET_ALL}\n")

        # Step 3: Cleanup old stores
        if not args.dry_run and args.force:
            print(f"{Fore.CYAN}Step 3: Cleanup old stores{Style.RESET_ALL}")
            cleanup_old_store()
            print()

        # Step 4: Reindex documents
        print(f"{Fore.CYAN}Step 4: Reindex documents{Style.RESET_ALL}")
        result = reindex_documents(dry_run=args.dry_run)

        if args.dry_run:
            print(f"{Fore.YELLOW}Dry run - found {result['count']} documents{Style.RESET_ALL}\n")
        else:
            print(f"\n{Fore.GREEN}✓ Reindex complete:{Style.RESET_ALL}")
            print(f"   Documents: {result.get('documents', 0)}")
            print(f"   Chunks: {result.get('total_chunks', 0)}")
            print(f"   Tokens: {result.get('total_tokens', 0):,}")
            print(f"   Duration: {result.get('duration', 0)}s")

            if 'store_stats' in result:
                stats = result['store_stats']
                print(f"   Store: {stats.get('document_count', 0)} docs, mode={stats.get('mode', 'unknown')}")
            print()

            # Step 5: Verify migration
            print(f"{Fore.CYAN}Step 5: Verify migration{Style.RESET_ALL}")
            success, msg = verify_migration()
            if not success:
                print(f"{Fore.YELLOW}⚠ Verification: {msg}{Style.RESET_ALL}")
            else:
                print(f"{Fore.GREEN}✓ Verification passed{Style.RESET_ALL}")
            print()

        print(f"{Fore.GREEN}{'=' * 70}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}DEPLOYMENT COMPLETE{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{'=' * 70}{Style.RESET_ALL}\n")

    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}✗ Interrupted by user{Style.RESET_ALL}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Fore.RED}✗ Deployment failed: {e}{Style.RESET_ALL}")
        logger.error(f"Deployment failed", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()