"""Database models for the HRIS system."""
from datetime import datetime, date
from enum import Enum
from typing import Optional, List
from sqlalchemy import (
    Column, Integer, String, Date, DateTime, Float, 
    ForeignKey, Text, Enum as SQLEnum, Boolean
)
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class EmployeeStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ON_LEAVE = "on_leave"
    TERMINATED = "terminated"


class AuditAction(str, Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"


class Employee(Base):
    """Employee model representing a single employee record."""
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String(50), unique=True, index=True, nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(50), nullable=True)
    title = Column(String(200), nullable=False)
    department = Column(String(100), nullable=False)
    hire_date = Column(Date, nullable=False)
    salary = Column(Float, nullable=True)
    status = Column(SQLEnum(EmployeeStatus), default=EmployeeStatus.ACTIVE, nullable=False)
    manager_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    manager = relationship("Employee", remote_side=[id], backref="direct_reports")
    team_memberships = relationship("TeamMember", back_populates="employee", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Employee {self.employee_id}: {self.first_name} {self.last_name}>"


class Team(Base):
    """Team model representing organizational teams."""
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    parent_team_id = Column(Integer, ForeignKey("teams.id"), nullable=True)
    lead_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    parent_team = relationship("Team", remote_side=[id], backref="sub_teams")
    lead = relationship("Employee", foreign_keys=[lead_id])
    members = relationship("TeamMember", back_populates="team", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Team {self.name}>"


class TeamMember(Base):
    """Association table for team membership."""
    __tablename__ = "team_members"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    joined_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    team = relationship("Team", back_populates="members")
    employee = relationship("Employee", back_populates="team_memberships")


class AuditLog(Base):
    """Audit log for tracking all changes to employee and team data."""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String(50), nullable=False)  # "employee" or "team"
    entity_id = Column(Integer, nullable=False)
    action = Column(SQLEnum(AuditAction), nullable=False)
    changes = Column(Text, nullable=True)  # JSON string of changes
    performed_by = Column(String(100), nullable=True)  # For future auth integration
    performed_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<AuditLog {self.action} on {self.entity_type}:{self.entity_id}>"

