#!/usr/bin/env python3
"""
Deployment script for migrating to OpenAI embeddings with backup and verification.

This script handles the complete migration process from existing vector store
to OpenAI-based embeddings with comprehensive safety checks and verification.
"""

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

from tqdm import tqdm
from colorama import Fore, Style, init
from dotenv import load_dotenv


# Initialize colorama for colored output
init(autoreset=True)

# Add project root to Python path for imports
script_dir = Path(__file__).resolve().parent
project_root = script_dir.parent
sys.path.insert(0, str(project_root))

# Load environment variables
load_dotenv()

# Setup logging
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
    """
    Verify that all required environment variables are set.
    
    Returns:
        Tuple of (success: bool, message: str)
    """
    logger.info("Checking environment configuration...")
    
    # Check OPENAI_API_KEY
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key or not openai_key.strip():
        error_msg = "OPENAI_API_KEY is not set or empty"
        logger.error(error_msg)
        return False, error_msg
    
    # Check CLAUDE_API_KEY
    claude_key = os.getenv("CLAUDE_API_KEY")
    if not claude_key:
        error_msg = "CLAUDE_API_KEY is not set"
        logger.error(error_msg)
        return False, error_msg
    
    # Check if config.py can be imported
    try:
        from config import settings
        logger.info("config.py imported successfully")
    except ImportError as e:
        error_msg = f"Cannot import config.py: {e}"
        logger.error(error_msg)
        return False, error_msg
    
    # Validate settings.openai_api_key is accessible
    try:
        if not hasattr(settings, 'OPENAI_API_KEY'):
            error_msg = "settings.OPENAI_API_KEY is not available"
            logger.error(error_msg)
            return False, error_msg
    except Exception as e:
        error_msg = f"Error accessing settings: {e}"
        logger.error(error_msg)
        return False, error_msg
    
    logger.info("Environment check passed")
    return True, "OK"


def backup_existing_store(backup_dir: str = None) -> Optional[Path]:
    """
    Create backup of existing vector store.
    
    Args:
        backup_dir: Optional custom backup directory name
        
    Returns:
        Path to backup directory or None if no store exists
    """
    logger.info("Checking for existing vector store...")
    
    vector_store_path = Path("vector_store")
    if not vector_store_path.exists():
        logger.info("No existing vector store found")
        return None
    
    try:
        if backup_dir is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = f"vector_store_backup_{timestamp}"
        
        backup_path = Path(backup_dir)
        logger.info(f"Creating backup: {backup_path}")
        
        shutil.copytree(vector_store_path, backup_path)
        
        print(f"{Fore.GREEN}✅ Backup created: {backup_path}{Style.RESET_ALL}")
        logger.info(f"Backup created successfully: {backup_path}")
        
        return backup_path
        
    except Exception as e:
        logger.error(f"Error creating backup: {e}")
        raise


def cleanup_old_store() -> bool:
    """
    Delete old vector store and ChromaDB directory.
    
    Returns:
        True if cleanup successful, False otherwise
    """
    logger.info("Cleaning up old vector store...")
    
    try:
        # Remove vector_store directory
        vector_store_path = Path("vector_store")
        if vector_store_path.exists():
            shutil.rmtree(vector_store_path)
            logger.info("Removed vector_store directory")
        
        # Remove .chroma directory
        chroma_path = Path(".chroma")
        if chroma_path.exists():
            shutil.rmtree(chroma_path)
            logger.info("Removed .chroma directory")
        
        print(f"{Fore.YELLOW}🗑️  Old vector store removed{Style.RESET_ALL}")
        logger.info("Cleanup completed successfully")
        
        return True
        
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")
        return False


