import re


def split_into_chunks(text, chunk_size=100):
    """
    Split text into chunks of specified size.
    
    Args:
        text: Input text string
        chunk_size: Maximum size of each chunk
        
    Returns:
        List of text chunks
    """
    if not text:
        return [""]
    
    chunks = []
    for i in range(0, len(text), chunk_size):
        chunks.append(text[i:i + chunk_size])
    return chunks


def remove_special_chars(text, keep_arabic=False):
    """
    Remove special characters and punctuation from text.
    
    Args:
        text: Input text string
        keep_arabic: If True, preserve Arabic characters (U+0600 to U+06FF)
        
    Returns:
        Cleaned text string
    """
    if keep_arabic:
        pattern = r'[^\w\s\u0600-\u06FF]'
    else:
        pattern = r'[^\w\s]'
    
    return re.sub(pattern, '', text)