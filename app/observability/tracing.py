"""OpenTelemetry tracing configuration."""
import os
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.resources import Resource, SERVICE_NAME, SERVICE_VERSION
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

# Optional OTLP exporter
try:
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    OTLP_AVAILABLE = True
except ImportError:
    OTLP_AVAILABLE = False


def setup_tracing(app, engine=None):
    """Set up OpenTelemetry tracing."""
    # Check if tracing is enabled
    tracing_enabled = os.getenv('OTEL_TRACING_ENABLED', 'false').lower() == 'true'
    
    if not tracing_enabled:
        return None
    
    # Create resource with service info
    resource = Resource.create({
        SERVICE_NAME: os.getenv('OTEL_SERVICE_NAME', 'hris-api'),
        SERVICE_VERSION: '1.0.0',
        'deployment.environment': os.getenv('ENVIRONMENT', 'development')
    })
    
    # Create tracer provider
    provider = TracerProvider(resource=resource)
    
    # Configure exporter based on environment
    otlp_endpoint = os.getenv('OTEL_EXPORTER_OTLP_ENDPOINT')
    
    if otlp_endpoint and OTLP_AVAILABLE:
        # Use OTLP exporter (for Jaeger, Tempo, etc.)
        exporter = OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True)
        provider.add_span_processor(BatchSpanProcessor(exporter))
    else:
        # Use console exporter for development
        if os.getenv('OTEL_CONSOLE_EXPORT', 'false').lower() == 'true':
            provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
    
    # Set the tracer provider
    trace.set_tracer_provider(provider)
    
    # Instrument FastAPI
    FastAPIInstrumentor.instrument_app(app)
    
    # Instrument SQLAlchemy if engine provided
    if engine:
        SQLAlchemyInstrumentor().instrument(engine=engine)
    
    return trace.get_tracer(__name__)


def get_tracer(name: str = __name__):
    """Get a tracer instance."""
    return trace.get_tracer(name)


def create_span(name: str, attributes: dict = None):
    """Create a new span."""
    tracer = get_tracer()
    span = tracer.start_span(name)
    if attributes:
        for key, value in attributes.items():
            span.set_attribute(key, value)
    return span

