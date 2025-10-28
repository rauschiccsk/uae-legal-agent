"""Text processing utilities for legal document analysis."""
import re
from typing import List


def clean_arabic_text(text: str) -> str:
    """
    Normalizuje arabský text - odstráni prebytočné medzery a whitespace.
    
    Args:
        text: Vstupný text na vyčistenie
        
    Returns:
        Vyčistený text s normalizovanými medzerami
    """
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text


def extract_legal_references(text: str) -> List[str]:
    """
    Extrahuje odkazy na právne predpisy z textu.
    
    Detekuje formáty ako:
    - Federal Law No. 5/2012
    - Law No. 10/2020
    
    Args:
        text: Text na analýzu
        
    Returns:
        Zoznam nájdených právnych odkazov
    """
    if not text:
        return []
    
    # Pattern pre Federal Law No. X/YYYY
    pattern = r'(?:Federal\s+)?Law\s+No\.\s+\d+/\d{4}'
    
    # Find all matches
    matches = re.findall(pattern, text, re.IGNORECASE)
    
    # Remove duplicates while preserving order
    seen = set()
    result = []
    for match in matches:
        if match not in seen:
            seen.add(match)
            result.append(match)
    
    return result


def split_into_chunks(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """
    Rozdelí text na menšie časti (chunks) s prekrytím pre RAG embeddings.
    
    Args:
        text: Text na rozdelenie
        chunk_size: Maximálna veľkosť chunk-u v znakoch
        overlap: Počet znakov prekrytia medzi chunk-ami
        
    Returns:
        Zoznam text chunks
    """
    # Handle empty string - return list with empty string
    if not text:
        return [""]
    
    # If text is shorter than chunk_size, return as single chunk
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        # Get chunk
        end = start + chunk_size
        chunk = text[start:end]
        
        # Try to break at sentence or word boundary if possible
        if end < len(text):
            # Look for last period, exclamation, or question mark
            last_sentence = max(
                chunk.rfind('.'),
                chunk.rfind('!'),
                chunk.rfind('?')
            )
            
            if last_sentence > chunk_size * 0.5:  # At least 50% into chunk
                chunk = chunk[:last_sentence + 1]
                end = start + last_sentence + 1
            else:
                # Look for last space
                last_space = chunk.rfind(' ')
                if last_space > chunk_size * 0.5:
                    chunk = chunk[:last_space]
                    end = start + last_space
        
        chunks.append(chunk.strip())
        
        # Move start position with overlap
        start = end - overlap if end < len(text) else len(text)
    
    return chunks


def remove_special_chars(text: str, keep_arabic: bool = True) -> str:
    """
    Odstráni špeciálne znaky a interpunkciu z textu.
    
    Args:
        text: Text na vyčistenie
        keep_arabic: Ak True, zachová arabské znaky
        
    Returns:
        Text bez špeciálnych znakov
    """
    if not text:
        return ""
    
    if keep_arabic:
        # Keep: letters, numbers, spaces, Arabic characters (U+0600 to U+06FF)
        pattern = r'[^\w\s\u0600-\u06FF]'
    else:
        # Keep only: ASCII letters, numbers, spaces
        pattern = r'[^\w\s]'
    
    # Remove special characters
    cleaned = re.sub(pattern, '', text)
    
    # Normalize whitespace
    cleaned = re.sub(r'\s+', ' ', cleaned)
    
    return cleaned.strip()