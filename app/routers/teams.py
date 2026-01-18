"""Team API routes."""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import (
    TeamCreate, TeamUpdate, TeamResponse, TeamWithDetails,
    TeamMemberAdd, TeamMemberResponse
)
from app.services.team_service import TeamService
from app.services.employee_service import EmployeeService
from app.services.export_service import ExportService

router = APIRouter(prefix="/teams", tags=["teams"])


@router.get("", response_model=dict)
def list_teams(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """List all teams with pagination."""
    service = TeamService(db)
    teams, total = service.get_all(skip, limit)
    
    return {
        "items": [TeamResponse.model_validate(t) for t in teams],
        "total": total,
        "page": skip // limit + 1,
        "page_size": limit,
        "total_pages": (total + limit - 1) // limit
    }


@router.get("/search", response_model=List[TeamResponse])
def search_teams(
    q: str = Query(..., min_length=1),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Search teams by name or description."""
    service = TeamService(db)
    teams = service.search(q, limit)
    return [TeamResponse.model_validate(t) for t in teams]


@router.get("/export/csv")
def export_teams_csv(db: Session = Depends(get_db)):
    """Export teams to CSV format."""
    service = TeamService(db)
    teams, _ = service.get_all(0, 10000)
    csv_content = ExportService.teams_to_csv(teams)
    
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=teams.csv"}
    )


@router.get("/export/excel")
def export_teams_excel(db: Session = Depends(get_db)):
    """Export teams to Excel format."""
    service = TeamService(db)
    teams, _ = service.get_all(0, 10000)
    excel_content = ExportService.teams_to_excel(teams)
    
    return Response(
        content=excel_content,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=teams.xlsx"}
    )


@router.get("/{team_id}", response_model=TeamWithDetails)
def get_team(team_id: int, db: Session = Depends(get_db)):
    """Get a single team with full details."""
    service = TeamService(db)
    team = service.get_by_id(team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return TeamWithDetails.model_validate(team)


@router.post("", response_model=TeamResponse, status_code=201)
def create_team(team_data: TeamCreate, db: Session = Depends(get_db)):
    """Create a new team."""
    team_service = TeamService(db)
    employee_service = EmployeeService(db)
    
    # Check for duplicate name
    if team_service.get_by_name(team_data.name):
        raise HTTPException(status_code=400, detail="Team name already exists")
    
    # Validate parent team if provided
    if team_data.parent_team_id:
        parent = team_service.get_by_id(team_data.parent_team_id)
        if not parent:
            raise HTTPException(status_code=400, detail="Parent team not found")
    
    # Validate lead if provided
    if team_data.lead_id:
        lead = employee_service.get_by_id(team_data.lead_id)
        if not lead:
            raise HTTPException(status_code=400, detail="Team lead not found")
    
    team = team_service.create(
        name=team_data.name,
        description=team_data.description,
        parent_team_id=team_data.parent_team_id,
        lead_id=team_data.lead_id
    )
    return TeamResponse.model_validate(team)


@router.put("/{team_id}", response_model=TeamResponse)
def update_team(team_id: int, team_data: TeamUpdate, db: Session = Depends(get_db)):
    """Update an existing team."""
    team_service = TeamService(db)
    employee_service = EmployeeService(db)
    
    # Check team exists
    existing = team_service.get_by_id(team_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Team not found")
    
    # Check for duplicate name if being updated
    if team_data.name and team_data.name != existing.name:
        if team_service.get_by_name(team_data.name):
            raise HTTPException(status_code=400, detail="Team name already exists")
    
    # Validate parent team if being updated
    if team_data.parent_team_id is not None:
        if team_data.parent_team_id == team_id:
            raise HTTPException(status_code=400, detail="Team cannot be its own parent")
        if team_data.parent_team_id:
            parent = team_service.get_by_id(team_data.parent_team_id)
            if not parent:
                raise HTTPException(status_code=400, detail="Parent team not found")
    
    # Validate lead if being updated
    if team_data.lead_id is not None and team_data.lead_id:
        lead = employee_service.get_by_id(team_data.lead_id)
        if not lead:
            raise HTTPException(status_code=400, detail="Team lead not found")
    
    team = team_service.update(
        team_id,
        name=team_data.name,
        description=team_data.description,
        parent_team_id=team_data.parent_team_id,
        lead_id=team_data.lead_id
    )
    return TeamResponse.model_validate(team)


@router.delete("/{team_id}", status_code=204)
def delete_team(team_id: int, db: Session = Depends(get_db)):
    """Delete a team."""
    service = TeamService(db)
    
    # Check if team has sub-teams
    sub_teams = service.get_sub_teams(team_id)
    if sub_teams:
        raise HTTPException(
            status_code=400, 
            detail="Cannot delete team with sub-teams. Delete or reassign them first."
        )
    
    if not service.delete(team_id):
        raise HTTPException(status_code=404, detail="Team not found")


@router.post("/{team_id}/members", response_model=TeamMemberResponse, status_code=201)
def add_team_member(team_id: int, member: TeamMemberAdd, db: Session = Depends(get_db)):
    """Add an employee to a team."""
    team_service = TeamService(db)
    employee_service = EmployeeService(db)
    
    # Validate team exists
    team = team_service.get_by_id(team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    # Validate employee exists
    employee = employee_service.get_by_id(member.employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    team_member = team_service.add_member(team_id, member.employee_id)
    return TeamMemberResponse.model_validate(team_member)


@router.delete("/{team_id}/members/{employee_id}", status_code=204)
def remove_team_member(team_id: int, employee_id: int, db: Session = Depends(get_db)):
    """Remove an employee from a team."""
    service = TeamService(db)
    
    if not service.remove_member(team_id, employee_id):
        raise HTTPException(status_code=404, detail="Team member not found")


@router.get("/{team_id}/members", response_model=List[TeamMemberResponse])
def list_team_members(team_id: int, db: Session = Depends(get_db)):
    """List all members of a team."""
    service = TeamService(db)
    
    team = service.get_by_id(team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    members = service.get_members(team_id)
    return [TeamMemberResponse.model_validate(m) for m in members]

