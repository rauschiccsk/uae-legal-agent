#!/usr/bin/env python3
"""
UAE Legal Agent CLI - Hlavný entry point
Systém pre prácu s právnymi dokumentami UAE
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

from utils.pdf_processor import PDFProcessor
from utils.embeddings import EmbeddingManager
from utils.vector_store import VectorStore
from utils.claude_client import ClaudeClient


class LegalAgent:
    """Hlavná trieda pre orchestráciu právneho agenta"""
    
    def __init__(self):
        self.pdf_processor = PDFProcessor()
        self.embedding_manager = EmbeddingManager()
        self.vector_store = VectorStore()
        self.claude_client = ClaudeClient()
    
    def import_document(self, pdf_path: str) -> bool:
        """Importuje PDF dokument do systému"""
        try:
            print(f"📄 Načítavam dokument: {pdf_path}")
            
            # Spracovanie PDF
            chunks = self.pdf_processor.process_pdf(pdf_path)
            print(f"✓ Dokument rozdelený na {len(chunks)} častí")
            
            # Generovanie embeddings
            print("🔄 Generujem embeddings...")
            embeddings = self.embedding_manager.generate_embeddings(chunks)
            print(f"✓ Vytvorených {len(embeddings)} embeddings")
            
            # Uloženie do vector store
            doc_name = Path(pdf_path).stem
            self.vector_store.add_documents(doc_name, chunks, embeddings)
            print(f"✓ Dokument '{doc_name}' úspešne importovaný")
            
            return True
            
        except Exception as e:
            print(f"❌ Chyba pri importe: {e}")
            return False
    
    def search_documents(self, query: str, top_k: int = 5) -> None:
        """Vyhľadá relevantné časti dokumentov"""
        try:
            print(f"🔍 Vyhľadávam: {query}")
            
            # Generovanie embedding pre query
            query_embedding = self.embedding_manager.generate_query_embedding(query)
            
            # Vyhľadávanie
            results = self.vector_store.search(query_embedding, top_k=top_k)
            
            if not results:
                print("❌ Nenašli sa žiadne výsledky")
                return
            
            print(f"\n✓ Našlo sa {len(results)} výsledkov:\n")
            
            for i, result in enumerate(results, 1):
                print(f"{'='*60}")
                print(f"Výsledok #{i} (skóre: {result['score']:.3f})")
                print(f"Dokument: {result['document']}")
                print(f"{'='*60}")
                print(result['text'][:300] + "...")
                print()
                
        except Exception as e:
            print(f"❌ Chyba pri vyhľadávaní: {e}")
    
    def analyze_document(self, query: str, context_size: int = 3) -> None:
        """Analyzuje dokumenty s pomocou Claude AI"""
        try:
            print(f"🤖 Analyzujem: {query}\n")
            
            # Získanie relevantného kontextu
            query_embedding = self.embedding_manager.generate_query_embedding(query)
            results = self.vector_store.search(query_embedding, top_k=context_size)
            
            if not results:
                print("❌ Nenašiel sa relevantný kontext")
                return
            
            # Príprava kontextu
            context = "\n\n".join([
                f"[Dokument: {r['document']}]\n{r['text']}"
                for r in results
            ])
            
            # Analýza s Claude
            print("⏳ Claude analyzuje dokumenty...\n")
            response = self.claude_client.analyze_legal_document(query, context)
            
            print("="*60)
            print("ANALÝZA CLAUDE AI")
            print("="*60)
            print(response)
            print("="*60)
            
            # Zobrazenie použitých zdrojov
            print("\n📚 Použité zdroje:")
            for r in results:
                print(f"  - {r['document']} (relevancia: {r['score']:.3f})")
            
        except Exception as e:
            print(f"❌ Chyba pri analýze: {e}")


def main():
    """Hlavná CLI funkcia"""
    
    parser = argparse.ArgumentParser(
        description="UAE Legal Agent - Systém pre analýzu právnych dokumentov",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Dostupné príkazy")
    
    # Import command
    import_parser = subparsers.add_parser(
        "import",
        help="Importovať PDF dokument do systému"
    )
    import_parser.add_argument(
        "pdf_path",
        type=str,
        help="Cesta k PDF dokumentu"
    )
    
    # Search command
    search_parser = subparsers.add_parser(
        "search",
        help="Vyhľadávať v dokumentoch"
    )
    search_parser.add_argument(
        "query",
        type=str,
        help="Vyhľadávací dotaz"
    )
    search_parser.add_argument(
        "-k", "--top-k",
        type=int,
        default=5,
        help="Počet výsledkov (default: 5)"
    )
    
    # Analyze command
    analyze_parser = subparsers.add_parser(
        "analyze",
        help="Analyzovať dokument s Claude AI"
    )
    analyze_parser.add_argument(
        "query",
        type=str,
        help="Otázka alebo téma na analýzu"
    )
    analyze_parser.add_argument(
        "-c", "--context-size",
        type=int,
        default=3,
        help="Počet kontextových častí (default: 3)"
    )
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Inicializácia agenta
    agent = LegalAgent()
    
    # Spustenie príkazu
    if args.command == "import":
        if not Path(args.pdf_path).exists():
            print(f"❌ Súbor neexistuje: {args.pdf_path}")
            sys.exit(1)
        agent.import_document(args.pdf_path)
    
    elif args.command == "search":
        agent.search_documents(args.query, top_k=args.top_k)
    
    elif args.command == "analyze":
        agent.analyze_document(args.query, context_size=args.context_size)


if __name__ == "__main__":
    main()