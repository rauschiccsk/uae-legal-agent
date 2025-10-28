"""Unit tests for text_processing module"""
import pytest
from src.text_processing import (
    clean_arabic_text,
    extract_legal_references,
    split_into_chunks,
    remove_special_chars
)


class TestCleanArabicText:
    """Tests for clean_arabic_text function"""
    
    def test_normalize_arabic_characters(self):
        """Test Arabic character normalization"""
        text = "أإآ ؤئ"
        result = clean_arabic_text(text)
        assert "ا" in result
        assert result.count("ا") >= 3
    
    def test_remove_extra_whitespace(self, sample_arabic_text):
        """Test removal of extra whitespace"""
        result = clean_arabic_text(sample_arabic_text)
        assert "  " not in result
        assert "\n" not in result
    
    def test_remove_diacritics(self):
        """Test removal of Arabic diacritics"""
        text = "مَرْحَباً"
        result = clean_arabic_text(text)
        assert "َ" not in result
        assert "ْ" not in result
        assert "مرحبا" in result
    
    def test_empty_text(self):
        """Test handling of empty text"""
        result = clean_arabic_text("")
        assert result == ""
    
    def test_preserve_content(self):
        """Test that actual content is preserved"""
        text = "المادة"
        result = clean_arabic_text(text)
        assert "المادة" in result or "الماده" in result


class TestExtractLegalReferences:
    """Tests for extract_legal_references function"""
    
    def test_extract_article_reference(self, sample_legal_text):
        """Test extraction of article references"""
        result = extract_legal_references(sample_legal_text)
        assert len(result) >= 2
        assert any("10" in ref for ref in result)
        assert any("25" in ref for ref in result)
    
    def test_extract_law_reference(self, sample_legal_text):
        """Test extraction of law number references"""
        result = extract_legal_references(sample_legal_text)
        assert any("5" in ref or "2020" in ref for ref in result)
    
    def test_no_references(self):
        """Test text without legal references"""
        text = "هذا نص عادي بدون مراجع قانونية"
        result = extract_legal_references(text)
        assert isinstance(result, list)
    
    def test_multiple_references(self):
        """Test extraction of multiple references"""
        text = "المادة 1 والمادة 2 والمادة 3 من القانون"
        result = extract_legal_references(text)
        assert len(result) >= 3
    
    def test_empty_text(self):
        """Test extraction from empty text"""
        result = extract_legal_references("")
        assert result == []


class TestSplitIntoChunks:
    """Tests for split_into_chunks function"""
    
    def test_chunk_creation(self, sample_long_text, mock_config):
        """Test creation of text chunks"""
        chunks = split_into_chunks(sample_long_text, mock_config["chunk_size"])
        assert len(chunks) > 1
        assert all(isinstance(chunk, str) for chunk in chunks)
    
    def test_chunk_size_limit(self, sample_long_text, mock_config):
        """Test that chunks respect size limit"""
        chunks = split_into_chunks(sample_long_text, mock_config["chunk_size"])
        assert all(len(chunk) <= mock_config["chunk_size"] * 1.2 for chunk in chunks)
    
    def test_chunk_overlap(self, sample_long_text, mock_config):
        """Test chunk overlap functionality"""
        chunks = split_into_chunks(
            sample_long_text, 
            mock_config["chunk_size"],
            mock_config["chunk_overlap"]
        )
        if len(chunks) > 1:
            assert len(chunks[0]) > mock_config["chunk_overlap"]
    
    def test_short_text(self, mock_config):
        """Test chunking of short text"""
        text = "نص قصير"
        chunks = split_into_chunks(text, mock_config["chunk_size"])
        assert len(chunks) == 1
        assert chunks[0] == text
    
    def test_empty_text(self, mock_config):
        """Test chunking of empty text"""
        chunks = split_into_chunks("", mock_config["chunk_size"])
        assert chunks == [] or chunks == [""]


class TestRemoveSpecialChars:
    """Tests for remove_special_chars function"""
    
    def test_remove_punctuation(self):
        """Test removal of punctuation marks"""
        text = "نص!! مع... علامات؟؟"
        result = remove_special_chars(text)
        assert "!" not in result
        assert "." not in result
        assert "?" not in result
    
    def test_remove_special_symbols(self):
        """Test removal of special symbols"""
        text = "نص @#$% مع رموز"
        result = remove_special_chars(text)
        assert "@" not in result
        assert "#" not in result
        assert "$" not in result
    
    def test_preserve_arabic_text(self):
        """Test that Arabic text is preserved"""
        text = "النص العربي"
        result = remove_special_chars(text)
        assert "النص" in result
        assert "العربي" in result
    
    def test_preserve_numbers(self):
        """Test that numbers are preserved"""
        text = "المادة 123 للقانون"
        result = remove_special_chars(text)
        assert "123" in result
    
    def test_preserve_spaces(self):
        """Test that spaces are preserved"""
        text = "كلمة أخرى"
        result = remove_special_chars(text)
        assert " " in result
    
    def test_empty_text(self):
        """Test handling of empty text"""
        result = remove_special_chars("")
        assert result == ""