import pytest
import logging
import os
from pathlib import Path
from unittest.mock import Mock, patch
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.logger import get_logger


@pytest.fixture
def temp_log_dir(tmp_path):
    """Vytvorí dočasný adresár pre log súbory"""
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    return log_dir


@pytest.fixture
def mock_logger(temp_log_dir):
    """Vytvorí izolovaný logger pre každý test"""
    logger_name = f"test_logger_{id(temp_log_dir)}"
    log_file = temp_log_dir / "test.log"
    logger = get_logger(logger_name, str(log_file))
    yield logger
    # Cleanup
    for handler in logger.handlers[:]:
        handler.close()
        logger.removeHandler(handler)


def test_logger_creation(temp_log_dir):
    """Overenie že get_logger() vytvorí logger"""
    log_file = temp_log_dir / "creation_test.log"
    logger = get_logger("test_creation", str(log_file))
    
    assert logger is not None
    assert logger.name == "test_creation"
    assert len(logger.handlers) > 0
    
    # Cleanup
    for handler in logger.handlers[:]:
        handler.close()
        logger.removeHandler(handler)


def test_log_levels(mock_logger, temp_log_dir):
    """Testovanie DEBUG, INFO, WARNING, ERROR"""
    log_file = [h.baseFilename for h in mock_logger.handlers 
                if isinstance(h, logging.FileHandler)][0]
    
    mock_logger.debug("Debug message")
    mock_logger.info("Info message")
    mock_logger.warning("Warning message")
    mock_logger.error("Error message")
    
    # Flush handlers
    for handler in mock_logger.handlers:
        handler.flush()
    
    with open(log_file, 'r', encoding='utf-8') as f:
        content = f.read()
        assert "Debug message" in content or "DEBUG" in content
        assert "Info message" in content
        assert "Warning message" in content
        assert "Error message" in content


def test_file_output(temp_log_dir):
    """Overenie že logy sa zapisujú do súboru"""
    log_file = temp_log_dir / "file_test.log"
    logger = get_logger("test_file", str(log_file))
    
    test_message = "Test file output"
    logger.info(test_message)
    
    # Flush handlers
    for handler in logger.handlers:
        handler.flush()
    
    assert log_file.exists()
    with open(log_file, 'r', encoding='utf-8') as f:
        content = f.read()
        assert test_message in content
    
    # Cleanup
    for handler in logger.handlers[:]:
        handler.close()
        logger.removeHandler(handler)


def test_console_output(temp_log_dir, capsys):
    """Overenie console output"""
    log_file = temp_log_dir / "console_test.log"
    logger = get_logger("test_console", str(log_file))
    
    test_message = "Console test message"
    logger.info(test_message)
    
    captured = capsys.readouterr()
    assert test_message in captured.out or test_message in captured.err
    
    # Cleanup
    for handler in logger.handlers[:]:
        handler.close()
        logger.removeHandler(handler)


def test_utf8_encoding(temp_log_dir):
    """Testovanie slovenských znakov v logoch"""
    log_file = temp_log_dir / "utf8_test.log"
    logger = get_logger("test_utf8", str(log_file))
    
    slovak_message = "Testovacia správa s diakritikou: áéíóúýčďľňŕšťž ÁÉÍÓÚÝČĎĽŇŔŠŤŽ"
    logger.info(slovak_message)
    
    # Flush handlers
    for handler in logger.handlers:
        handler.flush()
    
    with open(log_file, 'r', encoding='utf-8') as f:
        content = f.read()
        assert slovak_message in content
        assert "áéíóúý" in content
        assert "ÁÉÍÓÚÝ" in content
    
    # Cleanup
    for handler in logger.handlers[:]:
        handler.close()
        logger.removeHandler(handler)


def test_rotating_handler(temp_log_dir):
    """Overenie rotation policy"""
    log_file = temp_log_dir / "rotating_test.log"
    logger = get_logger("test_rotating", str(log_file))
    
    # Nájdi RotatingFileHandler
    rotating_handler = None
    for handler in logger.handlers:
        if handler.__class__.__name__ == 'RotatingFileHandler':
            rotating_handler = handler
            break
    
    assert rotating_handler is not None
    assert hasattr(rotating_handler, 'maxBytes')
    assert hasattr(rotating_handler, 'backupCount')
    assert rotating_handler.maxBytes > 0
    assert rotating_handler.backupCount > 0
    
    # Test zápisu veľkého množstva dát
    for i in range(100):
        logger.info(f"Rotating test message {i} " + "x" * 100)
    
    # Cleanup
    for handler in logger.handlers[:]:
        handler.close()
        logger.removeHandler(handler)