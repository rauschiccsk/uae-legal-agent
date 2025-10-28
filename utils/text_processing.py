import re
from typing import List


def split_into_chunks(text: str, chunk_size: int = 1000) -> List[str]:
    """Split text into chunks of specified size."""
    chunks = []
    words = text.split()
    current_chunk = []
    current_size = 0
    
    for word in words:
        word_size = len(word) + 1
        if current_size + word_size > chunk_size and current_chunk:
            chunks.append(' '.join(current_chunk))
            current_chunk = [word]
            current_size = word_size
        else:
            current_chunk.append(word)
            current_size += word_size
    
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    return chunks


def remove_special_chars(text: str) -> str:
    """Remove special characters from text."""
    return re.sub(r'[^\w\s\u0600-\u06FF]', '', text)


def clean_arabic_text(text: str) -> str:
    """Normalize Arabic text and remove excessive whitespace."""
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def extract_legal_references(text: str) -> List[str]:
    """Extract legal references from text."""
    pattern = r'(?:Federal\s+)?Law\s+No\.\s+\d+/\d{4}'
    references = re.findall(pattern, text, re.IGNORECASE)
    return list(set(references))