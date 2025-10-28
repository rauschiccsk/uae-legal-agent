from typing import List

def split_into_chunks(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """Split text into overlapping chunks for RAG embeddings."""
    if not text:
        return []
    
    chunks = []
    start = 0
    text_length = len(text)
    
    while start < text_length:
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start += chunk_size - overlap
        
        if start >= text_length:
            break
    
    return chunks

def remove_special_chars(text: str, keep_arabic: bool = True) -> str:
    """Remove special characters, optionally keeping Arabic characters."""
    if not text:
        return ""
    
    result = []
    for char in text:
        if char.isalnum() or char.isspace():
            result.append(char)
        elif keep_arabic and '\u0600' <= char <= '\u06FF':
            result.append(char)
    
    return ''.join(result)

def normalize_whitespace(text: str) -> str:
    """Normalize whitespace in text."""
    return ' '.join(text.split())

def count_words(text: str) -> int:
    """Count words in text."""
    return len(text.split())