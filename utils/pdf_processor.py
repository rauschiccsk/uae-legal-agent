"""PDF processor for UAE legal documents extraction and processing."""

import fitz  # PyMuPDF
from pathlib import Path
from typing import Dict, Optional
import logging
from datetime import datetime

from utils.text_processing import clean_text, normalize_whitespace
from utils.logger import setup_logger

logger = setup_logger(__name__)


def extract_text_from_pdf(pdf_path: Path) -> str:
    """
    Extract text from PDF file.
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        Extracted text as string
        
    Raises:
        FileNotFoundError: If PDF file doesn't exist
        ValueError: If PDF is corrupted or unreadable
    """
    if not pdf_path.exists():
        logger.error(f"PDF file not found: {pdf_path}")
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    try:
        logger.info(f"Extracting text from PDF: {pdf_path}")
        doc = fitz.open(pdf_path)
        
        text_parts = []
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            text_parts.append(text)
            logger.debug(f"Extracted page {page_num + 1}/{len(doc)}")
        
        doc.close()
        
        full_text = "\n\n".join(text_parts)
        logger.info(f"Successfully extracted {len(full_text)} characters from {len(doc)} pages")
        
        return full_text
        
    except fitz.FileDataError as e:
        logger.error(f"Corrupted PDF file: {pdf_path} - {str(e)}")
        raise ValueError(f"Corrupted or invalid PDF file: {pdf_path}")
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {pdf_path} - {str(e)}")
        raise ValueError(f"Failed to extract text from PDF: {str(e)}")


def get_pdf_metadata(pdf_path: Path) -> Dict:
    """
    Get metadata from PDF file.
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        Dictionary with metadata (pages, title, author, etc.)
    """
    if not pdf_path.exists():
        logger.error(f"PDF file not found: {pdf_path}")
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    try:
        logger.info(f"Extracting metadata from: {pdf_path}")
        doc = fitz.open(pdf_path)
        
        metadata = {
            "filename": pdf_path.name,
            "pages": len(doc),
            "title": doc.metadata.get("title", ""),
            "author": doc.metadata.get("author", ""),
            "subject": doc.metadata.get("subject", ""),
            "creator": doc.metadata.get("creator", ""),
            "producer": doc.metadata.get("producer", ""),
            "creation_date": doc.metadata.get("creationDate", ""),
            "mod_date": doc.metadata.get("modDate", ""),
            "file_size_bytes": pdf_path.stat().st_size,
            "extracted_at": datetime.now().isoformat()
        }
        
        doc.close()
        logger.info(f"Metadata extracted: {metadata['pages']} pages, title: {metadata['title']}")
        
        return metadata
        
    except Exception as e:
        logger.error(f"Error extracting metadata: {pdf_path} - {str(e)}")
        return {
            "filename": pdf_path.name,
            "error": str(e),
            "extracted_at": datetime.now().isoformat()
        }


def process_legal_document(pdf_path: Path) -> Dict:
    """
    Complete processing of legal document PDF.
    Extracts text, cleans it, and gathers metadata.
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        Dictionary with processed text, metadata, and stats
    """
    logger.info(f"Processing legal document: {pdf_path}")
    
    try:
        # Extract metadata
        metadata = get_pdf_metadata(pdf_path)
        
        # Extract text
        raw_text = extract_text_from_pdf(pdf_path)
        
        # Clean text
        cleaned_text = clean_text(raw_text)
        normalized_text = normalize_whitespace(cleaned_text)
        
        # Calculate statistics
        word_count = len(normalized_text.split())
        char_count = len(normalized_text)
        
        result = {
            "metadata": metadata,
            "raw_text": raw_text,
            "processed_text": normalized_text,
            "statistics": {
                "word_count": word_count,
                "char_count": char_count,
                "raw_char_count": len(raw_text)
            },
            "processed_at": datetime.now().isoformat(),
            "status": "success"
        }
        
        logger.info(f"Document processed successfully: {word_count} words, {char_count} chars")
        return result
        
    except Exception as e:
        logger.error(f"Error processing document: {pdf_path} - {str(e)}")
        return {
            "metadata": {"filename": pdf_path.name},
            "error": str(e),
            "status": "failed",
            "processed_at": datetime.now().isoformat()
        }


def save_processed_text(text: str, output_path: Path) -> None:
    """
    Save processed text to file.
    
    Args:
        text: Processed text to save
        output_path: Path where to save the text
    """
    try:
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Saving processed text to: {output_path}")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)
        
        logger.info(f"Text saved successfully: {len(text)} characters")
        
    except Exception as e:
        logger.error(f"Error saving processed text to {output_path}: {str(e)}")
        raise IOError(f"Failed to save processed text: {str(e)}")