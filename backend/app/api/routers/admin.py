import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.db.models import User, Student, AuditLog, Skill, UserRole
from backend.app.api.deps import get_current_user, require_role
from backend.app.core.audit import log_audit_event

router = APIRouter(prefix="/admin", tags=["Administration & Data Governance"])

class UpdateUserRoleRequest(BaseModel):
    role: str

class CreateSkillRequest(BaseModel):
    canonical_name: str
    category: str
    aliases: List[str] = []
    description: Optional[str] = None

@router.get("/users")
def list_users(
    current_user: User = Depends(require_role([UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    """Admin endpoint: List all user accounts and roles."""
    users = db.query(User).all()
    results = []
    for u in users:
        student_info = None
        if u.student_profile:
            student_info = {
                "roll_number": u.student_profile.roll_number,
                "registration_number": u.student_profile.registration_number,
                "department": u.student_profile.department
            }
        results.append({
            "user_id": u.user_id,
            "name": u.name,
            "email": u.email,
            "role": u.role,
            "is_active": u.is_active,
            "created_at": u.created_at.isoformat(),
            "student_profile": student_info
        })
    return results

@router.put("/users/{user_id}/role")
def update_user_role(
    user_id: str,
    request: UpdateUserRoleRequest,
    current_user: User = Depends(require_role([UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    """Admin endpoint: Modify role assignment for a user."""
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    old_role = user.role
    user.role = request.role
    db.commit()

    log_audit_event(
        db,
        user_id=current_user.user_id,
        action="USER_ROLE_UPDATED",
        entity_type="USER",
        entity_id=user.user_id,
        details={"old_role": old_role, "new_role": user.role}
    )

    return {"message": f"User role updated to '{user.role}'.", "user_id": user.user_id, "role": user.role}

@router.get("/audit-logs")
def list_audit_logs(
    limit: int = 50,
    current_user: User = Depends(require_role([UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    """Admin endpoint: View system audit trail (FR-08)."""
    logs = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(limit).all()
    return [
        {
            "log_id": log.log_id,
            "user_name": log.user.name if log.user else "System",
            "action": log.action,
            "entity_type": log.entity_type,
            "entity_id": log.entity_id,
            "details": log.details,
            "timestamp": log.timestamp.isoformat()
        }
        for log in logs
    ]

@router.get("/taxonomy")
def get_skills_taxonomy(db: Session = Depends(get_db)):
    """List normalized skills taxonomy."""
    skills = db.query(Skill).all()
    results = []
    for s in skills:
        aliases = []
        if s.aliases:
            try:
                aliases = json.loads(s.aliases)
            except Exception:
                aliases = [s.aliases]
        results.append({
            "skill_id": s.skill_id,
            "canonical_name": s.canonical_name,
            "category": s.category,
            "aliases": aliases,
            "description": s.description
        })
    return results

@router.post("/taxonomy")
def add_canonical_skill(
    request: CreateSkillRequest,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.FACULTY])),
    db: Session = Depends(get_db)
):
    """Add a new canonical skill to the normalized taxonomy."""
    existing = db.query(Skill).filter(Skill.canonical_name.ilike(request.canonical_name.strip())).first()
    if existing:
        raise HTTPException(status_code=400, detail="Skill already exists in taxonomy.")

    skill = Skill(
        canonical_name=request.canonical_name.strip(),
        category=request.category.strip(),
        aliases=json.dumps(request.aliases),
        description=request.description
    )
    db.add(skill)
    db.commit()

    return {"message": "Skill added to taxonomy.", "skill_id": skill.skill_id}
