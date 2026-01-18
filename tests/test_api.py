"""API tests for the HRIS system."""
import pytest


class TestHealthEndpoints:
    """Test health check endpoints."""
    
    def test_root(self, client):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "HRIS API"
        assert "version" in data
    
    def test_health(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


class TestEmployeeEndpoints:
    """Test employee CRUD endpoints."""
    
    def test_list_employees_empty(self, client):
        """Test listing employees when empty."""
        response = client.get("/api/v1/employees")
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0
    
    def test_create_employee(self, client, sample_employee):
        """Test creating a new employee."""
        response = client.post("/api/v1/employees", json=sample_employee)
        assert response.status_code == 201
        data = response.json()
        assert data["employee_id"] == "EMP001"
        assert data["first_name"] == "John"
        assert data["email"] == "john.doe@example.com"
    
    def test_create_duplicate_employee_id(self, client, sample_employee):
        """Test that duplicate employee IDs are rejected."""
        client.post("/api/v1/employees", json=sample_employee)
        
        sample_employee["email"] = "john2@example.com"
        response = client.post("/api/v1/employees", json=sample_employee)
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]
    
    def test_get_employee(self, client, sample_employee):
        """Test getting a single employee."""
        create_response = client.post("/api/v1/employees", json=sample_employee)
        emp_id = create_response.json()["id"]
        
        response = client.get(f"/api/v1/employees/{emp_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["employee_id"] == "EMP001"
    
    def test_get_employee_not_found(self, client):
        """Test getting non-existent employee."""
        response = client.get("/api/v1/employees/999")
        assert response.status_code == 404
    
    def test_update_employee(self, client, sample_employee):
        """Test updating an employee."""
        create_response = client.post("/api/v1/employees", json=sample_employee)
        emp_id = create_response.json()["id"]
        
        update_data = {"title": "Senior Software Engineer", "salary": 120000}
        response = client.put(f"/api/v1/employees/{emp_id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Senior Software Engineer"
        assert data["salary"] == 120000
    
    def test_delete_employee(self, client, sample_employee):
        """Test deleting an employee."""
        create_response = client.post("/api/v1/employees", json=sample_employee)
        emp_id = create_response.json()["id"]
        
        response = client.delete(f"/api/v1/employees/{emp_id}")
        assert response.status_code == 204
        
        response = client.get(f"/api/v1/employees/{emp_id}")
        assert response.status_code == 404
    
    def test_search_employees(self, client, sample_employee):
        """Test searching employees."""
        for i, name in enumerate(["Alice", "Bob", "Charlie"]):
            emp = sample_employee.copy()
            emp["employee_id"] = f"EMP00{i+1}"
            emp["first_name"] = name
            emp["email"] = f"{name.lower()}@example.com"
            client.post("/api/v1/employees", json=emp)
        
        response = client.get("/api/v1/employees/search?q=Alice")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["first_name"] == "Alice"


class TestTeamEndpoints:
    """Test team CRUD endpoints."""
    
    def test_create_team(self, client, sample_team):
        """Test creating a new team."""
        response = client.post("/api/v1/teams", json=sample_team)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Engineering"
    
    def test_list_teams(self, client, sample_team):
        """Test listing teams."""
        client.post("/api/v1/teams", json=sample_team)
        
        response = client.get("/api/v1/teams")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
    
    def test_add_team_member(self, client, sample_team, sample_employee):
        """Test adding a member to a team."""
        emp_response = client.post("/api/v1/employees", json=sample_employee)
        emp_id = emp_response.json()["id"]
        
        team_response = client.post("/api/v1/teams", json=sample_team)
        team_id = team_response.json()["id"]
        
        response = client.post(
            f"/api/v1/teams/{team_id}/members",
            json={"employee_id": emp_id}
        )
        assert response.status_code == 201


class TestOrgChartEndpoints:
    """Test organizational chart endpoints."""
    
    def test_get_org_chart_empty(self, client):
        """Test getting org chart when empty."""
        response = client.get("/api/v1/org-chart")
        assert response.status_code == 200
        assert response.json() == []
    
    def test_get_org_chart_with_employees(self, client, sample_employee):
        """Test getting org chart with employees."""
        ceo_response = client.post("/api/v1/employees", json=sample_employee)
        ceo_id = ceo_response.json()["id"]
        
        emp_data = sample_employee.copy()
        emp_data["employee_id"] = "EMP002"
        emp_data["first_name"] = "Jane"
        emp_data["email"] = "jane@example.com"
        emp_data["manager_id"] = ceo_id
        client.post("/api/v1/employees", json=emp_data)
        
        response = client.get("/api/v1/org-chart")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert len(data[0]["children"]) == 1


class TestSearchEndpoints:
    """Test search endpoints."""
    
    def test_global_search(self, client, sample_employee, sample_team):
        """Test global search across employees and teams."""
        sample_employee["first_name"] = "Engineering"
        client.post("/api/v1/employees", json=sample_employee)
        client.post("/api/v1/teams", json=sample_team)
        
        response = client.get("/api/v1/search?q=Engineering")
        assert response.status_code == 200
        data = response.json()
        assert data["total_employees"] >= 1
        assert data["total_teams"] >= 1


class TestAuditEndpoints:
    """Test audit log endpoints."""
    
    def test_audit_logs_created_on_employee_create(self, client, sample_employee):
        """Test that audit logs are created when creating employees."""
        client.post("/api/v1/employees", json=sample_employee)
        
        response = client.get("/api/v1/audit")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        assert data["items"][0]["action"] == "create"
