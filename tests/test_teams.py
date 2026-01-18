"""Comprehensive team tests."""
import pytest


class TestTeamCRUD:
    """Test team CRUD operations."""
    
    def test_create_team(self, client, sample_team):
        """Test creating a new team."""
        response = client.post("/api/v1/teams", json=sample_team)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == sample_team["name"]
        assert data["description"] == sample_team["description"]
    
    def test_create_team_duplicate_name(self, client, sample_team):
        """Test that duplicate team names are rejected."""
        client.post("/api/v1/teams", json=sample_team)
        response = client.post("/api/v1/teams", json=sample_team)
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]
    
    def test_get_team(self, client, sample_team):
        """Test getting a team by ID."""
        create_response = client.post("/api/v1/teams", json=sample_team)
        team_id = create_response.json()["id"]
        
        response = client.get(f"/api/v1/teams/{team_id}")
        assert response.status_code == 200
        assert response.json()["name"] == sample_team["name"]
    
    def test_get_team_not_found(self, client):
        """Test getting non-existent team."""
        response = client.get("/api/v1/teams/999")
        assert response.status_code == 404
    
    def test_update_team(self, client, sample_team):
        """Test updating a team."""
        create_response = client.post("/api/v1/teams", json=sample_team)
        team_id = create_response.json()["id"]
        
        response = client.put(
            f"/api/v1/teams/{team_id}",
            json={"name": "Updated Engineering", "description": "Updated description"}
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Updated Engineering"
    
    def test_delete_team(self, client, sample_team):
        """Test deleting a team."""
        create_response = client.post("/api/v1/teams", json=sample_team)
        team_id = create_response.json()["id"]
        
        response = client.delete(f"/api/v1/teams/{team_id}")
        assert response.status_code == 204
        
        get_response = client.get(f"/api/v1/teams/{team_id}")
        assert get_response.status_code == 404


class TestTeamHierarchy:
    """Test team hierarchy and sub-teams."""
    
    def test_create_sub_team(self, client, sample_team):
        """Test creating a sub-team."""
        parent_response = client.post("/api/v1/teams", json=sample_team)
        parent_id = parent_response.json()["id"]
        
        sub_team = {
            "name": "Backend",
            "description": "Backend team",
            "parent_team_id": parent_id
        }
        response = client.post("/api/v1/teams", json=sub_team)
        assert response.status_code == 201
        assert response.json()["parent_team_id"] == parent_id
    
    def test_cannot_be_own_parent(self, client, sample_team):
        """Test that a team cannot be its own parent."""
        create_response = client.post("/api/v1/teams", json=sample_team)
        team_id = create_response.json()["id"]
        
        response = client.put(
            f"/api/v1/teams/{team_id}",
            json={"parent_team_id": team_id}
        )
        assert response.status_code == 400
        assert "own parent" in response.json()["detail"]
    
    def test_cannot_delete_team_with_sub_teams(self, client, sample_team):
        """Test that a team with sub-teams cannot be deleted."""
        parent_response = client.post("/api/v1/teams", json=sample_team)
        parent_id = parent_response.json()["id"]
        
        sub_team = {"name": "Backend", "parent_team_id": parent_id}
        client.post("/api/v1/teams", json=sub_team)
        
        response = client.delete(f"/api/v1/teams/{parent_id}")
        assert response.status_code == 400
        assert "sub-teams" in response.json()["detail"]
    
    def test_get_team_with_sub_teams(self, client, sample_team):
        """Test getting a team includes sub-teams."""
        parent_response = client.post("/api/v1/teams", json=sample_team)
        parent_id = parent_response.json()["id"]
        
        for name in ["Backend", "Frontend"]:
            client.post("/api/v1/teams", json={"name": name, "parent_team_id": parent_id})
        
        response = client.get(f"/api/v1/teams/{parent_id}")
        assert response.status_code == 200
        assert len(response.json()["sub_teams"]) == 2


class TestTeamMembers:
    """Test team membership operations."""
    
    def test_add_member(self, client, sample_team, sample_employee):
        """Test adding a member to a team."""
        team_response = client.post("/api/v1/teams", json=sample_team)
        team_id = team_response.json()["id"]
        
        emp_response = client.post("/api/v1/employees", json=sample_employee)
        emp_id = emp_response.json()["id"]
        
        response = client.post(
            f"/api/v1/teams/{team_id}/members",
            json={"employee_id": emp_id}
        )
        assert response.status_code == 201
    
    def test_add_member_to_nonexistent_team(self, client, sample_employee):
        """Test adding member to non-existent team."""
        emp_response = client.post("/api/v1/employees", json=sample_employee)
        emp_id = emp_response.json()["id"]
        
        response = client.post(
            "/api/v1/teams/999/members",
            json={"employee_id": emp_id}
        )
        assert response.status_code == 404
    
    def test_add_nonexistent_employee_to_team(self, client, sample_team):
        """Test adding non-existent employee to team."""
        team_response = client.post("/api/v1/teams", json=sample_team)
        team_id = team_response.json()["id"]
        
        response = client.post(
            f"/api/v1/teams/{team_id}/members",
            json={"employee_id": 999}
        )
        assert response.status_code == 404
    
    def test_remove_member(self, client, sample_team, sample_employee):
        """Test removing a member from a team."""
        team_response = client.post("/api/v1/teams", json=sample_team)
        team_id = team_response.json()["id"]
        
        emp_response = client.post("/api/v1/employees", json=sample_employee)
        emp_id = emp_response.json()["id"]
        
        client.post(f"/api/v1/teams/{team_id}/members", json={"employee_id": emp_id})
        response = client.delete(f"/api/v1/teams/{team_id}/members/{emp_id}")
        assert response.status_code == 204
    
    def test_list_team_members(self, client, sample_team, sample_employee):
        """Test listing team members."""
        team_response = client.post("/api/v1/teams", json=sample_team)
        team_id = team_response.json()["id"]
        
        for i in range(3):
            emp = sample_employee.copy()
            emp["employee_id"] = f"EMP{i:03d}"
            emp["email"] = f"emp{i}@example.com"
            emp_response = client.post("/api/v1/employees", json=emp)
            client.post(
                f"/api/v1/teams/{team_id}/members",
                json={"employee_id": emp_response.json()["id"]}
            )
        
        response = client.get(f"/api/v1/teams/{team_id}/members")
        assert response.status_code == 200
        assert len(response.json()) == 3
    
    def test_add_duplicate_member(self, client, sample_team, sample_employee):
        """Test adding same member twice returns existing membership."""
        team_response = client.post("/api/v1/teams", json=sample_team)
        team_id = team_response.json()["id"]
        
        emp_response = client.post("/api/v1/employees", json=sample_employee)
        emp_id = emp_response.json()["id"]
        
        client.post(f"/api/v1/teams/{team_id}/members", json={"employee_id": emp_id})
        response = client.post(f"/api/v1/teams/{team_id}/members", json={"employee_id": emp_id})
        assert response.status_code == 201


class TestTeamLead:
    """Test team lead functionality."""
    
    def test_assign_team_lead(self, client, sample_team, sample_employee):
        """Test assigning a team lead."""
        emp_response = client.post("/api/v1/employees", json=sample_employee)
        emp_id = emp_response.json()["id"]
        
        sample_team["lead_id"] = emp_id
        response = client.post("/api/v1/teams", json=sample_team)
        assert response.status_code == 201
        assert response.json()["lead_id"] == emp_id
    
    def test_assign_invalid_lead(self, client, sample_team):
        """Test assigning invalid lead returns 400."""
        sample_team["lead_id"] = 999
        response = client.post("/api/v1/teams", json=sample_team)
        assert response.status_code == 400
        assert "lead not found" in response.json()["detail"].lower()
    
    def test_get_team_with_lead(self, client, sample_team, sample_employee):
        """Test getting team includes lead info."""
        emp_response = client.post("/api/v1/employees", json=sample_employee)
        emp_id = emp_response.json()["id"]
        
        sample_team["lead_id"] = emp_id
        team_response = client.post("/api/v1/teams", json=sample_team)
        team_id = team_response.json()["id"]
        
        response = client.get(f"/api/v1/teams/{team_id}")
        assert response.status_code == 200
        assert response.json()["lead"] is not None
        assert response.json()["lead"]["id"] == emp_id


class TestTeamSearch:
    """Test team search functionality."""
    
    def test_search_teams_by_name(self, client):
        """Test searching teams by name."""
        for name in ["Engineering", "Marketing", "Sales"]:
            client.post("/api/v1/teams", json={"name": name})
        
        response = client.get("/api/v1/teams/search?q=Engineering")
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["name"] == "Engineering"
    
    def test_search_teams_by_description(self, client):
        """Test searching teams by description."""
        client.post("/api/v1/teams", json={
            "name": "Backend",
            "description": "API development team"
        })
        
        response = client.get("/api/v1/teams/search?q=API")
        assert response.status_code == 200
        assert len(response.json()) == 1


class TestTeamExport:
    """Test team export functionality."""
    
    def test_export_teams_csv(self, client, sample_team):
        """Test exporting teams to CSV."""
        client.post("/api/v1/teams", json=sample_team)
        
        response = client.get("/api/v1/teams/export/csv")
        assert response.status_code == 200
        assert "text/csv" in response.headers["content-type"]
        assert "Engineering" in response.text
    
    def test_export_teams_excel(self, client, sample_team):
        """Test exporting teams to Excel."""
        client.post("/api/v1/teams", json=sample_team)
        
        response = client.get("/api/v1/teams/export/excel")
        assert response.status_code == 200
        assert "spreadsheetml" in response.headers["content-type"]
