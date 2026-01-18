"""Organizational chart API routes."""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import OrgChartNode
from app.services.employee_service import EmployeeService
from app.services.export_service import ExportService
from app.models import Employee

router = APIRouter(prefix="/org-chart", tags=["org-chart"])


def build_org_chart_node(employee: Employee, all_employees: List[Employee]) -> OrgChartNode:
    """Recursively build org chart node with children."""
    direct_reports = [e for e in all_employees if e.manager_id == employee.id]
    
    return OrgChartNode(
        id=employee.id,
        employee_id=employee.employee_id,
        name=f"{employee.first_name} {employee.last_name}",
        title=employee.title,
        department=employee.department,
        email=employee.email,
        children=[build_org_chart_node(report, all_employees) for report in direct_reports]
    )


@router.get("", response_model=List[OrgChartNode])
def get_org_chart(
    department: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get the full organizational chart.
    Returns a tree structure starting from employees without managers.
    """
    service = EmployeeService(db)
    
    # Get all employees (optionally filtered by department)
    employees, _ = service.get_all(0, 10000, department=department)
    
    # Find root employees (no manager)
    root_employees = [e for e in employees if e.manager_id is None]
    
    # Build tree for each root
    return [build_org_chart_node(root, employees) for root in root_employees]


@router.get("/subtree/{employee_id}", response_model=OrgChartNode)
def get_org_chart_subtree(employee_id: int, db: Session = Depends(get_db)):
    """
    Get org chart subtree starting from a specific employee.
    """
    service = EmployeeService(db)
    
    employee = service.get_by_id(employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    # Get all employees for building the tree
    all_employees, _ = service.get_all(0, 10000)
    
    return build_org_chart_node(employee, all_employees)


@router.get("/flat", response_model=List[dict])
def get_org_chart_flat(
    department: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get org chart as a flat list with hierarchy levels.
    Useful for table displays or alternative visualizations.
    """
    service = EmployeeService(db)
    employees, _ = service.get_all(0, 10000, department=department)
    
    result = []
    
    def add_with_level(employee: Employee, level: int):
        """Add employee and their reports recursively."""
        result.append({
            "id": employee.id,
            "employee_id": employee.employee_id,
            "name": f"{employee.first_name} {employee.last_name}",
            "title": employee.title,
            "department": employee.department,
            "email": employee.email,
            "manager_id": employee.manager_id,
            "level": level
        })
        
        direct_reports = [e for e in employees if e.manager_id == employee.id]
        for report in direct_reports:
            add_with_level(report, level + 1)
    
    # Start with root employees
    root_employees = [e for e in employees if e.manager_id is None]
    for root in root_employees:
        add_with_level(root, 0)
    
    return result


@router.get("/export/pdf")
def export_org_chart_pdf(
    department: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Export organizational chart to PDF format."""
    service = EmployeeService(db)
    employees, _ = service.get_all(0, 10000, department=department)
    
    title = "Organization Chart"
    if department:
        title += f" - {department}"
    
    pdf_content = ExportService.org_chart_to_pdf(employees, title)
    
    return Response(
        content=pdf_content,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=org_chart.pdf"}
    )

