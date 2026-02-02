"""
================================================================================
DAILY KOREAN CORE — Professional Module Framework
================================================================================
Centralized configuration, logging, and utilities for all modules.
================================================================================
"""

from .config import Config, get_config, reload_config
from .logger import setup_logger, get_logger, log_execution_time, LogContext
from .database import Database, get_db
from .utils import (
    safe_json_load,
    safe_json_save,
    retry_with_backoff,
    validate_file_exists,
    ensure_directory,
    sanitize_filename,
    truncate_text,
    format_duration,
    format_number,
    clean_text,
    RateLimiter,
    ProgressTracker,
)


class Logger:
    """Convenience wrapper for module logging"""
    
    def __init__(self, name: str = "dailykorean"):
        self._logger = get_logger(name)
    
    def debug(self, msg, *args, **kwargs):
        self._logger.debug(msg, *args, **kwargs)
    
    def info(self, msg, *args, **kwargs):
        self._logger.info(msg, *args, **kwargs)
    
    def warning(self, msg, *args, **kwargs):
        self._logger.warning(msg, *args, **kwargs)
    
    def error(self, msg, *args, **kwargs):
        self._logger.error(msg, *args, **kwargs)
    
    def critical(self, msg, *args, **kwargs):
        self._logger.critical(msg, *args, **kwargs)
    
    def exception(self, msg, *args, **kwargs):
        self._logger.exception(msg, *args, **kwargs)
    
    @staticmethod
    def log_execution_time(func):
        """Decorator for timing function execution"""
        return log_execution_time()(func)


__version__ = "2.0.0"
__all__ = [
    # Config
    "Config",
    "get_config",
    "reload_config",
    # Logger
    "Logger",
    "setup_logger",
    "get_logger",
    "log_execution_time",
    "LogContext",
    # Database
    "Database",
    "get_db",
    # Utils
    "safe_json_load",
    "safe_json_save",
    "retry_with_backoff",
    "validate_file_exists",
    "ensure_directory",
    "sanitize_filename",
    "truncate_text",
    "format_duration",
    "format_number",
    "clean_text",
    "RateLimiter",
    "ProgressTracker",
]
