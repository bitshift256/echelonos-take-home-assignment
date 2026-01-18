"""Pydantic schemas for request/response validation."""
from datetime import datetime, date
from typing import Optional, List, Any
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from app.models import EmployeeStatus, AuditAction


# ============== Employee Schemas ==============

class EmployeeBase(BaseModel):
    """Base employee schema with common fields."""
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=50)
    title: str = Field(..., min_length=1, max_length=200)
    department: str = Field(..., min_length=1, max_length=100)
    hire_date: date
    salary: Optional[float] = Field(None, ge=0)
    status: EmployeeStatus = EmployeeStatus.ACTIVE
    manager_id: Optional[int] = None


class EmployeeCreate(EmployeeBase):
    """Schema for creating a new employee."""
    employee_id: str = Field(..., min_length=1, max_length=50)


class EmployeeUpdate(BaseModel):
    """Schema for updating an employee (all fields optional)."""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=50)
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    department: Optional[str] = Field(None, min_length=1, max_length=100)
    hire_date: Optional[date] = None
    salary: Optional[float] = Field(None, ge=0)
    status: Optional[EmployeeStatus] = None
    manager_id: Optional[int] = None


class EmployeeResponse(EmployeeBase):
    """Schema for employee response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    employee_id: str
    created_at: datetime
    updated_at: datetime


class EmployeeWithManager(EmployeeResponse):
    """Employee response including manager info."""
    manager: Optional["EmployeeResponse"] = None


class EmployeeWithReports(EmployeeResponse):
    """Employee response including direct reports."""
    direct_reports: List["EmployeeResponse"] = []


# ============== Team Schemas ==============

class TeamBase(BaseModel):
    """Base team schema."""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    parent_team_id: Optional[int] = None
    lead_id: Optional[int] = None


class TeamCreate(TeamBase):
    """Schema for creating a new team."""
    pass


class TeamUpdate(BaseModel):
    """Schema for updating a team."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    parent_team_id: Optional[int] = None
    lead_id: Optional[int] = None


class TeamMemberAdd(BaseModel):
    """Schema for adding a member to a team."""
    employee_id: int


class TeamMemberResponse(BaseModel):
    """Schema for team member response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    employee_id: int
    joined_at: datetime
    employee: Optional[EmployeeResponse] = None


class TeamResponse(TeamBase):
    """Schema for team response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime
    updated_at: datetime


class TeamWithDetails(TeamResponse):
    """Team response with full details."""
    lead: Optional[EmployeeResponse] = None
    parent_team: Optional[TeamResponse] = None
    sub_teams: List[TeamResponse] = []
    members: List[TeamMemberResponse] = []


# ============== Org Chart Schemas ==============

class OrgChartNode(BaseModel):
    """Node in the organizational chart."""
    id: int
    employee_id: str
    name: str
    title: str
    department: str
    email: str
    children: List["OrgChartNode"] = []


# ============== Search Schemas ==============

class SearchQuery(BaseModel):
    """Schema for search queries."""
    query: str = Field(..., min_length=1)
    search_employees: bool = True
    search_teams: bool = True


class SearchResults(BaseModel):
    """Schema for search results."""
    employees: List[EmployeeResponse] = []
    teams: List[TeamResponse] = []
    total_employees: int = 0
    total_teams: int = 0


# ============== Audit Log Schemas ==============

class AuditLogResponse(BaseModel):
    """Schema for audit log response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    entity_type: str
    entity_id: int
    action: AuditAction
    changes: Optional[str] = None
    performed_by: Optional[str] = None
    performed_at: datetime


# ============== Bulk Import Schemas ==============

class BulkImportResult(BaseModel):
    """Schema for bulk import results."""
    total_processed: int
    successful: int
    failed: int
    errors: List[dict] = []


# ============== Pagination ==============

class PaginatedResponse(BaseModel):
    """Generic paginated response."""
    items: List[Any]
    total: int
    page: int
    page_size: int
    total_pages: int


# Fix forward references
OrgChartNode.model_rebuild()
EmployeeWithManager.model_rebuild()
EmployeeWithReports.model_rebuild()