def test_openai_connection() -> Tuple[bool, Dict]:
    """
    Test OpenAI API connection and embedding generation.
    
    Returns:
        Tuple of (success: bool, result_dict: Dict)
    """
    logger.info("Testing OpenAI connection...")
    
    try:
        from utils.embeddings import EmbeddingsClient
        from config import settings
        
        # Create embeddings client
        client = EmbeddingsClient(model_name="text-embedding-3-small")
        
        # Test embedding generation
        test_text = "Test UAE legal document"
        start_time = time.time()
        
        result = client.generate_embedding(test_text)
        
        response_time = time.time() - start_time
        
        # Verify result
        if not isinstance(result, list):
            error_msg = "Result is not a list"
            logger.error(error_msg)
            print(f"{Fore.RED}❌ OpenAI connection test failed: {error_msg}{Style.RESET_ALL}")
            return False, {"error": error_msg}
        
        if len(result) != 1536:
            error_msg = f"Expected dimension 1536, got {len(result)}"
            logger.error(error_msg)
            print(f"{Fore.RED}❌ OpenAI connection test failed: {error_msg}{Style.RESET_ALL}")
            return False, {"error": error_msg}
        
        result_dict = {
            "dimension": len(result),
            "response_time": round(response_time, 3)
        }
        
        print(f"{Fore.GREEN}✅ OpenAI connection test passed{Style.RESET_ALL}")
        print(f"   Dimension: {result_dict['dimension']}")
        print(f"   Response time: {result_dict['response_time']}s")
        logger.info(f"OpenAI connection test passed: {result_dict}")
        
        return True, result_dict
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"OpenAI connection test failed: {error_msg}")
        print(f"{Fore.RED}❌ OpenAI connection test failed: {error_msg}{Style.RESET_ALL}")
        return False, {"error": error_msg}


def reindex_documents(dry_run: bool = False) -> Dict:
    """
    Re-index all documents with OpenAI embeddings.
    
    Args:
        dry_run: If True, only count files without processing
        
    Returns:
        Dictionary with indexing statistics
    """
    logger.info("Starting document reindexing...")
    
    # Find all PDF files
    data_path = Path("data/uae_laws")
    if not data_path.exists():
        data_path = Path("data")
    
    pdf_files = list(data_path.rglob("*.pdf"))
    count = len(pdf_files)
    
    print(f"\n{Fore.CYAN}📚 Found {count} documents to index{Style.RESET_ALL}")
    logger.info(f"Found {count} PDF documents")
    
    if dry_run:
        logger.info("Dry run mode - no processing performed")
        return {
            "dry_run": True,
            "count": count
        }
    
    try:
        from utils.pdf_processor import PDFProcessor
        from utils.embeddings import EmbeddingsClient
        from utils.vector_store import VectorStore
        
        pdf_processor = PDFProcessor()
        embeddings_client = EmbeddingsClient()
        vector_store = VectorStore()
        
        total_tokens = 0
        processed_docs = 0
        start_time = time.time()
        
        # Process each PDF with progress bar
        for pdf_path in tqdm(pdf_files, desc="Indexing documents"):
            try:
                # Extract text from PDF
                chunks = pdf_processor.process_pdf(str(pdf_path))
                
                # Generate embeddings
                embeddings = embeddings_client.generate_embeddings(
                    [chunk['text'] for chunk in chunks]
                )
                
                # Store in vector database
                doc_name = pdf_path.stem
                for chunk, embedding in zip(chunks, embeddings):
                    vector_store.add_document(
                        text=chunk['text'],
                        embedding=embedding,
                        metadata={
                            "source": doc_name,
                            "page": chunk.get('page', 0)
                        }
                    )
                
                # Track usage
                usage_stats = embeddings_client.get_usage_stats()
                total_tokens = usage_stats.get('total_tokens', 0)
                
                processed_docs += 1
                logger.info(f"Processed: {doc_name}")
                
            except Exception as e:
                logger.error(f"Error processing {pdf_path}: {e}")
                continue
        
        duration = time.time() - start_time
        
        # Estimate cost (text-embedding-3-small: $0.00002 per 1K tokens)
        estimated_cost = (total_tokens / 1000) * 0.00002
        
        result = {
            "documents": processed_docs,
            "total_tokens": total_tokens,
            "estimated_cost": round(estimated_cost, 4),
            "duration": round(duration, 2)
        }
        
        logger.info(f"Reindexing completed: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Error during reindexing: {e}")
        raise


