"""Main FastAPI application entry point."""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import event

from app.database import init_db, engine
from app.routers import employees, teams, org_chart, search, audit
from app.observability.logging import setup_logging, get_logger
from app.observability.metrics import setup_metrics, metrics
from app.observability.tracing import setup_tracing
from app.observability.middleware import ObservabilityMiddleware, DatabaseMetricsMiddleware

# Set up structured logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup/shutdown."""
    # Startup
    logger.info("Starting HRIS API", extra={'event': 'startup'})
    init_db()
    
    # Set up database event listeners for metrics
    event.listen(engine, "before_cursor_execute", DatabaseMetricsMiddleware.before_cursor_execute)
    event.listen(engine, "after_cursor_execute", DatabaseMetricsMiddleware.after_cursor_execute)
    
    logger.info("HRIS API started successfully", extra={'event': 'startup_complete'})
    
    yield
    
    # Shutdown
    logger.info("Shutting down HRIS API", extra={'event': 'shutdown'})


# Create FastAPI application
app = FastAPI(
    title="HRIS API",
    description="""
## Lightweight Human Resource Information System (HRIS)

A production-ready API for managing employee data, teams, and organizational structure.

### Features
- **Employee Management**: CRUD operations for employee records
- **Team Management**: Create teams, assign members and leads
- **Organizational Chart**: Auto-generated from reporting relationships
- **Search**: Search across employees and teams
- **Export**: Export data to CSV, Excel, and PDF formats
- **Bulk Import**: Import employees from CSV or Excel files
- **Audit Logging**: Track all changes to employee and team data

### Observability
- **Metrics**: `/metrics` - Prometheus metrics endpoint
- **Health**: `/health` - Health check with dependency status
- **Structured Logging**: JSON formatted logs with request correlation
""",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Add observability middleware (before CORS)
app.add_middleware(ObservabilityMiddleware)

# Configure CORS
allowed_origins = os.getenv("CORS_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set up metrics endpoint
setup_metrics(app)

# Set up tracing (if enabled)
setup_tracing(app, engine)

# Include routers
app.include_router(employees.router, prefix="/api/v1")
app.include_router(teams.router, prefix="/api/v1")
app.include_router(org_chart.router, prefix="/api/v1")
app.include_router(search.router, prefix="/api/v1")
app.include_router(audit.router, prefix="/api/v1")


@app.get("/", tags=["health"])
def root():
    """Root endpoint - API information."""
    return {
        "name": "HRIS API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "metrics": "/metrics"
    }


@app.get("/health", tags=["health"])
def health_check():
    """
    Health check endpoint with dependency status.
    
    Returns detailed health information including:
    - Overall status
    - Database connectivity
    - System metrics
    """
    from app.database import SessionLocal
    from app.models import Employee, Team
    
    health = {
        "status": "healthy",
        "checks": {
            "database": {"status": "unknown"},
            "api": {"status": "healthy"}
        }
    }
    
    # Check database connectivity
    try:
        db = SessionLocal()
        # Simple query to verify connection
        employee_count = db.query(Employee).count()
        team_count = db.query(Team).count()
        db.close()
        
        health["checks"]["database"] = {
            "status": "healthy",
            "employees": employee_count,
            "teams": team_count
        }
        
        # Update metrics
        metrics.update_team_count(team_count)
        
    except Exception as e:
        logger.error("Database health check failed", extra={
            'event': 'health_check_failed',
            'component': 'database',
            'error': str(e)
        })
        health["status"] = "unhealthy"
        health["checks"]["database"] = {
            "status": "unhealthy",
            "error": str(e)
        }
    
    return health


@app.get("/ready", tags=["health"])
def readiness_check():
    """
    Readiness check for Kubernetes.
    
    Returns 200 if the service is ready to accept traffic.
    """
    from app.database import SessionLocal
    from sqlalchemy import text
    
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        return {"status": "ready"}
    except Exception as e:
        logger.error("Readiness check failed", extra={
            'event': 'readiness_check_failed',
            'error': str(e)
        })
        from fastapi import HTTPException
        raise HTTPException(status_code=503, detail="Service not ready")


@app.get("/live", tags=["health"])
def liveness_check():
    """
    Liveness check for Kubernetes.
    
    Returns 200 if the service is alive.
    """
    return {"status": "alive"}
