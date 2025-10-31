#!/usr/bin/env python3
"""Interactive legal query tool using RAG + Claude."""

import sys
import os
from pathlib import Path
from typing import List, Dict

from colorama import Fore, Style, init
from dotenv import load_dotenv

# Initialize colorama
init(autoreset=True)

# Add project root to path
script_dir = Path(__file__).resolve().parent
project_root = script_dir.parent
sys.path.insert(0, str(project_root))

# Load environment
load_dotenv()

from utils.vector_store_simple import VectorStore
from utils.embeddings import EmbeddingsClient
from utils.claude_client import ClaudeClient


class LegalQueryAgent:
    """Legal query agent with RAG pipeline."""

    def __init__(self):
        """Initialize agent components."""
        print(f"{Fore.CYAN}Initializing Legal Query Agent...{Style.RESET_ALL}")

        # Load vector store
        print(f"{Fore.YELLOW}Loading vector store...{Style.RESET_ALL}")
        self.vector_store = VectorStore()
        self.vector_store.initialize_db()

        stats = self.vector_store.get_collection_stats()
        print(f"{Fore.GREEN}✓ Loaded {stats['document_count']} legal documents{Style.RESET_ALL}")

        # Initialize clients
        self.embeddings_client = EmbeddingsClient()
        self.claude_client = ClaudeClient()

        print(f"{Fore.GREEN}✓ Agent ready!{Style.RESET_ALL}\n")

    def search_legal_docs(self, query: str, top_k: int = 5) -> List[Dict]:
        """Search for relevant legal documents.

        Args:
            query: Search query
            top_k: Number of results to return

        Returns:
            List of relevant document chunks
        """
        # Generate query embedding
        query_emb = self.embeddings_client.generate_embedding(query)

        # Search vector store
        results = self.vector_store.collection.query(
            query_embeddings=[query_emb],
            n_results=top_k
        )

        # Format results
        formatted = []
        if results['documents'][0]:
            for i in range(len(results['documents'][0])):
                formatted.append({
                    'text': results['documents'][0][i],
                    'source': results['metadatas'][0][i]['source'],
                    'page': results['metadatas'][0][i]['page'],
                    'distance': results['distances'][0][i]
                })

        return formatted

    def format_context(self, search_results: List[Dict]) -> str:
        """Format search results as context for Claude.

        Args:
            search_results: List of search results

        Returns:
            Formatted context string
        """
        context_parts = []

        for i, result in enumerate(search_results, 1):
            context_parts.append(
                f"[Document {i}]\n"
                f"Source: {result['source']}\n"
                f"Page: {result['page']}\n"
                f"Relevance: {1 - result['distance']:.2%}\n"
                f"\n{result['text']}\n"
            )

        return "\n" + "=" * 70 + "\n".join(context_parts)

    def analyze_query(self, query: str, top_k: int = 5) -> Dict:
        """Analyze legal query using RAG pipeline.

        Args:
            query: Legal question
            top_k: Number of documents to retrieve

        Returns:
            Dict with analysis results
        """
        print(f"{Fore.CYAN}Searching legal documents...{Style.RESET_ALL}")

        # 1. Retrieve relevant documents
        search_results = self.search_legal_docs(query, top_k=top_k)

        if not search_results:
            return {
                'error': 'No relevant documents found',
                'query': query
            }

        print(f"{Fore.GREEN}✓ Found {len(search_results)} relevant documents{Style.RESET_ALL}")

        # 2. Format context
        context = self.format_context(search_results)

        # 3. Build Claude prompt
        system_prompt = """You are a legal analysis assistant specializing in UAE law.

Your role:
- Analyze legal questions based on provided UAE legal documents
- Provide clear, accurate legal information
- Cite specific articles and laws
- Explain complex legal concepts simply
- Always state when information is not found in the provided documents

Important:
- Base answers ONLY on the provided legal documents
- If the answer is not in the documents, say so clearly
- Cite specific articles, sections, and page numbers
- Use clear, professional language"""

        user_prompt = f"""Based on the following UAE legal documents, please answer this question:

QUESTION: {query}

RELEVANT LEGAL DOCUMENTS:
{context}

Please provide:
1. Direct answer to the question
2. Relevant articles and laws cited
3. Page references from source documents
4. Any important context or clarifications

If the answer is not in the provided documents, please state that clearly."""

        print(f"{Fore.CYAN}Analyzing with Claude...{Style.RESET_ALL}\n")

        # 4. Get Claude's analysis
        try:
            response = self.claude_client.generate_response(
                prompt=user_prompt,
                system_prompt=system_prompt,
                max_tokens=2000
            )

            return {
                'query': query,
                'search_results': search_results,
                'analysis': response['content'],
                'tokens_used': response.get('usage', {})
            }

        except Exception as e:
            return {
                'error': f'Claude API error: {e}',
                'query': query,
                'search_results': search_results
            }

    def print_results(self, results: Dict) -> None:
        """Print analysis results in formatted way.

        Args:
            results: Analysis results dict
        """
        print(f"\n{Fore.CYAN}{'=' * 70}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}LEGAL ANALYSIS{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'=' * 70}{Style.RESET_ALL}\n")

        if 'error' in results:
            print(f"{Fore.RED}Error: {results['error']}{Style.RESET_ALL}")
            return

        # Print query
        print(f"{Fore.YELLOW}Question:{Style.RESET_ALL}")
        print(f"{results['query']}\n")

        # Print analysis
        print(f"{Fore.YELLOW}Analysis:{Style.RESET_ALL}")
        print(f"{results['analysis']}\n")

        # Print source documents
        print(f"{Fore.YELLOW}Source Documents:{Style.RESET_ALL}")
        for i, doc in enumerate(results['search_results'], 1):
            print(f"{i}. {doc['source']}")
            print(f"   Page {doc['page']}, Relevance: {1 - doc['distance']:.1%}")

        # Print token usage
        if 'tokens_used' in results:
            usage = results['tokens_used']
            print(f"\n{Fore.CYAN}Token Usage:{Style.RESET_ALL}")
            print(f"  Input: {usage.get('input_tokens', 0):,}")
            print(f"  Output: {usage.get('output_tokens', 0):,}")
            print(f"  Total: {usage.get('input_tokens', 0) + usage.get('output_tokens', 0):,}")

        print(f"\n{Fore.CYAN}{'=' * 70}{Style.RESET_ALL}\n")


