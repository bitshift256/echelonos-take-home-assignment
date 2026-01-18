"""Comprehensive employee tests."""
import pytest


class TestEmployeeValidation:
    """Test employee validation rules."""
    
    def test_create_employee_missing_required_fields(self, client):
        """Test that missing required fields returns 422."""
        response = client.post("/api/v1/employees", json={})
        assert response.status_code == 422
    
    def test_create_employee_invalid_email(self, client, sample_employee):
        """Test that invalid email returns 422."""
        sample_employee["email"] = "invalid-email"
        response = client.post("/api/v1/employees", json=sample_employee)
        assert response.status_code == 422
    
    def test_create_employee_negative_salary(self, client, sample_employee):
        """Test that negative salary returns 422."""
        sample_employee["salary"] = -1000
        response = client.post("/api/v1/employees", json=sample_employee)
        assert response.status_code == 422
    
    def test_create_employee_invalid_status(self, client, sample_employee):
        """Test that invalid status returns 422."""
        sample_employee["status"] = "invalid_status"
        response = client.post("/api/v1/employees", json=sample_employee)
        assert response.status_code == 422
    
    def test_duplicate_email(self, client, sample_employee):
        """Test that duplicate email returns 400."""
        client.post("/api/v1/employees", json=sample_employee)
        sample_employee["employee_id"] = "EMP002"
        response = client.post("/api/v1/employees", json=sample_employee)
        assert response.status_code == 400
        assert "Email already exists" in response.json()["detail"]


class TestEmployeeFiltering:
    """Test employee filtering and pagination."""
    
    def test_filter_by_department(self, client, sample_employee):
        """Test filtering employees by department."""
        client.post("/api/v1/employees", json=sample_employee)
        
        sample_employee["employee_id"] = "EMP002"
        sample_employee["email"] = "jane@example.com"
        sample_employee["department"] = "Marketing"
        client.post("/api/v1/employees", json=sample_employee)
        
        response = client.get("/api/v1/employees?department=Engineering")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["department"] == "Engineering"
    
    def test_filter_by_status(self, client, sample_employee):
        """Test filtering employees by status."""
        client.post("/api/v1/employees", json=sample_employee)
        
        sample_employee["employee_id"] = "EMP002"
        sample_employee["email"] = "jane@example.com"
        sample_employee["status"] = "inactive"
        client.post("/api/v1/employees", json=sample_employee)
        
        response = client.get("/api/v1/employees?status=active")
        assert response.status_code == 200
        assert response.json()["total"] == 1
    
    def test_pagination(self, client, sample_employee):
        """Test employee pagination."""
        for i in range(5):
            emp = sample_employee.copy()
            emp["employee_id"] = f"EMP{i:03d}"
            emp["email"] = f"emp{i}@example.com"
            client.post("/api/v1/employees", json=emp)
        
        response = client.get("/api/v1/employees?limit=2&skip=0")
        data = response.json()
        assert len(data["items"]) == 2
        assert data["total"] == 5
        assert data["total_pages"] == 3


class TestEmployeeHierarchy:
    """Test employee hierarchy and manager relationships."""
    
    def test_assign_manager(self, client, sample_employee):
        """Test assigning a manager to an employee."""
        manager = sample_employee.copy()
        manager_response = client.post("/api/v1/employees", json=manager)
        manager_id = manager_response.json()["id"]
        
        employee = sample_employee.copy()
        employee["employee_id"] = "EMP002"
        employee["email"] = "emp2@example.com"
        employee["manager_id"] = manager_id
        
        response = client.post("/api/v1/employees", json=employee)
        assert response.status_code == 201
        assert response.json()["manager_id"] == manager_id
    
    def test_cannot_be_own_manager(self, client, sample_employee):
        """Test that an employee cannot be their own manager."""
        response = client.post("/api/v1/employees", json=sample_employee)
        emp_id = response.json()["id"]
        
        update_response = client.put(
            f"/api/v1/employees/{emp_id}",
            json={"manager_id": emp_id}
        )
        assert update_response.status_code == 400
        assert "own manager" in update_response.json()["detail"]
    
    def test_invalid_manager_id(self, client, sample_employee):
        """Test that invalid manager ID returns 400."""
        sample_employee["manager_id"] = 9999
        response = client.post("/api/v1/employees", json=sample_employee)
        assert response.status_code == 400
        assert "Manager not found" in response.json()["detail"]
    
    def test_cannot_delete_manager_with_reports(self, client, sample_employee):
        """Test that manager with direct reports cannot be deleted."""
        manager_response = client.post("/api/v1/employees", json=sample_employee)
        manager_id = manager_response.json()["id"]
        
        employee = sample_employee.copy()
        employee["employee_id"] = "EMP002"
        employee["email"] = "emp2@example.com"
        employee["manager_id"] = manager_id
        client.post("/api/v1/employees", json=employee)
        
        response = client.delete(f"/api/v1/employees/{manager_id}")
        assert response.status_code == 400
        assert "direct reports" in response.json()["detail"]
    
    def test_get_direct_reports(self, client, sample_employee):
        """Test getting employee's direct reports."""
        manager_response = client.post("/api/v1/employees", json=sample_employee)
        manager_id = manager_response.json()["id"]
        
        for i in range(2):
            emp = sample_employee.copy()
            emp["employee_id"] = f"EMP{i+2:03d}"
            emp["email"] = f"emp{i+2}@example.com"
            emp["manager_id"] = manager_id
            client.post("/api/v1/employees", json=emp)
        
        response = client.get(f"/api/v1/employees/{manager_id}/reports")
        assert response.status_code == 200
        assert len(response.json()["direct_reports"]) == 2


class TestEmployeeExport:
    """Test employee export functionality."""
    
    def test_export_csv(self, client, sample_employee):
        """Test exporting employees to CSV."""
        client.post("/api/v1/employees", json=sample_employee)
        
        response = client.get("/api/v1/employees/export/csv")
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/csv; charset=utf-8"
        assert "Employee ID" in response.text
        assert "EMP001" in response.text
    
    def test_export_excel(self, client, sample_employee):
        """Test exporting employees to Excel."""
        client.post("/api/v1/employees", json=sample_employee)
        
        response = client.get("/api/v1/employees/export/excel")
        assert response.status_code == 200
        assert "spreadsheetml" in response.headers["content-type"]
    
    def test_export_pdf(self, client, sample_employee):
        """Test exporting employees to PDF."""
        client.post("/api/v1/employees", json=sample_employee)
        
        response = client.get("/api/v1/employees/export/pdf")
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"


class TestDepartments:
    """Test department-related functionality."""
    
    def test_get_departments(self, client, sample_employee):
        """Test getting list of unique departments."""
        departments = ["Engineering", "Marketing", "Sales"]
        for i, dept in enumerate(departments):
            emp = sample_employee.copy()
            emp["employee_id"] = f"EMP{i:03d}"
            emp["email"] = f"emp{i}@example.com"
            emp["department"] = dept
            client.post("/api/v1/employees", json=emp)
        
        response = client.get("/api/v1/employees/departments")
        assert response.status_code == 200
        assert set(response.json()) == set(departments)
