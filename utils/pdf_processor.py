"""PDF processor modul pre extrahovanie textu z UAE legal dokumentov."""

import re
from pathlib import Path
from typing import Dict, List, Optional
import logging

try:
    import PyPDF2
except ImportError:
    try:
        import pypdf as PyPDF2
    except ImportError:
        raise ImportError("Please install pypdf or PyPDF2: pip install pypdf")

from utils.logger import get_logger
from utils.text_processing import clean_arabic_text

logger = get_logger(__name__)


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Načíta PDF súbor a extrahuje text zo všetkých strán.
    
    Args:
        pdf_path: Cesta k PDF súboru
        
    Returns:
        Celý text ako string
        
    Raises:
        FileNotFoundError: Ak súbor neexistuje
        ValueError: Ak PDF je poškodený
    """
    path = Path(pdf_path)
    
    if not path.exists():
        logger.error(f"PDF súbor neexistuje: {pdf_path}")
        raise FileNotFoundError(f"PDF súbor neexistuje: {pdf_path}")
    
    try:
        logger.info(f"Extrahujem text z PDF: {pdf_path}")
        
        with open(path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            total_pages = len(pdf_reader.pages)
            logger.info(f"PDF má {total_pages} strán")
            
            text_parts = []
            for page_num in range(total_pages):
                page = pdf_reader.pages[page_num]
                text = page.extract_text()
                text_parts.append(text)
                
                if (page_num + 1) % 10 == 0:
                    logger.debug(f"Progress: {page_num + 1}/{total_pages} strán")
            
            full_text = "\n\n".join(text_parts)
            logger.info(f"Úspešne extrahovaných {len(full_text)} znakov z {total_pages} strán")
            
            return full_text
            
    except PyPDF2.errors.PdfReadError as e:
        logger.error(f"Poškodený PDF súbor: {pdf_path} - {str(e)}")
        raise ValueError(f"Poškodený PDF súbor: {str(e)}")
    except Exception as e:
        logger.error(f"Chyba pri extrakcii textu: {pdf_path} - {str(e)}")
        raise ValueError(f"Nepodarilo sa extrahovať text: {str(e)}")


def extract_pdf_metadata(pdf_path: str) -> dict:
    """
    Extrahuje metadata z PDF súboru.
    
    Args:
        pdf_path: Cesta k PDF súboru
        
    Returns:
        Dict s: title, author, subject, creation_date, page_count
        
    Raises:
        FileNotFoundError: Ak súbor neexistuje
    """
    path = Path(pdf_path)
    
    if not path.exists():
        logger.error(f"PDF súbor neexistuje: {pdf_path}")
        raise FileNotFoundError(f"PDF súbor neexistuje: {pdf_path}")
    
    try:
        logger.info(f"Extrahujem metadata z PDF: {pdf_path}")
        
        with open(path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            metadata = pdf_reader.metadata if pdf_reader.metadata else {}
            
            result = {
                'title': metadata.get('/Title', ''),
                'author': metadata.get('/Author', ''),
                'subject': metadata.get('/Subject', ''),
                'creation_date': metadata.get('/CreationDate', ''),
                'page_count': len(pdf_reader.pages)
            }
            
            logger.info(f"Metadata extrahované: {result['page_count']} strán, title: {result['title']}")
            
            return result
            
    except Exception as e:
        logger.error(f"Chyba pri extrakcii metadata: {pdf_path} - {str(e)}")
        return {
            'title': '',
            'author': '',
            'subject': '',
            'creation_date': '',
            'page_count': 0,
            'error': str(e)
        }


def extract_structured_content(pdf_path: str) -> dict:
    """
    Rozpozná articles, sections, clauses v právnom dokumente.
    Parsuje číslovanie (Article 1, Section 2, etc).
    
    Args:
        pdf_path: Cesta k PDF súboru
        
    Returns:
        Strukturovaný dict s articles, sections, clauses
    """
    logger.info(f"Extrahujem štruktúrovaný obsah z: {pdf_path}")
    
    try:
        text = extract_text_from_pdf(pdf_path)
        
        # Patterns pre detekciu štruktúry
        article_pattern = r'Article\s+(\d+)[:\.]?\s*([^\n]*)'
        section_pattern = r'Section\s+(\d+)[:\.]?\s*([^\n]*)'
        clause_pattern = r'(?:Clause|Paragraph)\s+(\d+)[:\.]?\s*([^\n]*)'
        
        # Extract articles
        articles = []
        for match in re.finditer(article_pattern, text, re.IGNORECASE):
            articles.append({
                'number': int(match.group(1)),
                'title': match.group(2).strip(),
                'position': match.start()
            })
        
        # Extract sections
        sections = []
        for match in re.finditer(section_pattern, text, re.IGNORECASE):
            sections.append({
                'number': int(match.group(1)),
                'title': match.group(2).strip(),
                'position': match.start()
            })
        
        # Extract clauses
        clauses = []
        for match in re.finditer(clause_pattern, text, re.IGNORECASE):
            clauses.append({
                'number': int(match.group(1)),
                'title': match.group(2).strip(),
                'position': match.start()
            })
        
        result = {
            'articles': articles,
            'sections': sections,
            'clauses': clauses,
            'article_count': len(articles),
            'section_count': len(sections),
            'clause_count': len(clauses)
        }
        
        logger.info(f"Štruktúra rozpoznaná: {len(articles)} článkov, {len(sections)} sekcií, {len(clauses)} klauzúl")
        
        return result
        
    except Exception as e:
        logger.error(f"Chyba pri extrakcii štruktúry: {pdf_path} - {str(e)}")
        return {
            'articles': [],
            'sections': [],
            'clauses': [],
            'article_count': 0,
            'section_count': 0,
            'clause_count': 0,
            'error': str(e)
        }


def process_legal_pdf(pdf_path: str) -> dict:
    """
    Main funkcia kombinujúca všetky extrakcie.
    
    Args:
        pdf_path: Cesta k PDF súboru
        
    Returns:
        Dict s: text, metadata, structured_content, errors
    """
    logger.info(f"Spracovávam legal PDF: {pdf_path}")
    
    result = {
        'text': '',
        'metadata': {},
        'structured_content': {},
        'errors': []
    }
    
    # Extract metadata
    try:
        result['metadata'] = extract_pdf_metadata(pdf_path)
        if 'error' in result['metadata']:
            result['errors'].append(f"Metadata error: {result['metadata']['error']}")
    except Exception as e:
        error_msg = f"Metadata extraction failed: {str(e)}"
        logger.error(error_msg)
        result['errors'].append(error_msg)
    
    # Extract text
    try:
        result['text'] = extract_text_from_pdf(pdf_path)
    except Exception as e:
        error_msg = f"Text extraction failed: {str(e)}"
        logger.error(error_msg)
        result['errors'].append(error_msg)
        return result
    
    # Extract structured content
    try:
        result['structured_content'] = extract_structured_content(pdf_path)
        if 'error' in result['structured_content']:
            result['errors'].append(f"Structure error: {result['structured_content']['error']}")
    except Exception as e:
        error_msg = f"Structure extraction failed: {str(e)}"
        logger.error(error_msg)
        result['errors'].append(error_msg)
    
    if not result['errors']:
        logger.info(f"PDF úspešne spracovaný: {pdf_path}")
    else:
        logger.warning(f"PDF spracovaný s chybami: {len(result['errors'])} errors")
    
    return result