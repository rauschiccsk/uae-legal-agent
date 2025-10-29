"""Comprehensive test suite for utils/pdf_processor.py module."""

import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch, mock_open
import pypdf.errors as PyPDF2

from utils.pdf_processor import (
    extract_text_from_pdf,
    extract_pdf_metadata,
    extract_structured_content,
    process_legal_pdf
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def tmp_pdf_path(tmp_path):
    """Create temporary PDF file path."""
    pdf_file = tmp_path / "test_document.pdf"
    return str(pdf_file)


@pytest.fixture
def sample_pdf_path(tmp_path):
    """Create sample PDF file for testing."""
    pdf_file = tmp_path / "sample.pdf"
    pdf_file.write_bytes(b"%PDF-1.4 mock content")
    return str(pdf_file)


@pytest.fixture
def mock_pdf_reader():
    """Create mock PDF reader with pages."""
    reader = MagicMock()
    
    # Mock pages
    page1 = MagicMock()
    page1.extract_text.return_value = "Article 1: First article content"
    
    page2 = MagicMock()
    page2.extract_text.return_value = "Section 2: Second section content"
    
    reader.pages = [page1, page2]
    
    # Mock metadata
    reader.metadata = {
        '/Title': 'UAE Legal Document',
        '/Author': 'UAE Government',
        '/Subject': 'Federal Law',
        '/CreationDate': 'D:20240101120000'
    }
    
    return reader


@pytest.fixture
def mock_arabic_pdf_reader():
    """Create mock PDF reader with Arabic text."""
    reader = MagicMock()
    
    page = MagicMock()
    page.extract_text.return_value = "المادة ١: Article 1 في القانون الاتحادي"
    
    reader.pages = [page]
    reader.metadata = {}
    
    return reader


@pytest.fixture
def mock_empty_pdf_reader():
    """Create mock PDF reader with empty content."""
    reader = MagicMock()
    
    page = MagicMock()
    page.extract_text.return_value = ""
    
    reader.pages = [page]
    reader.metadata = None
    
    return reader


@pytest.fixture
def mock_structured_pdf_reader():
    """Create mock PDF reader with structured legal content."""
    reader = MagicMock()
    
    page = MagicMock()
    page.extract_text.return_value = """
    Article 1: Introduction
    This is the first article.
    
    Section 1: General Provisions
    This is the first section.
    
    Article 2: Definitions
    This article contains definitions.
    
    Clause 1: First clause content
    Paragraph 2: Second paragraph content
    
    Section 2: Implementation
    This is the second section.
    """
    
    reader.pages = [page]
    reader.metadata = {}
    
    return reader


# ============================================================================
# TEST GROUP 1: Basic Text Extraction (4 tests)
# ============================================================================

def test_extract_text_from_pdf_valid(sample_pdf_path, mock_pdf_reader):
    """Test extracting text from valid PDF file."""
    with patch('utils.pdf_processor.PyPDF2.PdfReader', return_value=mock_pdf_reader):
        with patch('builtins.open', mock_open(read_data=b'pdf_content')):
            result = extract_text_from_pdf(sample_pdf_path)
            
            assert isinstance(result, str)
            assert "Article 1" in result
            assert "Section 2" in result
            assert len(result) > 0


def test_extract_text_from_pdf_empty(sample_pdf_path, mock_empty_pdf_reader):
    """Test extracting text from PDF with empty content."""
    with patch('utils.pdf_processor.PyPDF2.PdfReader', return_value=mock_empty_pdf_reader):
        with patch('builtins.open', mock_open(read_data=b'pdf_content')):
            result = extract_text_from_pdf(sample_pdf_path)
            
            assert isinstance(result, str)
            assert result == ""


def test_extract_text_from_pdf_missing_file():
    """Test extraction fails with FileNotFoundError for missing file."""
    non_existent_path = "/path/to/nonexistent/file.pdf"
    
    with pytest.raises(FileNotFoundError) as exc_info:
        extract_text_from_pdf(non_existent_path)
    
    assert "neexistuje" in str(exc_info.value)


def test_extract_text_from_pdf_invalid_format(sample_pdf_path):
    """Test extraction fails with ValueError for corrupted PDF."""
    with patch('utils.pdf_processor.PyPDF2.PdfReader') as mock_reader:
        mock_reader.side_effect = pypdf.errors.PdfReadError("Invalid PDF")
        
        with patch('builtins.open', mock_open(read_data=b'invalid_content')):
            with pytest.raises(ValueError) as exc_info:
                extract_text_from_pdf(sample_pdf_path)
            
            assert "Poškodený" in str(exc_info.value)


# ============================================================================
# TEST GROUP 2: Metadata Extraction (3 tests)
# ============================================================================

def test_extract_pdf_metadata_valid(sample_pdf_path, mock_pdf_reader):
    """Test extracting metadata from valid PDF."""
    with patch('utils.pdf_processor.PyPDF2.PdfReader', return_value=mock_pdf_reader):
        with patch('builtins.open', mock_open(read_data=b'pdf_content')):
            result = extract_pdf_metadata(sample_pdf_path)
            
            assert isinstance(result, dict)
            assert result['title'] == 'UAE Legal Document'
            assert result['author'] == 'UAE Government'
            assert result['subject'] == 'Federal Law'
            assert result['page_count'] == 2
            assert 'error' not in result


def test_extract_pdf_metadata_no_metadata(sample_pdf_path, mock_empty_pdf_reader):
    """Test extracting metadata from PDF with no metadata."""
    with patch('utils.pdf_processor.PyPDF2.PdfReader', return_value=mock_empty_pdf_reader):
        with patch('builtins.open', mock_open(read_data=b'pdf_content')):
            result = extract_pdf_metadata(sample_pdf_path)
            
            assert isinstance(result, dict)
            assert result['title'] == ''
            assert result['author'] == ''
            assert result['subject'] == ''
            assert result['page_count'] == 1


def test_extract_pdf_metadata_missing_file():
    """Test metadata extraction fails for missing file."""
    non_existent_path = "/path/to/nonexistent/file.pdf"
    
    with pytest.raises(FileNotFoundError) as exc_info:
        extract_pdf_metadata(non_existent_path)
    
    assert "neexistuje" in str(exc_info.value)


# ============================================================================
# TEST GROUP 3: Structured Content (4 tests)
# ============================================================================

def test_extract_structured_content_articles(sample_pdf_path, mock_structured_pdf_reader):
    """Test extraction of articles from structured content."""
    with patch('utils.pdf_processor.PyPDF2.PdfReader', return_value=mock_structured_pdf_reader):
        with patch('builtins.open', mock_open(read_data=b'pdf_content')):
            result = extract_structured_content(sample_pdf_path)
            
            assert isinstance(result, dict)
            assert 'articles' in result
            assert result['article_count'] == 2
            assert len(result['articles']) == 2
            assert result['articles'][0]['number'] == 1
            assert result['articles'][0]['title'] == 'Introduction'
            assert result['articles'][1]['number'] == 2


def test_extract_structured_content_sections(sample_pdf_path, mock_structured_pdf_reader):
    """Test extraction of sections from structured content."""
    with patch('utils.pdf_processor.PyPDF2.PdfReader', return_value=mock_structured_pdf_reader):
        with patch('builtins.open', mock_open(read_data=b'pdf_content')):
            result = extract_structured_content(sample_pdf_path)
            
            assert 'sections' in result
            assert result['section_count'] == 2
            assert len(result['sections']) == 2
            assert result['sections'][0]['number'] == 1
            assert result['sections'][0]['title'] == 'General Provisions'


def test_extract_structured_content_numbering(sample_pdf_path, mock_structured_pdf_reader):
    """Test correct numbering extraction for clauses and paragraphs."""
    with patch('utils.pdf_processor.PyPDF2.PdfReader', return_value=mock_structured_pdf_reader):
        with patch('builtins.open', mock_open(read_data=b'pdf_content')):
            result = extract_structured_content(sample_pdf_path)
            
            assert 'clauses' in result
            assert result['clause_count'] == 2
            assert len(result['clauses']) == 2
            # Clause 1
            assert result['clauses'][0]['number'] == 1
            # Paragraph 2
            assert result['clauses'][1]['number'] == 2


def test_extract_structured_content_empty(sample_pdf_path, mock_empty_pdf_reader):
    """Test structured content extraction from empty PDF."""
    with patch('utils.pdf_processor.PyPDF2.PdfReader', return_value=mock_empty_pdf_reader):
        with patch('builtins.open', mock_open(read_data=b'pdf_content')):
            result = extract_structured_content(sample_pdf_path)
            
            assert result['article_count'] == 0
            assert result['section_count'] == 0
            assert result['clause_count'] == 0
            assert len(result['articles']) == 0
            assert len(result['sections']) == 0
            assert len(result['clauses']) == 0


# ============================================================================
# TEST GROUP 4: Integration Tests (3 tests)
# ============================================================================

def test_process_legal_pdf_complete(sample_pdf_path, mock_structured_pdf_reader):
    """Test complete processing of legal PDF with all components."""
    with patch('utils.pdf_processor.PyPDF2.PdfReader', return_value=mock_structured_pdf_reader):
        with patch('builtins.open', mock_open(read_data=b'pdf_content')):
            result = process_legal_pdf(sample_pdf_path)
            
            assert isinstance(result, dict)
            assert 'text' in result
            assert 'metadata' in result
            assert 'structured_content' in result
            assert 'errors' in result
            
            assert len(result['text']) > 0
            assert result['metadata']['page_count'] == 1
            assert result['structured_content']['article_count'] == 2
            assert len(result['errors']) == 0


def test_process_legal_pdf_with_errors(sample_pdf_path):
    """Test processing handles errors gracefully."""
    with patch('utils.pdf_processor.extract_pdf_metadata') as mock_metadata:
        mock_metadata.side_effect = Exception("Metadata error")
        
        with patch('utils.pdf_processor.extract_text_from_pdf') as mock_text:
            mock_text.side_effect = Exception("Text extraction error")
            
            result = process_legal_pdf(sample_pdf_path)
            
            assert isinstance(result, dict)
            assert len(result['errors']) > 0
            assert any('Metadata' in err for err in result['errors'])
            assert any('Text extraction' in err for err in result['errors'])


def test_process_legal_pdf_arabic_text(sample_pdf_path, mock_arabic_pdf_reader):
    """Test processing PDF with Arabic text content."""
    with patch('utils.pdf_processor.PyPDF2.PdfReader', return_value=mock_arabic_pdf_reader):
        with patch('builtins.open', mock_open(read_data=b'pdf_content')):
            result = process_legal_pdf(sample_pdf_path)
            
            assert isinstance(result, dict)
            assert 'المادة' in result['text']
            assert 'Article 1' in result['text']
            assert len(result['errors']) == 0


# ============================================================================
# TEST GROUP 5: Error Handling (3 tests)
# ============================================================================

def test_corrupted_pdf_handling(sample_pdf_path):
    """Test handling of corrupted PDF files."""
    with patch('utils.pdf_processor.PyPDF2.PdfReader') as mock_reader:
        mock_reader.side_effect = pypdf.errors.PdfReadError("Corrupted PDF")
        
        with patch('builtins.open', mock_open(read_data=b'corrupted')):
            with pytest.raises(ValueError) as exc_info:
                extract_text_from_pdf(sample_pdf_path)
            
            assert "Poškodený" in str(exc_info.value)


def test_permission_error_handling(sample_pdf_path):
    """Test handling of permission errors when accessing PDF."""
    with patch('builtins.open') as mock_file:
        mock_file.side_effect = PermissionError("Access denied")
        
        with pytest.raises(ValueError) as exc_info:
            extract_text_from_pdf(sample_pdf_path)
        
        assert "Nepodarilo sa extrahovať" in str(exc_info.value)


def test_invalid_file_type(tmp_path):
    """Test handling of invalid file types (non-PDF)."""
    text_file = tmp_path / "document.txt"
    text_file.write_text("This is not a PDF")
    
    with patch('utils.pdf_processor.PyPDF2.PdfReader') as mock_reader:
        mock_reader.side_effect = pypdf.errors.PdfReadError("Not a PDF")
        
        with pytest.raises(ValueError) as exc_info:
            extract_text_from_pdf(str(text_file))
        
        assert "Poškodený" in str(exc_info.value)


# ============================================================================
# TEST GROUP 6: UTF-8 Support (2 tests)
# ============================================================================

def test_arabic_text_extraction(sample_pdf_path, mock_arabic_pdf_reader):
    """Test extraction of Arabic text with proper UTF-8 encoding."""
    with patch('utils.pdf_processor.PyPDF2.PdfReader', return_value=mock_arabic_pdf_reader):
        with patch('builtins.open', mock_open(read_data=b'pdf_content')):
            result = extract_text_from_pdf(sample_pdf_path)
            
            assert isinstance(result, str)
            assert 'المادة' in result  # Arabic word for "article"
            assert 'القانون' in result  # Arabic word for "law"
            assert 'الاتحادي' in result  # Arabic word for "federal"


def test_mixed_english_arabic(sample_pdf_path, mock_arabic_pdf_reader):
    """Test extraction of mixed English and Arabic text."""
    with patch('utils.pdf_processor.PyPDF2.PdfReader', return_value=mock_arabic_pdf_reader):
        with patch('builtins.open', mock_open(read_data=b'pdf_content')):
            result = extract_text_from_pdf(sample_pdf_path)
            
            # Should contain both English and Arabic
            assert 'Article 1' in result
            assert 'المادة' in result
            
            # Should preserve order and structure
            assert result.find('المادة') < result.find('Article')