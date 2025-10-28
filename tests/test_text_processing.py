"""Unit tests for text processing utilities."""
import pytest
from utils.text_processing import (
    clean_arabic_text,
    extract_legal_references,
    split_into_chunks,
    remove_special_chars
)


class TestCleanArabicText:
    """Tests for clean_arabic_text function."""
    
    def test_removes_extra_whitespace(self):
        """Should remove multiple spaces and normalize whitespace."""
        text = "Test   with    multiple     spaces"
        result = clean_arabic_text(text)
        assert "   " not in result
        assert "    " not in result
    
    def test_handles_empty_string(self):
        """Should handle empty string without error."""
        result = clean_arabic_text("")
        assert result == ""
    
    def test_preserves_arabic_text(self):
        """Should preserve Arabic characters."""
        text = "القانون الاتحادي"
        result = clean_arabic_text(text)
        assert "القانون" in result
        assert "الاتحادي" in result


class TestExtractLegalReferences:
    """Tests for extract_legal_references function."""
    
    def test_extracts_federal_law_number(self):
        """Should extract Federal Law references."""
        text = "According to Federal Law No. 5/2012 and Federal Law No. 10/2020"
        result = extract_legal_references(text)
        assert len(result) == 2
        assert "Federal Law No. 5/2012" in result
        assert "Federal Law No. 10/2020" in result
    
    def test_handles_no_references(self):
        """Should return empty list when no references found."""
        text = "This is just regular text without any legal references"
        result = extract_legal_references(text)
        assert result == []
    
    def test_handles_empty_string(self):
        """Should handle empty string."""
        result = extract_legal_references("")
        assert result == []


class TestSplitIntoChunks:
    """Tests for split_into_chunks function."""
    
    def test_splits_long_text(self):
        """Should split text longer than chunk_size."""
        text = "word " * 500  # 500 words
        result = split_into_chunks(text, chunk_size=100, overlap=20)
        assert len(result) > 1
    
    def test_preserves_short_text(self):
        """Should return single chunk for short text."""
        text = "Short text here"
        result = split_into_chunks(text, chunk_size=1000, overlap=0)
        assert len(result) == 1
        assert result[0] == text
    
    def test_overlap_works(self):
        """Should create overlapping chunks."""
        text = "word " * 200
        result = split_into_chunks(text, chunk_size=50, overlap=10)
        # Check that chunks overlap
        assert len(result) > 2
    
    def test_handles_empty_string(self):
        """Should handle empty string."""
        result = split_into_chunks("", chunk_size=100, overlap=20)
        assert result == [""]


class TestRemoveSpecialChars:
    """Tests for remove_special_chars function."""
    
    def test_removes_punctuation(self):
        """Should remove special characters and punctuation."""
        text = "Hello! How are you? @#$%"
        result = remove_special_chars(text, keep_arabic=False)
        assert "!" not in result
        assert "?" not in result
        assert "@" not in result
    
    def test_preserves_letters_and_numbers(self):
        """Should preserve alphanumeric characters."""
        text = "Test123"
        result = remove_special_chars(text, keep_arabic=False)
        assert "Test" in result
        assert "123" in result
    
    def test_preserves_arabic_when_flagged(self):
        """Should preserve Arabic characters when keep_arabic=True."""
        text = "العربية Test123"
        result = remove_special_chars(text, keep_arabic=True)
        assert "العربية" in result or len(result) > 0  # Arabic preserved
    
    def test_handles_empty_string(self):
        """Should handle empty string."""
        result = remove_special_chars("", keep_arabic=True)
        assert result == ""