def interactive_mode(agent: LegalQueryAgent) -> None:
    """Run interactive query mode.

    Args:
        agent: LegalQueryAgent instance
    """
    print(f"{Fore.GREEN}Interactive Legal Query Mode{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Enter your legal questions (or 'quit' to exit){Style.RESET_ALL}\n")

    while True:
        try:
            # Get user query
            query = input(f"{Fore.CYAN}Legal Question > {Style.RESET_ALL}").strip()

            if not query:
                continue

            if query.lower() in ['quit', 'exit', 'q']:
                print(f"\n{Fore.YELLOW}Exiting...{Style.RESET_ALL}")
                break

            # Process query
            print()  # Empty line
            results = agent.analyze_query(query)
            agent.print_results(results)

        except KeyboardInterrupt:
            print(f"\n\n{Fore.YELLOW}Interrupted by user{Style.RESET_ALL}")
            break
        except Exception as e:
            print(f"\n{Fore.RED}Error: {e}{Style.RESET_ALL}\n")


def single_query_mode(agent: LegalQueryAgent, query: str) -> None:
    """Run single query mode.

    Args:
        agent: LegalQueryAgent instance
        query: Query string
    """
    results = agent.analyze_query(query)
    agent.print_results(results)


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description='UAE Legal Query Agent - RAG-powered legal analysis'
    )
    parser.add_argument(
        '-q', '--query',
        type=str,
        help='Single query (non-interactive mode)'
    )
    parser.add_argument(
        '-k', '--top-k',
        type=int,
        default=5,
        help='Number of documents to retrieve (default: 5)'
    )

    args = parser.parse_args()

    try:
        # Initialize agent
        agent = LegalQueryAgent()

        # Run appropriate mode
        if args.query:
            # Single query mode
            single_query_mode(agent, args.query)
        else:
            # Interactive mode
            interactive_mode(agent)

    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}Interrupted by user{Style.RESET_ALL}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Fore.RED}Fatal error: {e}{Style.RESET_ALL}")
        sys.exit(1)


if __name__ == "__main__":
    main()