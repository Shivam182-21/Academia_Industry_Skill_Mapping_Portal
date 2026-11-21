from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.db.models import LearningResource, JobRole, Student, Skill, User, UserRole
from backend.app.api.deps import get_current_user, require_role
from backend.app.nlp.gap_analyzer import default_gap_analyzer

router = APIRouter(prefix="/recommendations", tags=["Learning Resource Recommendations"])

class AddResourceRequest(BaseModel):
    title: str
    provider: str
    url: str
    skill_name: str
    resource_type: str = "Course"
    difficulty: str = "Intermediate"

@router.get("/for-job/{job_id}")
def get_recommendations_for_job(
    job_id: str,
    student_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Ranks learning resources to address specific identified skill gaps for a student and target job role (FR-06).
    Explains which gap each recommendation addresses and provides verified course links.
    """
    # 1. Resolve student
    target_student_id = student_id
    if not target_student_id:
        if current_user.student_profile:
            target_student_id = current_user.student_profile.student_id
        else:
            raise HTTPException(status_code=400, detail="Student ID required.")

    student = db.query(Student).filter(Student.student_id == target_student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found.")

    job_role = db.query(JobRole).filter(JobRole.job_id == job_id).first()
    if not job_role:
        raise HTTPException(status_code=404, detail="Job role not found.")

    # 2. Get gap analysis
    job_skills_data = [
        {
            "canonical_name": js.skill.canonical_name if js.skill else "Unknown",
            "category": js.skill.category if js.skill else "General",
            "importance_weight": js.importance_weight,
            "required_proficiency": js.required_proficiency
        }
        for js in job_role.skills
    ]

    student_skills_data = [
        {
            "canonical_name": ss.skill.canonical_name if ss.skill else "Unknown",
            "proficiency_level": ss.proficiency_level,
            "evidence_source": ss.evidence_source,
            "verified": ss.verified
        }
        for ss in student.skills
    ]

    gap_result = default_gap_analyzer.analyze_student_gap(
        job_skills=job_skills_data,
        student_skills=student_skills_data
    )

    # 3. Fetch catalog resources
    all_resources = db.query(LearningResource).all()
    catalog = []
    for res in all_resources:
        # Find importance weight from job skills if present
        imp_weight = 3.0
        for js in job_skills_data:
            if js["canonical_name"].lower() == res.skill.canonical_name.lower():
                imp_weight = js["importance_weight"]
                break

        catalog.append({
            "resource_id": res.resource_id,
            "title": res.title,
            "provider": res.provider,
            "url": res.url,
            "skill_name": res.skill.canonical_name if res.skill else "Unknown",
            "difficulty": res.difficulty,
            "resource_type": res.resource_type,
            "importance_weight": imp_weight
        })

    # 4. Rank recommendations
    ranked = default_gap_analyzer.rank_recommendations(
        gap_analysis=gap_result,
        catalog_resources=catalog,
        top_k=8
    )

    return {
        "student_id": student.student_id,
        "job_id": job_role.job_id,
        "job_title": job_role.title,
        "missing_skills_count": len(gap_result["missing"]),
        "partially_covered_count": len(gap_result["partially_demonstrated"]),
        "recommendations": ranked
    }

@router.get("/resources")
def list_learning_resources(db: Session = Depends(get_db)):
    """List all available learning resources in the system."""
    resources = db.query(LearningResource).all()
    return [
        {
            "resource_id": r.resource_id,
            "title": r.title,
            "provider": r.provider,
            "url": r.url,
            "skill_name": r.skill.canonical_name if r.skill else "Unknown",
            "resource_type": r.resource_type,
            "difficulty": r.difficulty
        }
        for r in resources
    ]

@router.post("/resources")
def add_learning_resource(
    request: AddResourceRequest,
    current_user: User = Depends(require_role([UserRole.FACULTY, UserRole.ADMIN, UserRole.PLACEMENT_OFFICER])),
    db: Session = Depends(get_db)
):
    """Add a verified learning resource."""
    skill = db.query(Skill).filter(Skill.canonical_name.ilike(request.skill_name.strip())).first()
    if not skill:
        skill = Skill(
            canonical_name=request.skill_name.strip(),
            category="Technical Skills",
            aliases="[]",
            description="Created for learning resource"
        )
        db.add(skill)
        db.flush()

    res = LearningResource(
        title=request.title.strip(),
        provider=request.provider.strip(),
        url=request.url.strip(),
        skill_id=skill.skill_id,
        resource_type=request.resource_type,
        difficulty=request.difficulty
    )
    db.add(res)
    db.commit()

    return {"message": "Resource added successfully.", "resource_id": res.resource_id}
