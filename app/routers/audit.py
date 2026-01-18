"""Audit log API routes."""
from typing import Optional, List
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.database import get_db
from app.models import AuditLog, AuditAction
from app.schemas import AuditLogResponse

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("", response_model=dict)
def list_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    entity_type: Optional[str] = Query(None, description="Filter by entity type (employee/team)"),
    entity_id: Optional[int] = Query(None, description="Filter by entity ID"),
    action: Optional[AuditAction] = Query(None, description="Filter by action type"),
    days: Optional[int] = Query(None, ge=1, le=365, description="Filter by last N days"),
    db: Session = Depends(get_db)
):
    """
    List audit logs with optional filtering.
    Returns paginated audit log entries.
    """
    query = db.query(AuditLog)
    
    if entity_type:
        query = query.filter(AuditLog.entity_type == entity_type)
    if entity_id is not None:
        query = query.filter(AuditLog.entity_id == entity_id)
    if action:
        query = query.filter(AuditLog.action == action)
    if days:
        cutoff = datetime.utcnow() - timedelta(days=days)
        query = query.filter(AuditLog.performed_at >= cutoff)
    
    total = query.count()
    logs = query.order_by(desc(AuditLog.performed_at)).offset(skip).limit(limit).all()
    
    return {
        "items": [AuditLogResponse.model_validate(log) for log in logs],
        "total": total,
        "page": skip // limit + 1,
        "page_size": limit,
        "total_pages": (total + limit - 1) // limit
    }


@router.get("/entity/{entity_type}/{entity_id}", response_model=List[AuditLogResponse])
def get_entity_audit_logs(
    entity_type: str,
    entity_id: int,
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """
    Get audit logs for a specific entity.
    """
    logs = db.query(AuditLog).filter(
        AuditLog.entity_type == entity_type,
        AuditLog.entity_id == entity_id
    ).order_by(desc(AuditLog.performed_at)).limit(limit).all()
    
    return [AuditLogResponse.model_validate(log) for log in logs]

