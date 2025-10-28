"""Logging systém pre UAE Legal Agent s podporou slovenčiny."""

import logging
import logging.handlers
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict


class JSONFormatter(logging.Formatter):
    """JSON formatter pre structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Formatuje log record do JSON formátu."""
        log_data: Dict[str, Any] = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        if hasattr(record, 'extra_data'):
            log_data['extra'] = record.extra_data
        
        return json.dumps(log_data, ensure_ascii=False)


class UTF8FileHandler(logging.handlers.RotatingFileHandler):
    """File handler s UTF-8 encoding pre slovenčinu."""
    
    def __init__(self, filename: str, maxBytes: int = 10485760, 
                 backupCount: int = 5, encoding: str = 'utf-8'):
        """Inicializuje handler s rotation policy."""
        Path(filename).parent.mkdir(parents=True, exist_ok=True)
        super().__init__(filename, maxBytes=maxBytes, 
                        backupCount=backupCount, encoding=encoding)


def setup_logging(log_dir: str = 'logs', log_level: str = 'INFO',
                 console_output: bool = True) -> None:
    """
    Nastavuje logging systém pre aplikáciu.
    
    Args:
        log_dir: Adresár pre log súbory
        log_level: Úroveň logovania (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        console_output: Či logovať aj do konzoly
    """
    log_level_num = getattr(logging, log_level.upper(), logging.INFO)
    
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level_num)
    root_logger.handlers.clear()
    
    log_file = os.path.join(log_dir, 'uae_legal_agent.log')
    file_handler = UTF8FileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,
        backupCount=5
    )
    file_handler.setLevel(log_level_num)
    file_handler.setFormatter(JSONFormatter())
    root_logger.addHandler(file_handler)
    
    if console_output:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level_num)
        console_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_format)
        root_logger.addHandler(console_handler)
    
    root_logger.info(f'Logging systém inicializovaný: level={log_level}, dir={log_dir}')


def get_logger(name: str) -> logging.Logger:
    """
    Získa logger pre daný modul.
    
    Args:
        name: Názov loggera (zvyčajne __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


class LoggerAdapter(logging.LoggerAdapter):
    """Adapter pre pridanie extra dát do logov."""
    
    def process(self, msg: str, kwargs: Dict[str, Any]) -> tuple:
        """Spracuje správu a pridá extra dáta."""
        if 'extra' in kwargs:
            if not hasattr(kwargs['extra'], 'extra_data'):
                kwargs['extra']['extra_data'] = kwargs['extra']
        return msg, kwargs


def get_logger_with_context(name: str, context: Dict[str, Any]) -> LoggerAdapter:
    """
    Získa logger s kontextovými dátami.
    
    Args:
        name: Názov loggera
        context: Kontextové dáta pre všetky logy
        
    Returns:
        LoggerAdapter s kontextom
    """
    logger = get_logger(name)
    return LoggerAdapter(logger, {'extra_data': context})