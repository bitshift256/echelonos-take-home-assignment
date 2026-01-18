"""Observability middleware for request tracking."""
import time
import uuid
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.observability.logging import get_logger, set_request_id, get_request_id
from app.observability.metrics import metrics

logger = get_logger(__name__)


class ObservabilityMiddleware(BaseHTTPMiddleware):
    """Middleware for request logging and metrics."""
    
    async def dispatch(self, request: Request, call_next):
        # Generate or extract request ID
        request_id = request.headers.get('X-Request-ID', str(uuid.uuid4()))
        set_request_id(request_id)
        
        # Get request details
        method = request.method
        path = request.url.path
        client_ip = request.client.host if request.client else 'unknown'
        
        # Track request timing
        start_time = time.perf_counter()
        
        # Track in-progress requests
        in_progress = metrics.request_in_progress(method, path)
        in_progress.inc()
        
        # Log request start
        logger.info(
            "Request started",
            extra={
                'event': 'request_start',
                'method': method,
                'path': path,
                'client_ip': client_ip,
                'query_params': str(request.query_params)
            }
        )
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate duration
            duration = time.perf_counter() - start_time
            status_code = response.status_code
            
            # Record metrics
            metrics.record_request(method, path, status_code, duration)
            
            # Log request completion
            log_level = 'warning' if status_code >= 400 else 'info'
            getattr(logger, log_level)(
                "Request completed",
                extra={
                    'event': 'request_complete',
                    'method': method,
                    'path': path,
                    'status_code': status_code,
                    'duration_ms': round(duration * 1000, 2),
                    'client_ip': client_ip
                }
            )
            
            # Add request ID to response headers
            response.headers['X-Request-ID'] = request_id
            
            return response
            
        except Exception as e:
            # Calculate duration
            duration = time.perf_counter() - start_time
            
            # Record error metrics
            metrics.record_request(method, path, 500, duration)
            
            # Log error
            logger.error(
                "Request failed",
                extra={
                    'event': 'request_error',
                    'method': method,
                    'path': path,
                    'duration_ms': round(duration * 1000, 2),
                    'error': str(e),
                    'error_type': type(e).__name__
                },
                exc_info=True
            )
            
            raise
            
        finally:
            in_progress.dec()


class DatabaseMetricsMiddleware:
    """Middleware to track database query metrics."""
    
    @staticmethod
    def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        """Called before query execution."""
        context._query_start_time = time.perf_counter()
    
    @staticmethod
    def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        """Called after query execution."""
        duration = time.perf_counter() - context._query_start_time
        
        # Determine operation type
        operation = statement.split()[0].upper() if statement else 'UNKNOWN'
        
        # Try to extract table name
        table = 'unknown'
        statement_upper = statement.upper()
        if 'FROM' in statement_upper:
            parts = statement_upper.split('FROM')
            if len(parts) > 1:
                table = parts[1].split()[0].strip().lower()
        elif 'INTO' in statement_upper:
            parts = statement_upper.split('INTO')
            if len(parts) > 1:
                table = parts[1].split()[0].strip().lower()
        elif 'UPDATE' in statement_upper:
            parts = statement_upper.split('UPDATE')
            if len(parts) > 1:
                table = parts[1].split()[0].strip().lower()
        
        metrics.record_db_query(operation, table, duration)

