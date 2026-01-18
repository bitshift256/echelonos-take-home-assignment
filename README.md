# HRIS - Human Resource Information System

A production-ready, lightweight Human Resource Information System built with FastAPI, React, and PostgreSQL.

## Features

- **Employee Management** - Full CRUD with search, filter, and pagination
- **Team Management** - Teams, sub-teams, and membership management
- **Organizational Chart** - Interactive hierarchy visualization
- **Data Export** - CSV, Excel, and PDF exports
- **Bulk Import** - Import employees from CSV/Excel files
- **Audit Logging** - Complete change history tracking
- **Observability** - Structured logging, Prometheus metrics, OpenTelemetry tracing

## Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | FastAPI (Python 3.12) |
| Frontend | React 18 + Vite + Tailwind CSS |
| Database | PostgreSQL 16 |
| Containerization | Docker & Docker Compose |

---

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- Git

### 1. Clone and Start

```bash
git clone <repository-url>
cd echelonos-take-home

# Start all services
docker-compose up -d --build
```

### 2. Seed Sample Data (Optional)

```bash
docker-compose exec api python scripts/seed_data.py
```

### 3. Access the Application

| Service | URL |
|---------|-----|
| **Frontend** | http://localhost:3000 |
| **API Docs** | http://localhost:8000/docs |
| **ReDoc** | http://localhost:8000/redoc |
| **Metrics** | http://localhost:8000/metrics |
| **Health** | http://localhost:8000/health |

---

## Running Tests

```bash
# Run all tests (82 tests)
docker-compose exec api pytest tests/ -v

# Run specific test file
docker-compose exec api pytest tests/test_employees.py -v

# Run with coverage
docker-compose exec api pytest tests/ --cov=app --cov-report=term-missing
```

---

## API Endpoints

### Employees

```bash
# List employees (paginated)
curl http://localhost:8000/api/v1/employees

# Get employee by ID
curl http://localhost:8000/api/v1/employees/1

# Create employee
curl -X POST http://localhost:8000/api/v1/employees \
  -H "Content-Type: application/json" \
  -d '{
    "employee_id": "EMP100",
    "first_name": "John",
    "last_name": "Smith",
    "email": "john.smith@company.com",
    "title": "Software Engineer",
    "department": "Engineering",
    "hire_date": "2024-01-15",
    "salary": 95000
  }'

# Update employee
curl -X PUT http://localhost:8000/api/v1/employees/1 \
  -H "Content-Type: application/json" \
  -d '{"title": "Senior Engineer", "salary": 120000}'

# Delete employee
curl -X DELETE http://localhost:8000/api/v1/employees/25

# Search employees
curl "http://localhost:8000/api/v1/employees/search?q=Engineer"

# Filter by department
curl "http://localhost:8000/api/v1/employees?department=Technology"

# Export to CSV/Excel/PDF
curl -o employees.csv http://localhost:8000/api/v1/employees/export/csv
curl -o employees.xlsx http://localhost:8000/api/v1/employees/export/excel
curl -o employees.pdf http://localhost:8000/api/v1/employees/export/pdf
```

### Teams

```bash
# List teams
curl http://localhost:8000/api/v1/teams

# Create team
curl -X POST http://localhost:8000/api/v1/teams \
  -H "Content-Type: application/json" \
  -d '{"name": "DevOps", "description": "Infrastructure team"}'

# Add member to team
curl -X POST http://localhost:8000/api/v1/teams/1/members \
  -H "Content-Type: application/json" \
  -d '{"employee_id": 5}'

# Remove member
curl -X DELETE http://localhost:8000/api/v1/teams/1/members/5
```

### Organization Chart

```bash
# Get full org chart (tree structure)
curl http://localhost:8000/api/v1/org-chart

# Get subtree from specific employee
curl http://localhost:8000/api/v1/org-chart/subtree/5

# Get flat hierarchy
curl http://localhost:8000/api/v1/org-chart/flat

# Export org chart to PDF
curl -o org_chart.pdf http://localhost:8000/api/v1/org-chart/export/pdf
```

### Search & Audit

