"""Employee service for business logic."""
import json
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models import Employee, AuditLog, AuditAction, EmployeeStatus
from app.schemas import EmployeeCreate, EmployeeUpdate


class EmployeeService:
    """Service class for employee operations."""

    def __init__(self, db: Session):
        self.db = db

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        department: Optional[str] = None,
        status: Optional[EmployeeStatus] = None,
        manager_id: Optional[int] = None
    ) -> tuple[List[Employee], int]:
        """Get all employees with optional filters."""
        query = self.db.query(Employee)
        
        if department:
            query = query.filter(Employee.department == department)
        if status:
            query = query.filter(Employee.status == status)
        if manager_id is not None:
            query = query.filter(Employee.manager_id == manager_id)
        
        total = query.count()
        employees = query.offset(skip).limit(limit).all()
        return employees, total

    def get_by_id(self, employee_id: int) -> Optional[Employee]:
        """Get employee by ID."""
        return self.db.query(Employee).filter(Employee.id == employee_id).first()

    def get_by_employee_id(self, employee_id: str) -> Optional[Employee]:
        """Get employee by employee_id string."""
        return self.db.query(Employee).filter(Employee.employee_id == employee_id).first()

    def get_by_email(self, email: str) -> Optional[Employee]:
        """Get employee by email."""
        return self.db.query(Employee).filter(Employee.email == email).first()

    def create(self, employee_data: EmployeeCreate, performed_by: Optional[str] = None) -> Employee:
        """Create a new employee."""
        employee = Employee(**employee_data.model_dump())
        self.db.add(employee)
        self.db.commit()
        self.db.refresh(employee)
        
        # Create audit log
        self._create_audit_log(
            entity_type="employee",
            entity_id=employee.id,
            action=AuditAction.CREATE,
            changes=json.dumps(employee_data.model_dump(), default=str),
            performed_by=performed_by
        )
        
        return employee

    def update(
        self, 
        employee_id: int, 
        employee_data: EmployeeUpdate,
        performed_by: Optional[str] = None
    ) -> Optional[Employee]:
        """Update an employee."""
        employee = self.get_by_id(employee_id)
        if not employee:
            return None
        
        # Track changes for audit
        changes = {}
        update_data = employee_data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            old_value = getattr(employee, field)
            if old_value != value:
                changes[field] = {"old": old_value, "new": value}
                setattr(employee, field, value)
        
        if changes:
            self.db.commit()
            self.db.refresh(employee)
            
            # Create audit log
            self._create_audit_log(
                entity_type="employee",
                entity_id=employee.id,
                action=AuditAction.UPDATE,
                changes=json.dumps(changes, default=str),
                performed_by=performed_by
            )
        
        return employee

    def delete(self, employee_id: int, performed_by: Optional[str] = None) -> bool:
        """Delete an employee."""
        employee = self.get_by_id(employee_id)
        if not employee:
            return False
        
        # Store data for audit before deletion
        employee_data = {
            "employee_id": employee.employee_id,
            "name": f"{employee.first_name} {employee.last_name}",
            "email": employee.email
        }
        
        self.db.delete(employee)
        self.db.commit()
        
        # Create audit log
        self._create_audit_log(
            entity_type="employee",
            entity_id=employee_id,
            action=AuditAction.DELETE,
            changes=json.dumps(employee_data, default=str),
            performed_by=performed_by
        )
        
        return True

    def search(self, query: str, limit: int = 50) -> List[Employee]:
        """Search employees by name, email, title, or department."""
        search_term = f"%{query}%"
        return self.db.query(Employee).filter(
            or_(
                Employee.first_name.ilike(search_term),
                Employee.last_name.ilike(search_term),
                Employee.email.ilike(search_term),
                Employee.title.ilike(search_term),
                Employee.department.ilike(search_term),
                Employee.employee_id.ilike(search_term)
            )
        ).limit(limit).all()

    def get_direct_reports(self, manager_id: int) -> List[Employee]:
        """Get all direct reports for a manager."""
        return self.db.query(Employee).filter(Employee.manager_id == manager_id).all()

    def get_departments(self) -> List[str]:
        """Get list of all unique departments."""
        result = self.db.query(Employee.department).distinct().all()
        return [r[0] for r in result]

    def get_root_employees(self) -> List[Employee]:
        """Get employees without managers (top of org chart)."""
        return self.db.query(Employee).filter(Employee.manager_id.is_(None)).all()

    def _create_audit_log(
        self,
        entity_type: str,
        entity_id: int,
        action: AuditAction,
        changes: Optional[str],
        performed_by: Optional[str]
    ):
        """Create an audit log entry."""
        audit_log = AuditLog(
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            changes=changes,
            performed_by=performed_by
        )
        self.db.add(audit_log)
        self.db.commit()

