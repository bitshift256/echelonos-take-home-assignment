"""Shared test configuration and fixtures."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import get_db
from app.models import Base

# Create in-memory SQLite database for testing
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Apply the override globally
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def client():
    """Create test client with fresh database for each test."""
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    yield TestClient(app)
    
    # Drop all tables after test
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def sample_employee():
    """Sample employee data for testing."""
    return {
        "employee_id": "EMP001",
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "phone": "+1-555-0001",
        "title": "Software Engineer",
        "department": "Engineering",
        "hire_date": "2024-01-15",
        "salary": 100000,
        "status": "active"
    }


@pytest.fixture
def sample_team():
    """Sample team data for testing."""
    return {
        "name": "Engineering",
        "description": "Engineering team"
    }


def create_test_employee(client, employee_id="EMP001", first_name="John", 
                         last_name="Doe", title="Engineer", department="Engineering",
                         manager_id=None):
    """Helper to create an employee in tests."""
    data = {
        "employee_id": employee_id,
        "first_name": first_name,
        "last_name": last_name,
        "email": f"{first_name.lower()}.{last_name.lower()}@example.com",
        "title": title,
        "department": department,
        "hire_date": "2024-01-15",
        "manager_id": manager_id
    }
    response = client.post("/api/v1/employees", json=data)
    return response.json()

