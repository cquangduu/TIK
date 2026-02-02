"""
================================================================================
DAILY KOREAN — Professional Logging System
================================================================================
Unified logging with file rotation, console colors, and structured output.
================================================================================
"""

import os
import sys
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler

# ==================== CONFIGURATION ====================
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
MAX_LOG_SIZE = 10 * 1024 * 1024  # 10 MB
BACKUP_COUNT = 5


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for console output"""
    
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
        'RESET': '\033[0m',      # Reset
    }
    
    ICONS = {
        'DEBUG': '🔍',
        'INFO': '✅',
        'WARNING': '⚠️',
        'ERROR': '❌',
        'CRITICAL': '💀',
    }
    
    def __init__(self, use_colors: bool = True, use_icons: bool = True):
        super().__init__(LOG_FORMAT, LOG_DATE_FORMAT)
        self.use_colors = use_colors and sys.stdout.isatty()
        self.use_icons = use_icons
        
    def format(self, record):
        # Add icon
        if self.use_icons:
            icon = self.ICONS.get(record.levelname, '')
            record.msg = f"{icon} {record.msg}"
        
        # Add colors
        if self.use_colors:
            color = self.COLORS.get(record.levelname, '')
            reset = self.COLORS['RESET']
            record.levelname = f"{color}{record.levelname}{reset}"
        
        return super().format(record)


class StructuredFormatter(logging.Formatter):
    """JSON-like structured logging for production"""
    
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields if present
        for key in ['user_id', 'video_id', 'platform', 'duration', 'error_code']:
            if hasattr(record, key):
                log_data[key] = getattr(record, key)
        
        import json
        return json.dumps(log_data, ensure_ascii=False)


def setup_logger(
    name: str = "dailykorean",
    level: int = logging.INFO,
    log_file: Optional[str] = None,
    use_colors: bool = True,
    use_rotation: bool = True,
    structured: bool = False,
) -> logging.Logger:
    """
    Set up a professional logger with console and file handlers.
    
    Args:
        name: Logger name
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path (defaults to logs/{name}.log)
        use_colors: Enable colored console output
        use_rotation: Enable log file rotation
        structured: Use JSON structured logging
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    if structured:
        console_handler.setFormatter(StructuredFormatter())
    else:
        console_handler.setFormatter(ColoredFormatter(use_colors=use_colors))
    
    logger.addHandler(console_handler)
    
    # File handler
    if log_file is None:
        log_file = LOG_DIR / f"{name}.log"
    else:
        log_file = Path(log_file)
    
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    if use_rotation:
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=MAX_LOG_SIZE,
            backupCount=BACKUP_COUNT,
            encoding='utf-8'
        )
    else:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
    
    file_handler.setLevel(level)
    
    if structured:
        file_handler.setFormatter(StructuredFormatter())
    else:
        file_handler.setFormatter(logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT))
    
    logger.addHandler(file_handler)
    
    # Daily rotating log for audit trail
    audit_handler = TimedRotatingFileHandler(
        LOG_DIR / f"{name}_audit.log",
        when='midnight',
        interval=1,
        backupCount=30,
        encoding='utf-8'
    )
    audit_handler.setLevel(logging.INFO)
    audit_handler.setFormatter(logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT))
    logger.addHandler(audit_handler)
    
    return logger


# Cached loggers
_loggers: dict = {}


def get_logger(name: str = "dailykorean") -> logging.Logger:
    """Get or create a named logger"""
    if name not in _loggers:
        _loggers[name] = setup_logger(name)
    return _loggers[name]


class LogContext:
    """Context manager for structured logging with extra fields"""
    
    def __init__(self, logger: logging.Logger, **context):
        self.logger = logger
        self.context = context
        self.old_factory = None
        
    def __enter__(self):
        self.old_factory = logging.getLogRecordFactory()
        context = self.context
        
        def record_factory(*args, **kwargs):
            record = self.old_factory(*args, **kwargs)
            for key, value in context.items():
                setattr(record, key, value)
            return record
        
        logging.setLogRecordFactory(record_factory)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        logging.setLogRecordFactory(self.old_factory)


# Performance tracking decorator
def log_execution_time(logger: Optional[logging.Logger] = None):
    """Decorator to log function execution time"""
    import functools
    import time
    
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            _logger = logger or get_logger()
            start = time.perf_counter()
            
            try:
                result = func(*args, **kwargs)
                elapsed = time.perf_counter() - start
                _logger.debug(f"{func.__name__} completed in {elapsed:.3f}s")
                return result
            except Exception as e:
                elapsed = time.perf_counter() - start
                _logger.error(f"{func.__name__} failed after {elapsed:.3f}s: {e}")
                raise
        
        return wrapper
    return decorator
