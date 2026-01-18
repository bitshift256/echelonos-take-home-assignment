"""Prometheus metrics configuration."""
from prometheus_client import Counter, Histogram, Gauge, Info, REGISTRY, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response
import time


class Metrics:
    """Application metrics collection."""
    
    def __init__(self):
        # Request metrics
        self.requests_total = Counter(
            'http_requests_total',
            'Total HTTP requests',
            ['method', 'endpoint', 'status_code']
        )
        
        self.request_duration_seconds = Histogram(
            'http_request_duration_seconds',
            'HTTP request duration in seconds',
            ['method', 'endpoint'],
            buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
        )
        
        self.requests_in_progress = Gauge(
            'http_requests_in_progress',
            'HTTP requests currently in progress',
            ['method', 'endpoint']
        )
        
        # Database metrics
        self.db_queries_total = Counter(
            'db_queries_total',
            'Total database queries',
            ['operation', 'table']
        )
        
        self.db_query_duration_seconds = Histogram(
            'db_query_duration_seconds',
            'Database query duration in seconds',
            ['operation'],
            buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0]
        )
        
        # Business metrics
        self.employees_total = Gauge(
            'hris_employees_total',
            'Total number of employees',
            ['status']
        )
        
        self.teams_total = Gauge(
            'hris_teams_total',
            'Total number of teams'
        )
        
        self.api_operations_total = Counter(
            'hris_api_operations_total',
            'Total API operations by type',
            ['operation', 'entity']
        )
        
        # Application info
        self.app_info = Info(
            'hris_app',
            'HRIS application information'
        )
        self.app_info.info({
            'version': '1.0.0',
            'service': 'hris-api'
        })
    
    def record_request(self, method: str, endpoint: str, status_code: int, duration: float):
        """Record HTTP request metrics."""
        # Normalize endpoint to avoid high cardinality
        normalized_endpoint = self._normalize_endpoint(endpoint)
        
        self.requests_total.labels(
            method=method,
            endpoint=normalized_endpoint,
            status_code=str(status_code)
        ).inc()
        
        self.request_duration_seconds.labels(
            method=method,
            endpoint=normalized_endpoint
        ).observe(duration)
    
    def request_in_progress(self, method: str, endpoint: str):
        """Track request in progress."""
        normalized_endpoint = self._normalize_endpoint(endpoint)
        return self.requests_in_progress.labels(
            method=method,
            endpoint=normalized_endpoint
        )
    
    def record_db_query(self, operation: str, table: str, duration: float):
        """Record database query metrics."""
        self.db_queries_total.labels(operation=operation, table=table).inc()
        self.db_query_duration_seconds.labels(operation=operation).observe(duration)
    
    def record_api_operation(self, operation: str, entity: str):
        """Record API operation."""
        self.api_operations_total.labels(operation=operation, entity=entity).inc()
    
    def update_employee_count(self, active: int, inactive: int, on_leave: int, terminated: int):
        """Update employee count gauges."""
        self.employees_total.labels(status='active').set(active)
        self.employees_total.labels(status='inactive').set(inactive)
        self.employees_total.labels(status='on_leave').set(on_leave)
        self.employees_total.labels(status='terminated').set(terminated)
    
    def update_team_count(self, count: int):
        """Update team count gauge."""
        self.teams_total.set(count)
    
    def _normalize_endpoint(self, endpoint: str) -> str:
        """Normalize endpoint path to reduce cardinality."""
        # Replace numeric IDs with placeholder
        import re
        normalized = re.sub(r'/\d+', '/{id}', endpoint)
        # Remove query string
        normalized = normalized.split('?')[0]
        return normalized


# Global metrics instance
metrics = Metrics()


def setup_metrics(app):
    """Set up metrics endpoint for the FastAPI app."""
    from fastapi import APIRouter
    
    router = APIRouter()
    
    @router.get("/metrics")
    async def get_metrics():
        """Prometheus metrics endpoint."""
        return Response(
            content=generate_latest(REGISTRY),
            media_type=CONTENT_TYPE_LATEST
        )
    
    app.include_router(router)
    return metrics