def verify_migration() -> Tuple[bool, str]:
    """
    Verify that migration was successful.
    
    Returns:
        Tuple of (success: bool, message: str)
    """
    logger.info("Verifying migration...")
    
    try:
        from utils.vector_store import VectorStore
        
        # Create vector store instance
        store = VectorStore()
        
        # Test query
        test_query = "federal law UAE"
        results = store.search(test_query, top_k=3)
        
        # Verify results
        if not results or len(results) == 0:
            error_msg = "No results returned from test query"
            logger.error(error_msg)
            print(f"{Fore.RED}❌ Verification failed: {error_msg}{Style.RESET_ALL}")
            return False, error_msg
        
        # Check embedding dimension
        first_result = results[0]
        if 'embedding' in first_result:
            dimension = len(first_result['embedding'])
            if dimension != 1536:
                error_msg = f"Incorrect embedding dimension: {dimension}"
                logger.error(error_msg)
                return False, error_msg
        
        # Print verification report
        print(f"\n{Fore.GREEN}✅ Migration verification passed{Style.RESET_ALL}")
        print(f"   Test query: '{test_query}'")
        print(f"   Results found: {len(results)}")
        print(f"   Embedding dimension: 1536")
        
        logger.info("Verification passed successfully")
        return True, "Verification passed"
        
    except Exception as e:
        error_msg = f"Verification error: {e}"
        logger.error(error_msg)
        print(f"{Fore.RED}❌ Verification failed: {error_msg}{Style.RESET_ALL}")
        return False, error_msg


def print_summary(results: Dict):
    """
    Print comprehensive deployment summary.
    
    Args:
        results: Dictionary containing all deployment results
    """
    print("\n" + "="*70)
    print(f"{Fore.CYAN}{Style.BRIGHT}")
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║              DEPLOYMENT SUMMARY                                  ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    print(Style.RESET_ALL)
    
    # Environment check
    env_check = results.get('environment_check', False)
    status = f"{Fore.GREEN}✓{Style.RESET_ALL}" if env_check else f"{Fore.RED}✗{Style.RESET_ALL}"
    print(f"{status} Environment Check")
    
    # Backup
    backup_path = results.get('backup_path')
    if backup_path:
        print(f"{Fore.GREEN}✓{Style.RESET_ALL} Backup Created: {backup_path}")
    else:
        print(f"{Fore.YELLOW}⊘{Style.RESET_ALL} Backup: Not needed (no existing store)")
    
    # OpenAI Connection
    openai_test = results.get('openai_test', {})
    if openai_test.get('success'):
        print(f"{Fore.GREEN}✓{Style.RESET_ALL} OpenAI Connection Test")
        print(f"  → Response time: {openai_test.get('response_time', 'N/A')}s")
    else:
        print(f"{Fore.RED}✗{Style.RESET_ALL} OpenAI Connection Test")
    
    # Cleanup
    cleanup = results.get('cleanup', False)
    status = f"{Fore.GREEN}✓{Style.RESET_ALL}" if cleanup else f"{Fore.RED}✗{Style.RESET_ALL}"
    print(f"{status} Old Store Cleanup")
    
    # Reindexing
    reindex = results.get('reindex', {})
    if reindex and not reindex.get('dry_run'):
        print(f"{Fore.GREEN}✓{Style.RESET_ALL} Document Reindexing")
        print(f"  → Documents processed: {reindex.get('documents', 0)}")
        print(f"  → Total tokens: {reindex.get('total_tokens', 0):,}")
        print(f"  → Estimated cost: ${reindex.get('estimated_cost', 0):.4f}")
        print(f"  → Duration: {reindex.get('duration', 0):.2f}s")
    elif reindex and reindex.get('dry_run'):
        print(f"{Fore.YELLOW}⊘{Style.RESET_ALL} Document Reindexing (DRY RUN)")
        print(f"  → Documents found: {reindex.get('count', 0)}")
    
    # Verification
    verification = results.get('verification', False)
    status = f"{Fore.GREEN}✓{Style.RESET_ALL}" if verification else f"{Fore.RED}✗{Style.RESET_ALL}"
    print(f"{status} Migration Verification")
    
    # Next steps
    print("\n" + "="*70)
    print(f"{Fore.CYAN}{Style.BRIGHT}NEXT STEPS:{Style.RESET_ALL}")
    print("1. Test the system with sample queries")
    print("2. Monitor embedding generation performance")
    print("3. Review logs/deployment.log for details")
    if backup_path:
        print(f"4. Keep backup until verification complete: {backup_path}")
    print("="*70 + "\n")


