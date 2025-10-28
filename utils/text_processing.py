"""Nástroje pre spracovanie právnych textov."""

import re
from typing import List


def clean_arabic_text(text: str) -> str:
    """
    Normalizácia arabského textu.
    
    Args:
        text: Vstupný arabský text
        
    Returns:
        Normalizovaný text
        
    Raises:
        ValueError: Ak text nie je string
    """
    if not isinstance(text, str):
        raise ValueError("Text musí byť string")
    
    if not text.strip():
        return ""
    
    # Normalizácia Arabic characters
    text = re.sub('[إأآا]', 'ا', text)
    text = re.sub('ى', 'ي', text)
    text = re.sub('ؤ', 'و', text)
    text = re.sub('ئ', 'ي', text)
    text = re.sub('ة', 'ه', text)
    
    # Odstránenie diacritics
    text = re.sub('[\u064B-\u0652]', '', text)
    
    # Normalizácia whitespace
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()


def extract_legal_references(text: str) -> List[str]:
    """
    Detekcia odkazov na zákony v texte.
    
    Args:
        text: Vstupný text s odkazmi na zákony
        
    Returns:
        Zoznam nájdených odkazov
        
    Raises:
        ValueError: Ak text nie je string
    """
    if not isinstance(text, str):
        raise ValueError("Text musí byť string")
    
    if not text.strip():
        return []
    
    references = []
    
    # Federal Law No. X/YYYY
    pattern1 = r'Federal\s+Law\s+No\.\s*(\d+)/(\d{4})'
    matches1 = re.finditer(pattern1, text, re.IGNORECASE)
    references.extend([m.group(0) for m in matches1])
    
    # Law No. X of YYYY
    pattern2 = r'Law\s+No\.\s*(\d+)\s+of\s+(\d{4})'
    matches2 = re.finditer(pattern2, text, re.IGNORECASE)
    references.extend([m.group(0) for m in matches2])
    
    # Article X
    pattern3 = r'Article\s+(\d+)'
    matches3 = re.finditer(pattern3, text, re.IGNORECASE)
    references.extend([m.group(0) for m in matches3])
    
    return list(set(references))


def split_into_chunks(
    text: str,
    chunk_size: int = 1000,
    overlap: int = 200
) -> List[str]:
    """
    Rozdelenie textu na chunky pre RAG embeddings.
    
    Args:
        text: Vstupný text
        chunk_size: Veľkosť chunku v znakoch
        overlap: Prekrytie medzi chunkami
        
    Returns:
        Zoznam chunkov
        
    Raises:
        ValueError: Ak text nie je string alebo neplatné parametre
    """
    if not isinstance(text, str):
        raise ValueError("Text musí byť string")
    
    if chunk_size <= 0:
        raise ValueError("chunk_size musí byť > 0")
    
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap musí byť >= 0 a < chunk_size")
    
    if not text.strip():
        return []
    
    chunks = []
    start = 0
    text_len = len(text)
    
    while start < text_len:
        end = start + chunk_size
        
        if end < text_len:
            # Hľadaj koniec vety
            next_period = text.find('.', end - 100, end + 100)
            if next_period != -1:
                end = next_period + 1
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        start = end - overlap
    
    return chunks


def remove_special_chars(text: str, keep_arabic: bool = True) -> str:
    """
    Odstránenie špeciálnych znakov z textu.
    
    Args:
        text: Vstupný text
        keep_arabic: Ponechať arabské znaky
        
    Returns:
        Vyčistený text
        
    Raises:
        ValueError: Ak text nie je string
    """
    if not isinstance(text, str):
        raise ValueError("Text musí byť string")
    
    if not text.strip():
        return ""
    
    if keep_arabic:
        # Ponechať latinku, arabčinu, čísla, whitespace, základnú interpunkciu
        pattern = r'[^a-zA-Z0-9\u0600-\u06FF\s.,;:!?()\-]'
    else:
        # Ponechať len latinku, čísla, whitespace, základnú interpunkciu
        pattern = r'[^a-zA-Z0-9\s.,;:!?()\-]'
    
    text = re.sub(pattern, '', text)
    
    # Normalizácia whitespace
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()