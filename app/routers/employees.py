"""Employee API routes."""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Response
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import EmployeeStatus
from app.schemas import (
    EmployeeCreate, EmployeeUpdate, EmployeeResponse, 
    EmployeeWithManager, EmployeeWithReports, BulkImportResult
)
from app.services.employee_service import EmployeeService
from app.services.export_service import ExportService
from app.services.import_service import ImportService

router = APIRouter(prefix="/employees", tags=["employees"])


@router.get("", response_model=dict)
def list_employees(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    department: Optional[str] = None,
    status: Optional[EmployeeStatus] = None,
    manager_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """List all employees with optional filtering and pagination."""
    service = EmployeeService(db)
    employees, total = service.get_all(skip, limit, department, status, manager_id)
    
    return {
        "items": [EmployeeResponse.model_validate(e) for e in employees],
        "total": total,
        "page": skip // limit + 1,
        "page_size": limit,
        "total_pages": (total + limit - 1) // limit
    }


@router.get("/departments", response_model=List[str])
def list_departments(db: Session = Depends(get_db)):
    """Get list of all unique departments."""
    service = EmployeeService(db)
    return service.get_departments()


@router.get("/search", response_model=List[EmployeeResponse])
def search_employees(
    q: str = Query(..., min_length=1),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Search employees by name, email, title, or department."""
    service = EmployeeService(db)
    employees = service.search(q, limit)
    return [EmployeeResponse.model_validate(e) for e in employees]


@router.get("/export/csv")
def export_employees_csv(
    department: Optional[str] = None,
    status: Optional[EmployeeStatus] = None,
    db: Session = Depends(get_db)
):
    """Export employees to CSV format."""
    service = EmployeeService(db)
    employees, _ = service.get_all(0, 10000, department, status)
    csv_content = ExportService.employees_to_csv(employees)
    
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=employees.csv"}
    )


@router.get("/export/excel")
def export_employees_excel(
    department: Optional[str] = None,
    status: Optional[EmployeeStatus] = None,
    db: Session = Depends(get_db)
):
    """Export employees to Excel format."""
    service = EmployeeService(db)
    employees, _ = service.get_all(0, 10000, department, status)
    excel_content = ExportService.employees_to_excel(employees)
    
    return Response(
        content=excel_content,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=employees.xlsx"}
    )


@router.get("/export/pdf")
def export_employees_pdf(
    department: Optional[str] = None,
    status: Optional[EmployeeStatus] = None,
    db: Session = Depends(get_db)
):
    """Export employees to PDF format."""
    service = EmployeeService(db)
    employees, _ = service.get_all(0, 10000, department, status)
    pdf_content = ExportService.employees_to_pdf(employees)
    
    return Response(
        content=pdf_content,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=employees.pdf"}
    )


@router.post("/import/csv", response_model=BulkImportResult)
async def import_employees_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Bulk import employees from CSV file."""
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV file")
    
    content = await file.read()
    service = ImportService(db)
    return service.import_employees_csv(content)


@router.post("/import/excel", response_model=BulkImportResult)
async def import_employees_excel(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Bulk import employees from Excel file."""
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="File must be an Excel file")
    
    content = await file.read()
    service = ImportService(db)
    return service.import_employees_excel(content)


@router.get("/{employee_id}", response_model=EmployeeWithManager)
def get_employee(employee_id: int, db: Session = Depends(get_db)):
    """Get a single employee by ID."""
    service = EmployeeService(db)
    employee = service.get_by_id(employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return EmployeeWithManager.model_validate(employee)


@router.get("/{employee_id}/reports", response_model=EmployeeWithReports)
def get_employee_reports(employee_id: int, db: Session = Depends(get_db)):
    """Get an employee with their direct reports."""
    service = EmployeeService(db)
    employee = service.get_by_id(employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return EmployeeWithReports.model_validate(employee)


@router.post("", response_model=EmployeeResponse, status_code=201)
def create_employee(employee_data: EmployeeCreate, db: Session = Depends(get_db)):
    """Create a new employee."""
    service = EmployeeService(db)
    
    # Check for duplicate employee_id
    if service.get_by_employee_id(employee_data.employee_id):
        raise HTTPException(status_code=400, detail="Employee ID already exists")
    
    # Check for duplicate email
    if service.get_by_email(employee_data.email):
        raise HTTPException(status_code=400, detail="Email already exists")
    
    # Validate manager exists if provided
    if employee_data.manager_id:
        manager = service.get_by_id(employee_data.manager_id)
        if not manager:
            raise HTTPException(status_code=400, detail="Manager not found")
    
    employee = service.create(employee_data)
    return EmployeeResponse.model_validate(employee)


@router.put("/{employee_id}", response_model=EmployeeResponse)
def update_employee(
    employee_id: int, 
    employee_data: EmployeeUpdate, 
    db: Session = Depends(get_db)
):
    """Update an existing employee."""
    service = EmployeeService(db)
    
    # Check employee exists
    existing = service.get_by_id(employee_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    # Check for duplicate email if being updated
    if employee_data.email and employee_data.email != existing.email:
        if service.get_by_email(employee_data.email):
            raise HTTPException(status_code=400, detail="Email already exists")
    
    # Validate manager exists if being updated
    if employee_data.manager_id:
        if employee_data.manager_id == employee_id:
            raise HTTPException(status_code=400, detail="Employee cannot be their own manager")
        manager = service.get_by_id(employee_data.manager_id)
        if not manager:
            raise HTTPException(status_code=400, detail="Manager not found")
    
    employee = service.update(employee_id, employee_data)
    return EmployeeResponse.model_validate(employee)


@router.delete("/{employee_id}", status_code=204)
def delete_employee(employee_id: int, db: Session = Depends(get_db)):
    """Delete an employee."""
    service = EmployeeService(db)
    
    # Check if employee has direct reports
    reports = service.get_direct_reports(employee_id)
    if reports:
        raise HTTPException(
            status_code=400, 
            detail="Cannot delete employee with direct reports. Reassign them first."
        )
    
    if not service.delete(employee_id):
        raise HTTPException(status_code=404, detail="Employee not found")

