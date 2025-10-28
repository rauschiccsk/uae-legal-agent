"""Unit testy pre logger modul."""

import pytest
import logging
import json
from pathlib import Path
from utils.logger import (
    setup_logging,
    get_logger,
    get_logger_with_context,
    JSONFormatter,
    UTF8FileHandler
)


@pytest.fixture
def temp_log_dir(tmp_path):
    """Vytvorí dočasný adresár pre logy"""
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    return log_dir


@pytest.fixture
def clean_logging():
    """Vyčistí logging handlers pred a po teste"""
    # Cleanup before test
    root = logging.getLogger()
    for handler in root.handlers[:]:
        handler.close()
        root.removeHandler(handler)
    
    yield
    
    # Cleanup after test
    root = logging.getLogger()
    for handler in root.handlers[:]:
        handler.close()
        root.removeHandler(handler)


def test_logger_creation(temp_log_dir, clean_logging):
    """Test: get_logger() vytvorí logger"""
    setup_logging(log_dir=str(temp_log_dir))
    logger = get_logger("test_module")
    
    assert logger is not None
    assert isinstance(logger, logging.Logger)
    assert logger.name == "test_module"


def test_log_levels(temp_log_dir, clean_logging):
    """Test: Logovania na rôznych úrovniach"""
    setup_logging(log_dir=str(temp_log_dir), log_level='DEBUG')
    logger = get_logger("test_levels")
    
    # Test všetkých úrovní
    logger.debug("Debug správa")
    logger.info("Info správa")
    logger.warning("Warning správa")
    logger.error("Error správa")
    logger.critical("Critical správa")
    
    # Over že súbor obsahuje logy
    log_file = temp_log_dir / "uae_legal_agent.log"
    assert log_file.exists()
    
    content = log_file.read_text(encoding='utf-8')
    assert "Debug správa" in content
    assert "Info správa" in content
    assert "Warning správa" in content


def test_file_output(temp_log_dir, clean_logging):
    """Test: Logy sa zapisujú do súboru"""
    setup_logging(log_dir=str(temp_log_dir))
    logger = get_logger("test_file")
    
    test_message = "Test file output"
    logger.info(test_message)
    
    log_file = temp_log_dir / "uae_legal_agent.log"
    assert log_file.exists()
    
    content = log_file.read_text(encoding='utf-8')
    assert test_message in content


def test_console_output(temp_log_dir, clean_logging, capsys):
    """Test: Logy sa zobrazujú v konzole"""
    setup_logging(log_dir=str(temp_log_dir), console_output=True)
    
    logger = get_logger("test_console")
    logger.info("Console test message")
    
    # Zachyť stdout/stderr output
    captured = capsys.readouterr()
    assert "Console test message" in captured.err


def test_utf8_encoding(temp_log_dir, clean_logging):
    """Test: UTF-8 encoding pre slovenčinu"""
    setup_logging(log_dir=str(temp_log_dir))
    logger = get_logger("test_utf8")
    
    # Slovenské znaky
    test_messages = [
        "Správa s diakritikou: áäčďéíľĺňóôŕšťúýž",
        "VEĽKÉ PÍSMENÁ: ÁÄČĎÉÍĽĹŇÓÔŔŠŤÚÝŽ",
        "Test emoji: ✅ ❌ 🔧"
    ]
    
    for msg in test_messages:
        logger.info(msg)
    
    log_file = temp_log_dir / "uae_legal_agent.log"
    content = log_file.read_text(encoding='utf-8')
    
    for msg in test_messages:
        assert msg in content


def test_rotating_handler(temp_log_dir, clean_logging):
    """Test: RotatingFileHandler rotation policy"""
    setup_logging(log_dir=str(temp_log_dir))
    logger = get_logger("test_rotation")
    
    # Over že handler je RotatingFileHandler
    root = logging.getLogger()
    file_handlers = [h for h in root.handlers if isinstance(h, UTF8FileHandler)]
    
    assert len(file_handlers) > 0
    handler = file_handlers[0]
    
    assert handler.maxBytes == 10 * 1024 * 1024  # 10MB
    assert handler.backupCount == 5


def test_json_formatter():
    """Test: JSONFormatter formátuje logy do JSON"""
    formatter = JSONFormatter()
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="test.py",
        lineno=42,
        msg="Test message",
        args=(),
        exc_info=None
    )
    
    formatted = formatter.format(record)
    log_data = json.loads(formatted)
    
    assert log_data['level'] == 'INFO'
    assert log_data['message'] == 'Test message'
    assert log_data['module'] == 'test'
    assert log_data['line'] == 42
    assert 'timestamp' in log_data


def test_logger_with_context(temp_log_dir, clean_logging):
    """Test: Logger s kontextovými dátami"""
    setup_logging(log_dir=str(temp_log_dir))
    
    context = {
        'user_id': '12345',
        'request_id': 'abc-def-ghi'
    }
    
    logger = get_logger_with_context("test_context", context)
    assert logger is not None
    
    logger.info("Message with context")
    
    log_file = temp_log_dir / "uae_legal_agent.log"
    content = log_file.read_text(encoding='utf-8')
    assert "Message with context" in content