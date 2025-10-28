"""Pytest fixtures for UAE Legal Agent tests"""
import pytest
import tempfile
import shutil
from pathlib import Path


@pytest.fixture
def mock_config():
    """Mock configuration for testing"""
    return {
        "chunk_size": 500,
        "chunk_overlap": 50,
        "model_name": "gpt-3.5-turbo",
        "temperature": 0.7,
        "max_tokens": 1000
    }


@pytest.fixture
def temp_dir():
    """Create temporary directory for tests"""
    temp_path = tempfile.mkdtemp()
    yield Path(temp_path)
    shutil.rmtree(temp_path)


@pytest.fixture
def sample_arabic_text():
    """Sample Arabic text for testing"""
    return "المادة ١: هذا نص قانوني   للاختبار.\nالمادة ٢: نص آخر!!"


@pytest.fixture
def sample_legal_text():
    """Sample legal text with references"""
    return "وفقاً للمادة 10 من القانون رقم 5 لسنة 2020 والمادة 25"


@pytest.fixture
def sample_long_text():
    """Sample long text for chunking tests"""
    return " ".join(["كلمة"] * 200)