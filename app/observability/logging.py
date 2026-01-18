"""Structured logging configuration."""
import logging
import sys
import os
from datetime import datetime, timezone
from pythonjsonlogger import jsonlogger
from contextvars import ContextVar

# Context variable for request correlation
request_id_var: ContextVar[str] = ContextVar('request_id', default='-')


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter with additional fields."""
    
    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)
        
        # Add timestamp in ISO format
        log_record['timestamp'] = datetime.now(timezone.utc).isoformat()
        
        # Add log level
        log_record['level'] = record.levelname.lower()
        
        # Add service name
        log_record['service'] = 'hris-api'
        
        # Add request ID from context
        log_record['request_id'] = request_id_var.get()
        
        # Add source location
        log_record['source'] = {
            'file': record.filename,
            'line': record.lineno,
            'function': record.funcName
        }
        
        # Remove default fields we've replaced
        if 'levelname' in log_record:
            del log_record['levelname']
        if 'asctime' in log_record:
            del log_record['asctime']


def setup_logging(level: str = None):
    """Set up structured JSON logging."""
    log_level = level or os.getenv('LOG_LEVEL', 'INFO')
    
    # Create formatter
    formatter = CustomJsonFormatter(
        '%(timestamp)s %(level)s %(name)s %(message)s'
    )
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Add stdout handler with JSON formatting
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(formatter)
    root_logger.addHandler(stdout_handler)
    
    # Reduce noise from third-party libraries
    logging.getLogger('uvicorn.access').setLevel(logging.WARNING)
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
    
    return root_logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the given name."""
    return logging.getLogger(name)


def set_request_id(request_id: str):
    """Set the request ID in context."""
    request_id_var.set(request_id)


def get_request_id() -> str:
    """Get the current request ID from context."""
    return request_id_var.get()

