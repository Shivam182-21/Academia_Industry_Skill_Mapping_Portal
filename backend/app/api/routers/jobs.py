import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.db.models import JobRole, JobSkill, Skill, User, UserRole
from backend.app.api.deps import get_current_user, require_role
from backend.app.nlp.extractor import default_extractor
from backend.app.core.audit import log_audit_event

router = APIRouter(prefix="/jobs", tags=["Industry Job Requirement Management"])

class JobRoleCreateRequest(BaseModel):
    title: str
    company_name: Optional[str] = "Industry Partner"
    industry: str
    experience_level: Optional[str] = "Entry-Level / 0–2 Years"
    description: str

class JDUploadRequest(BaseModel):
    title: str
    company_name: Optional[str] = "Industry Partner"
    industry: str
    experience_level: Optional[str] = "Entry-Level / 0–2 Years"
    job_description_text: str

class JobSkillUpdateRequest(BaseModel):
    importance_weight: float  # 1.0 to 5.0
    required_proficiency: str  # beginner, intermediate, advanced

class AddJobSkillRequest(BaseModel):
    skill_name: str
    importance_weight: float = 3.0
    required_proficiency: str = "intermediate"

@router.get("/roles")
def list_job_roles(
    industry: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List all active industry job profiles with required skills and importance weights."""
    query = db.query(JobRole)
    if industry:
        query = query.filter(JobRole.industry.ilike(f"%{industry}%"))
    
    roles = query.all()
    results = []

    for role in roles:
        skills = []
        for js in role.skills:
            skills.append({
                "job_skill_id": js.id,
                "skill_id": js.skill_id,
                "canonical_name": js.skill.canonical_name if js.skill else "Unknown",
                "category": js.skill.category if js.skill else "General",
                "importance_weight": js.importance_weight,
                "required_proficiency": js.required_proficiency
            })

        results.append({
            "job_id": role.job_id,
            "title": role.title,
            "company_name": role.company_name,
            "industry": role.industry,
            "experience_level": role.experience_level,
            "description": role.description,
            "skills": skills,
            "required_skill_count": len(skills)
        })

    return results

@router.get("/roles/{job_id}")
def get_job_role(job_id: str, db: Session = Depends(get_db)):
    """Retrieve full details of a specific job role and required competencies."""
    role = db.query(JobRole).filter(JobRole.job_id == job_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Job role not found.")

    skills = [
        {
            "job_skill_id": js.id,
            "skill_id": js.skill_id,
            "canonical_name": js.skill.canonical_name if js.skill else "Unknown",
            "category": js.skill.category if js.skill else "General",
            "importance_weight": js.importance_weight,
            "required_proficiency": js.required_proficiency
        }
        for js in role.skills
    ]

    return {
        "job_id": role.job_id,
        "title": role.title,
        "company_name": role.company_name,
        "industry": role.industry,
        "experience_level": role.experience_level,
        "description": role.description,
        "skills": skills
    }

@router.post("/upload-jd")
def upload_job_description(
    request: JDUploadRequest,
    current_user: User = Depends(require_role([UserRole.EMPLOYER, UserRole.PLACEMENT_OFFICER, UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    """
    Ingest unstructured Job Description text, automatically extract skills via NLP,
    and initialize importance weights for skill-gap and curriculum mapping.
    """
    role = JobRole(
        title=request.title.strip(),
        company_name=request.company_name.strip() if request.company_name else "Tech Partner",
        industry=request.industry.strip(),
        experience_level=request.experience_level,
        description=request.job_description_text.strip(),
        created_by=current_user.user_id
    )
    db.add(role)
    db.flush()

    # Extract skills using NLP engine
    extracted = default_extractor.extract_skills(request.job_description_text)

    for item in extracted:
        skill = db.query(Skill).filter(Skill.canonical_name == item["canonical_name"]).first()
        if not skill:
            skill = Skill(
                canonical_name=item["canonical_name"],
                category=item["category"],
                aliases=json.dumps([item["canonical_name"].lower()]),
                description=item["description"]
            )
            db.add(skill)
            db.flush()

        # Determine default importance weight: frequency > 1 implies core requirement (4.5), else 3.5
        weight = 4.5 if item.get("frequency", 1) > 1 else 3.5

        db.add(JobSkill(
            job_id=role.job_id,
            skill_id=skill.skill_id,
            importance_weight=weight,
            required_proficiency="intermediate"
        ))

    db.commit()

    log_audit_event(
        db,
        user_id=current_user.user_id,
        action="JOB_DESCRIPTION_UPLOADED",
        entity_type="JOB_ROLE",
        entity_id=role.job_id,
        details={"title": role.title, "extracted_skills": len(extracted)}
    )

    return {
        "message": "Job description parsed and skills extracted successfully.",
        "job_id": role.job_id,
        "title": role.title,
        "extracted_skills_count": len(extracted)
    }

@router.put("/roles/{job_id}/skills/{job_skill_id}")
def update_job_skill_weight(
    job_id: str,
    job_skill_id: str,
    update: JobSkillUpdateRequest,
    current_user: User = Depends(require_role([UserRole.EMPLOYER, UserRole.PLACEMENT_OFFICER, UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    """Modify importance weight (w_i in 1-5) or required proficiency for a skill in a job profile."""
    js = db.query(JobSkill).filter(
        JobSkill.id == job_skill_id,
        JobSkill.job_id == job_id
    ).first()

    if not js:
        raise HTTPException(status_code=404, detail="Job skill requirement record not found.")

    js.importance_weight = max(1.0, min(5.0, update.importance_weight))
    js.required_proficiency = update.required_proficiency.lower()

    db.commit()

    return {
        "message": "Job skill weight updated successfully.",
        "job_skill_id": js.id,
        "importance_weight": js.importance_weight,
        "required_proficiency": js.required_proficiency
    }
