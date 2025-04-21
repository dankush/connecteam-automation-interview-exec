"""Structured logging implementation for the automation framework."""
import logging
import os
import sys
import json
from datetime import datetime
from typing import Dict, Any, Optional


class StructuredLogFormatter(logging.Formatter):
    """Custom formatter for structured logging with JSON output."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON with additional context."""
        log_data: Dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "module": record.module,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields from record
        if hasattr(record, "extra"):
            log_data.update(record.extra)
        
        return json.dumps(log_data)


def setup_logger(log_level: str = "INFO", log_file: Optional[str] = None) -> None:
    """
    Set up structured logging for the automation framework.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file, if None logs to stdout only
    """
    # Create logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level))
    
    # Clear existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create console handler with a simpler formatter for readability
    console_handler = logging.StreamHandler(sys.stdout)
    console_format = "%(asctime)s [%(levelname)8s] %(message)s (%(filename)s:%(lineno)s)"
    console_handler.setFormatter(logging.Formatter(console_format))
    root_logger.addHandler(console_handler)
    
    # Create file handler with structured JSON formatter if log_file is specified
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(StructuredLogFormatter())
        root_logger.addHandler(file_handler)
    
    # Log startup information
    logging.info(f"Logging initialized at level {log_level}")


class LogContext:
    """Context manager for adding context to logs."""
    
    def __init__(self, **kwargs: Any):
        """Initialize with context key-value pairs."""
        self.extra = kwargs
        self.previous_factory = logging.getLogRecordFactory()
    
    def __enter__(self) -> "LogContext":
        """Add context to log records."""
        old_factory = self.previous_factory
        
        def record_factory(*args: Any, **kwargs: Any) -> logging.LogRecord:
            record = old_factory(*args, **kwargs)
            record.extra = getattr(record, "extra", {})
            record.extra.update(self.extra)
            return record
        
        logging.setLogRecordFactory(record_factory)
        return self
    
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Restore original log record factory."""
        logging.setLogRecordFactory(self.previous_factory)
