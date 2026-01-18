"""Search and audit log tests."""
import pytest


class TestGlobalSearch:
    """Test global search functionality."""
    
    def test_search_empty(self, client):
        """Test search with no data."""
        response = client.get("/api/v1/search?q=test")
        assert response.status_code == 200
        data = response.json()
        assert data["total_employees"] == 0
        assert data["total_teams"] == 0
    
    def test_search_employees_by_name(self, client, sample_employee):
        """Test searching employees by name."""
        client.post("/api/v1/employees", json=sample_employee)
        
        response = client.get("/api/v1/search?q=John")
        assert response.status_code == 200
        data = response.json()
        assert data["total_employees"] == 1
        assert data["employees"][0]["first_name"] == "John"
    
    def test_search_employees_by_email(self, client, sample_employee):
        """Test searching employees by email."""
        client.post("/api/v1/employees", json=sample_employee)
        
        response = client.get("/api/v1/search?q=john.doe")
        assert response.status_code == 200
        assert response.json()["total_employees"] == 1
    
    def test_search_employees_by_title(self, client, sample_employee):
        """Test searching employees by title."""
        sample_employee["title"] = "Senior Software Engineer"
        client.post("/api/v1/employees", json=sample_employee)
        
        response = client.get("/api/v1/search?q=Software")
        assert response.status_code == 200
        assert response.json()["total_employees"] == 1
    
    def test_search_teams_by_name(self, client, sample_team):
        """Test searching teams by name."""
        client.post("/api/v1/teams", json=sample_team)
        
        response = client.get("/api/v1/search?q=Engineering")
        assert response.status_code == 200
        data = response.json()
        assert data["total_teams"] == 1
        assert data["teams"][0]["name"] == "Engineering"
    
    def test_search_only_employees(self, client, sample_employee, sample_team):
        """Test searching only employees."""
        sample_employee["first_name"] = "Engineering"
        client.post("/api/v1/employees", json=sample_employee)
        client.post("/api/v1/teams", json=sample_team)
        
        response = client.get("/api/v1/search?q=Engineering&search_teams=false")
        assert response.status_code == 200
        data = response.json()
        assert data["total_employees"] >= 1
        assert data["total_teams"] == 0
    
    def test_search_only_teams(self, client, sample_team):
        """Test searching only teams."""
        client.post("/api/v1/teams", json=sample_team)
        
        response = client.get("/api/v1/search?q=Engineering&search_employees=false")
        assert response.status_code == 200
        data = response.json()
        assert data["total_employees"] == 0
        assert data["total_teams"] == 1
    
    def test_search_case_insensitive(self, client, sample_employee):
        """Test that search is case insensitive."""
        client.post("/api/v1/employees", json=sample_employee)
        
        for query in ["john", "JOHN", "John", "jOhN"]:
            response = client.get(f"/api/v1/search?q={query}")
            assert response.json()["total_employees"] == 1, f"Failed for query: {query}"


class TestAuditLogs:
    """Test audit log functionality."""
    
    def test_audit_log_on_create(self, client, sample_employee):
        """Test that audit log is created on employee creation."""
        client.post("/api/v1/employees", json=sample_employee)
        
        response = client.get("/api/v1/audit")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        
        create_log = next((l for l in data["items"] if l["action"] == "create"), None)
        assert create_log is not None
        assert create_log["entity_type"] == "employee"
    
    def test_audit_log_on_update(self, client, sample_employee):
        """Test that audit log is created on employee update."""
        response = client.post("/api/v1/employees", json=sample_employee)
        emp_id = response.json()["id"]
        
        client.put(f"/api/v1/employees/{emp_id}", json={"title": "Senior Engineer"})
        
        response = client.get("/api/v1/audit")
        data = response.json()
        
        update_log = next((l for l in data["items"] if l["action"] == "update"), None)
        assert update_log is not None
    
    def test_audit_log_on_delete(self, client, sample_employee):
        """Test that audit log is created on employee deletion."""
        response = client.post("/api/v1/employees", json=sample_employee)
        emp_id = response.json()["id"]
        
        client.delete(f"/api/v1/employees/{emp_id}")
        
        response = client.get("/api/v1/audit")
        data = response.json()
        
        delete_log = next((l for l in data["items"] if l["action"] == "delete"), None)
        assert delete_log is not None
    
    def test_audit_log_filter_by_entity_type(self, client, sample_employee, sample_team):
        """Test filtering audit logs by entity type."""
        client.post("/api/v1/employees", json=sample_employee)
        client.post("/api/v1/teams", json=sample_team)
        
        response = client.get("/api/v1/audit?entity_type=employee")
        assert response.status_code == 200
        for log in response.json()["items"]:
            assert log["entity_type"] == "employee"
    
    def test_audit_log_filter_by_action(self, client, sample_employee):
        """Test filtering audit logs by action."""
        response = client.post("/api/v1/employees", json=sample_employee)
        emp_id = response.json()["id"]
        
        client.put(f"/api/v1/employees/{emp_id}", json={"title": "Senior Engineer"})
        
        response = client.get("/api/v1/audit?action=create")
        assert response.status_code == 200
        for log in response.json()["items"]:
            assert log["action"] == "create"
    
    def test_get_entity_audit_logs(self, client, sample_employee):
        """Test getting audit logs for specific entity."""
        response = client.post("/api/v1/employees", json=sample_employee)
        emp_id = response.json()["id"]
        
        # Make two updates with actual changes
        client.put(f"/api/v1/employees/{emp_id}", json={"title": "Senior Engineer"})
        client.put(f"/api/v1/employees/{emp_id}", json={"title": "Staff Engineer"})
        
        response = client.get(f"/api/v1/audit/entity/employee/{emp_id}")
        assert response.status_code == 200
        logs = response.json()
        
        # Should have 1 create + 2 updates = 3 logs
        assert len(logs) >= 3
        for log in logs:
            assert log["entity_id"] == emp_id
    
    def test_audit_log_pagination(self, client, sample_employee):
        """Test audit log pagination."""
        for i in range(10):
            emp = sample_employee.copy()
            emp["employee_id"] = f"EMP{i:03d}"
            emp["email"] = f"emp{i}@example.com"
            client.post("/api/v1/employees", json=emp)
        
        response = client.get("/api/v1/audit?limit=5")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 5
        assert data["total"] >= 10
