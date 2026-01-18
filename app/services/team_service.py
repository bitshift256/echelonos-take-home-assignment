"""Team service for business logic."""
import json
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models import Team, TeamMember, AuditLog, AuditAction


class TeamService:
    """Service class for team operations."""

    def __init__(self, db: Session):
        self.db = db

    def get_all(self, skip: int = 0, limit: int = 100) -> tuple[List[Team], int]:
        """Get all teams."""
        query = self.db.query(Team)
        total = query.count()
        teams = query.offset(skip).limit(limit).all()
        return teams, total

    def get_by_id(self, team_id: int) -> Optional[Team]:
        """Get team by ID."""
        return self.db.query(Team).filter(Team.id == team_id).first()

    def get_by_name(self, name: str) -> Optional[Team]:
        """Get team by name."""
        return self.db.query(Team).filter(Team.name == name).first()

    def create(self, name: str, description: Optional[str] = None, 
               parent_team_id: Optional[int] = None, lead_id: Optional[int] = None,
               performed_by: Optional[str] = None) -> Team:
        """Create a new team."""
        team = Team(
            name=name,
            description=description,
            parent_team_id=parent_team_id,
            lead_id=lead_id
        )
        self.db.add(team)
        self.db.commit()
        self.db.refresh(team)
        
        # Create audit log
        self._create_audit_log(
            entity_type="team",
            entity_id=team.id,
            action=AuditAction.CREATE,
            changes=json.dumps({
                "name": name,
                "description": description,
                "parent_team_id": parent_team_id,
                "lead_id": lead_id
            }),
            performed_by=performed_by
        )
        
        return team

    def update(
        self, 
        team_id: int, 
        name: Optional[str] = None,
        description: Optional[str] = None,
        parent_team_id: Optional[int] = None,
        lead_id: Optional[int] = None,
        performed_by: Optional[str] = None
    ) -> Optional[Team]:
        """Update a team."""
        team = self.get_by_id(team_id)
        if not team:
            return None
        
        changes = {}
        
        if name is not None and team.name != name:
            changes["name"] = {"old": team.name, "new": name}
            team.name = name
        if description is not None and team.description != description:
            changes["description"] = {"old": team.description, "new": description}
            team.description = description
        if parent_team_id is not None and team.parent_team_id != parent_team_id:
            changes["parent_team_id"] = {"old": team.parent_team_id, "new": parent_team_id}
            team.parent_team_id = parent_team_id
        if lead_id is not None and team.lead_id != lead_id:
            changes["lead_id"] = {"old": team.lead_id, "new": lead_id}
            team.lead_id = lead_id
        
        if changes:
            self.db.commit()
            self.db.refresh(team)
            
            self._create_audit_log(
                entity_type="team",
                entity_id=team.id,
                action=AuditAction.UPDATE,
                changes=json.dumps(changes),
                performed_by=performed_by
            )
        
        return team

    def delete(self, team_id: int, performed_by: Optional[str] = None) -> bool:
        """Delete a team."""
        team = self.get_by_id(team_id)
        if not team:
            return False
        
        team_data = {"name": team.name}
        
        self.db.delete(team)
        self.db.commit()
        
        self._create_audit_log(
            entity_type="team",
            entity_id=team_id,
            action=AuditAction.DELETE,
            changes=json.dumps(team_data),
            performed_by=performed_by
        )
        
        return True

    def search(self, query: str, limit: int = 50) -> List[Team]:
        """Search teams by name or description."""
        search_term = f"%{query}%"
        return self.db.query(Team).filter(
            or_(
                Team.name.ilike(search_term),
                Team.description.ilike(search_term)
            )
        ).limit(limit).all()

    def add_member(self, team_id: int, employee_id: int) -> Optional[TeamMember]:
        """Add an employee to a team."""
        # Check if already a member
        existing = self.db.query(TeamMember).filter(
            TeamMember.team_id == team_id,
            TeamMember.employee_id == employee_id
        ).first()
        
        if existing:
            return existing
        
        member = TeamMember(team_id=team_id, employee_id=employee_id)
        self.db.add(member)
        self.db.commit()
        self.db.refresh(member)
        return member

    def remove_member(self, team_id: int, employee_id: int) -> bool:
        """Remove an employee from a team."""
        member = self.db.query(TeamMember).filter(
            TeamMember.team_id == team_id,
            TeamMember.employee_id == employee_id
        ).first()
        
        if not member:
            return False
        
        self.db.delete(member)
        self.db.commit()
        return True

    def get_members(self, team_id: int) -> List[TeamMember]:
        """Get all members of a team."""
        return self.db.query(TeamMember).filter(TeamMember.team_id == team_id).all()

    def get_sub_teams(self, team_id: int) -> List[Team]:
        """Get all sub-teams of a team."""
        return self.db.query(Team).filter(Team.parent_team_id == team_id).all()

    def get_root_teams(self) -> List[Team]:
        """Get teams without parent teams."""
        return self.db.query(Team).filter(Team.parent_team_id.is_(None)).all()

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