```bash
# Global search (employees + teams)
curl "http://localhost:8000/api/v1/search?q=Engineering"

# View audit logs
curl http://localhost:8000/api/v1/audit

# Filter audit logs
curl "http://localhost:8000/api/v1/audit?entity_type=employee&action=update"
```

---

## Bulk Import

### CSV Format

Create a CSV file with these headers:

```csv
Employee ID,First Name,Last Name,Email,Phone,Title,Department,Hire Date,Salary,Status,Manager ID
EMP100,John,Smith,john@example.com,+1-555-0001,Engineer,Technology,2024-01-15,100000,active,
```

### Import Commands

```bash
# Import from CSV
curl -X POST http://localhost:8000/api/v1/employees/import/csv \
  -F "file=@employees.csv"

# Import from Excel
curl -X POST http://localhost:8000/api/v1/employees/import/excel \
  -F "file=@employees.xlsx"
```

---

## Observability

### Health Checks

```bash
# Detailed health check
curl http://localhost:8000/health

# Kubernetes readiness probe
curl http://localhost:8000/ready

# Kubernetes liveness probe
curl http://localhost:8000/live
```

### Metrics (Prometheus)

```bash
# View all metrics
curl http://localhost:8000/metrics

# Key metrics:
# - http_requests_total{method, endpoint, status_code}
# - http_request_duration_seconds{method, endpoint}
# - hris_employees_total{status}
# - hris_teams_total
```

### Structured Logging

Logs are JSON formatted with request correlation:

```json
{
  "timestamp": "2026-01-18T13:18:38.412739+00:00",
  "level": "info",
  "message": "Request completed",
  "method": "GET",
  "path": "/api/v1/employees",
  "status_code": 200,
  "duration_ms": 4.33,
  "request_id": "a33039eb-132f-445c-91a7-fe107325ba82"
}
```

### Full Monitoring Stack (Optional)

Enable Prometheus, Grafana, and Jaeger:

```bash
docker-compose -f docker-compose.yml -f docker-compose.monitoring.yml up -d
```

Access monitoring tools:

| Service | URL | Credentials |
|---------|-----|-------------|
| Prometheus | http://localhost:9090 | - |
| Grafana | http://localhost:3001 | admin / admin |
| Jaeger | http://localhost:16686 | - |

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://hris_user:hris_password@db:5432/hris_db` |
| `CORS_ORIGINS` | Allowed CORS origins | `*` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `OTEL_TRACING_ENABLED` | Enable OpenTelemetry tracing | `false` |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | OTLP collector endpoint | - |

---

## Project Structure

```
├── app/
│   ├── main.py                 # FastAPI application
│   ├── models.py               # SQLAlchemy models
│   ├── schemas.py              # Pydantic schemas
│   ├── database.py             # Database configuration
│   ├── routers/                # API endpoints
│   │   ├── employees.py
│   │   ├── teams.py
│   │   ├── org_chart.py
│   │   ├── search.py
│   │   └── audit.py
│   ├── services/               # Business logic
│   │   ├── employee_service.py
│   │   ├── team_service.py
│   │   ├── export_service.py
│   │   └── import_service.py
│   └── observability/          # Logging, metrics, tracing
│       ├── logging.py
│       ├── metrics.py
│       ├── tracing.py
│       └── middleware.py
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── pages/              # Page components
│   │   ├── App.jsx
│   │   └── api.js              # API client
│   ├── Dockerfile
│   └── package.json
├── tests/                      # Test suite (82 tests)
│   ├── conftest.py
│   ├── test_api.py
│   ├── test_employees.py
│   ├── test_teams.py
│   ├── test_org_chart.py
│   └── test_search.py
├── monitoring/                 # Monitoring configs
│   ├── prometheus.yml
│   └── grafana/
├── scripts/
│   └── seed_data.py            # Sample data seeder
├── docker-compose.yml          # Main compose file
├── docker-compose.monitoring.yml
├── Dockerfile
└── requirements.txt
```

---

## Common Commands

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop services
docker-compose down

# Reset database
docker-compose down -v && docker-compose up -d

# Rebuild after code changes
docker-compose up --build -d

# Run tests
docker-compose exec api pytest tests/ -v

# Seed sample data
docker-compose exec api python scripts/seed_data.py

# Access API container shell
docker-compose exec api bash
```

---

## License

MIT License