def main():
    """
    Main deployment workflow.
    """
    parser = argparse.ArgumentParser(
        description="Deploy OpenAI embeddings migration with backup and verification",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Skip confirmation prompts'
    )
    parser.add_argument(
        '--no-backup',
        action='store_true',
        help='Skip backup step'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Test mode - show plan without making changes'
    )
    
    args = parser.parse_args()
    
    results = {}
    
    try:
        # Print header
        print("\n" + "="*70)
        print(f"{Fore.CYAN}{Style.BRIGHT}OpenAI Embeddings Deployment{Style.RESET_ALL}")
        print("="*70 + "\n")
        
        if args.dry_run:
            print(f"{Fore.YELLOW}🔍 DRY RUN MODE - No changes will be made{Style.RESET_ALL}\n")
        
        # Step 1: Check environment
        print(f"{Fore.CYAN}Step 1:{Style.RESET_ALL} Checking environment...")
        success, message = check_environment()
        results['environment_check'] = success
        
        if not success:
            print(f"{Fore.RED}❌ Environment check failed: {message}{Style.RESET_ALL}")
            logger.error("Deployment aborted: Environment check failed")
            sys.exit(1)
        
        print(f"{Fore.GREEN}✅ Environment check passed{Style.RESET_ALL}\n")
        
        # Step 2: Backup (if not skipped)
        if not args.no_backup and not args.dry_run:
            print(f"{Fore.CYAN}Step 2:{Style.RESET_ALL} Creating backup...")
            backup_path = backup_existing_store()
            results['backup_path'] = backup_path
            print()
        else:
            print(f"{Fore.YELLOW}Step 2: Backup skipped{Style.RESET_ALL}\n")
            results['backup_path'] = None
        
        # Step 3: Confirmation (if not forced)
        if not args.force and not args.dry_run:
            print(f"{Fore.YELLOW}⚠️  WARNING: This will delete the existing vector store!{Style.RESET_ALL}")
            response = input("Continue? (yes/no): ")
            if response.lower() != 'yes':
                print("Deployment cancelled by user")
                logger.info("Deployment cancelled by user")
                sys.exit(0)
            print()
        
        # Step 4: Test OpenAI connection
        print(f"{Fore.CYAN}Step 3:{Style.RESET_ALL} Testing OpenAI connection...")
        success, test_result = test_openai_connection()
        results['openai_test'] = {'success': success, **test_result}
        
        if not success:
            print(f"{Fore.RED}❌ OpenAI connection test failed{Style.RESET_ALL}")
            logger.error("Deployment aborted: OpenAI connection test failed")
            sys.exit(1)
        
        print()
        
        # Step 5: Cleanup old store
        if not args.dry_run:
            print(f"{Fore.CYAN}Step 4:{Style.RESET_ALL} Cleaning up old vector store...")
            cleanup_success = cleanup_old_store()
            results['cleanup'] = cleanup_success
            print()
        else:
            print(f"{Fore.YELLOW}Step 4: Cleanup skipped (dry run){Style.RESET_ALL}\n")
        
        # Step 6: Reindex documents
        print(f"{Fore.CYAN}Step 5:{Style.RESET_ALL} Reindexing documents...")
        reindex_result = reindex_documents(dry_run=args.dry_run)
        results['reindex'] = reindex_result
        print()
        
        # Step 7: Verify migration
        if not args.dry_run:
            print(f"{Fore.CYAN}Step 6:{Style.RESET_ALL} Verifying migration...")
            success, message = verify_migration()
            results['verification'] = success
            
            if not success:
                print(f"{Fore.RED}❌ Verification failed: {message}{Style.RESET_ALL}")
                logger.error("Deployment completed with verification failure")
            print()
        else:
            print(f"{Fore.YELLOW}Step 6: Verification skipped (dry run){Style.RESET_ALL}\n")
        
        # Step 8: Print summary
        print_summary(results)
        
        logger.info("Deployment completed successfully")
        sys.exit(0)
        
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Deployment interrupted by user{Style.RESET_ALL}")
        logger.warning("Deployment interrupted by user")
        sys.exit(1)
        
    except Exception as e:
        print(f"\n{Fore.RED}❌ Deployment failed: {e}{Style.RESET_ALL}")
        logger.error(f"Deployment failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()