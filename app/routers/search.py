"""Search API routes."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import SearchResults, EmployeeResponse, TeamResponse
from app.services.employee_service import EmployeeService
from app.services.team_service import TeamService

router = APIRouter(prefix="/search", tags=["search"])


@router.get("", response_model=SearchResults)
def search(
    q: str = Query(..., min_length=1, description="Search query"),
    search_employees: bool = Query(True, description="Search in employees"),
    search_teams: bool = Query(True, description="Search in teams"),
    limit: int = Query(50, ge=1, le=100, description="Max results per category"),
    db: Session = Depends(get_db)
):
    """
    Search across employees and teams.
    Returns matching results from both categories.
    """
    results = SearchResults()
    
    if search_employees:
        employee_service = EmployeeService(db)
        employees = employee_service.search(q, limit)
        results.employees = [EmployeeResponse.model_validate(e) for e in employees]
        results.total_employees = len(employees)
    
    if search_teams:
        team_service = TeamService(db)
        teams = team_service.search(q, limit)
        results.teams = [TeamResponse.model_validate(t) for t in teams]
        results.total_teams = len(teams)
    
    return results

