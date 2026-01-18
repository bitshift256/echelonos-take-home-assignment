"""Organizational chart tests."""
import pytest
from tests.conftest import create_test_employee


class TestOrgChart:
    """Test organizational chart endpoints."""
    
    def test_empty_org_chart(self, client):
        """Test org chart with no employees."""
        response = client.get("/api/v1/org-chart")
        assert response.status_code == 200
        assert response.json() == []
    
    def test_single_employee_org_chart(self, client):
        """Test org chart with single employee (no manager)."""
        create_test_employee(client, "EMP001", "John", "Doe", "CEO")
        
        response = client.get("/api/v1/org-chart")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "John Doe"
        assert data[0]["children"] == []
    
    def test_hierarchical_org_chart(self, client):
        """Test org chart with hierarchy."""
        ceo = create_test_employee(client, "EMP001", "Alice", "CEO", "CEO")
        
        manager1 = create_test_employee(client, "EMP002", "Bob", "Manager", "VP Engineering", manager_id=ceo["id"])
        manager2 = create_test_employee(client, "EMP003", "Carol", "Lead", "VP Sales", manager_id=ceo["id"])
        
        create_test_employee(client, "EMP004", "Dave", "Eng", "Engineer", manager_id=manager1["id"])
        create_test_employee(client, "EMP005", "Eve", "Dev", "Engineer", manager_id=manager1["id"])
        create_test_employee(client, "EMP006", "Frank", "Rep", "Sales Rep", manager_id=manager2["id"])
        
        response = client.get("/api/v1/org-chart")
        assert response.status_code == 200
        data = response.json()
        
        assert len(data) == 1
        ceo_node = data[0]
        assert ceo_node["name"] == "Alice CEO"
        assert len(ceo_node["children"]) == 2
    
    def test_multiple_roots(self, client):
        """Test org chart with multiple root employees."""
        create_test_employee(client, "EMP001", "Alice", "CEO", "CEO")
        create_test_employee(client, "EMP002", "Bob", "President", "President")
        
        response = client.get("/api/v1/org-chart")
        assert response.status_code == 200
        assert len(response.json()) == 2
    
    def test_org_chart_subtree(self, client):
        """Test getting org chart subtree from specific employee."""
        ceo = create_test_employee(client, "EMP001", "Alice", "CEO", "CEO")
        manager = create_test_employee(client, "EMP002", "Bob", "VP", "VP", manager_id=ceo["id"])
        create_test_employee(client, "EMP003", "Carol", "Eng", "Engineer", manager_id=manager["id"])
        
        response = client.get(f"/api/v1/org-chart/subtree/{manager['id']}")
        assert response.status_code == 200
        data = response.json()
        
        assert data["name"] == "Bob VP"
        assert len(data["children"]) == 1
    
    def test_org_chart_subtree_not_found(self, client):
        """Test getting subtree for non-existent employee."""
        response = client.get("/api/v1/org-chart/subtree/999")
        assert response.status_code == 404
    
    def test_org_chart_flat(self, client):
        """Test flat org chart representation."""
        ceo = create_test_employee(client, "EMP001", "Alice", "CEO", "CEO")
        manager = create_test_employee(client, "EMP002", "Bob", "VP", "VP", manager_id=ceo["id"])
        create_test_employee(client, "EMP003", "Carol", "Eng", "Engineer", manager_id=manager["id"])
        
        response = client.get("/api/v1/org-chart/flat")
        assert response.status_code == 200
        data = response.json()
        
        assert len(data) == 3
        
        ceo_entry = next(e for e in data if e["name"] == "Alice CEO")
        manager_entry = next(e for e in data if e["name"] == "Bob VP")
        engineer_entry = next(e for e in data if e["name"] == "Carol Eng")
        
        assert ceo_entry["level"] == 0
        assert manager_entry["level"] == 1
        assert engineer_entry["level"] == 2
    
    def test_org_chart_export_pdf(self, client):
        """Test exporting org chart to PDF."""
        ceo = create_test_employee(client, "EMP001", "Alice", "CEO", "CEO")
        create_test_employee(client, "EMP002", "Bob", "VP", "VP", manager_id=ceo["id"])
        
        response = client.get("/api/v1/org-chart/export/pdf")
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"


class TestOrgChartNode:
    """Test org chart node structure."""
    
    def test_node_contains_required_fields(self, client):
        """Test that org chart nodes contain all required fields."""
        create_test_employee(client, "EMP001", "John", "Doe", "Software Engineer")
        
        response = client.get("/api/v1/org-chart")
        node = response.json()[0]
        
        required_fields = ["id", "employee_id", "name", "title", "department", "email", "children"]
        for field in required_fields:
            assert field in node, f"Missing field: {field}"
    
    def test_node_name_formatting(self, client):
        """Test that node name is properly formatted."""
        data = {
            "employee_id": "EMP001",
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com",
            "title": "Engineer",
            "department": "Engineering",
            "hire_date": "2024-01-15"
        }
        client.post("/api/v1/employees", json=data)
        
        response = client.get("/api/v1/org-chart")
        node = response.json()[0]
        
        assert node["name"] == "John Doe"
