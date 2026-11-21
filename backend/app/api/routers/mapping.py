from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.db.models import JobRole, Course, CourseSkill, JobSkill, SkillMapping, Skill, User, UserRole
from backend.app.api.deps import get_current_user, require_role
from backend.app.nlp.matcher import default_matcher
from backend.app.core.audit import log_audit_event

router = APIRouter(prefix="/mapping", tags=["Academia–Industry Skill Mapping"])

class MappingRunRequest(BaseModel):
    job_id: str
    department: Optional[str] = None
    cohort_id: Optional[str] = None

class MappingReviewRequest(BaseModel):
    status: str = "approved"  # approved, rejected
    confidence: Optional[float] = None

@router.post("/curriculum-to-job")
def map_curriculum_to_job(
    request: MappingRunRequest,
    db: Session = Depends(get_db)
):
    """
    Compare academic curriculum skills with industry job requirements (FR-04).
    Detects Exact matches, Semantic/Related matches, and Unmapped requirements.
    Calculates Curriculum Coverage percentages.
    """
    job_role = db.query(JobRole).filter(JobRole.job_id == request.job_id).first()
    if not job_role:
        raise HTTPException(status_code=404, detail="Target job role not found.")

    # Fetch courses for the department or all courses
    course_query = db.query(Course)
    if request.department:
        course_query = course_query.filter(Course.department == request.department)
    if request.cohort_id:
        course_query = course_query.filter(Course.cohort_id == request.cohort_id)
    
    courses = course_query.all()
    course_ids = [c.course_id for c in courses]

    # Gather academic skills from courses
    course_skills = db.query(CourseSkill).filter(
        CourseSkill.course_id.in_(course_ids),
        CourseSkill.status == "approved"
    ).all()

    academic_skills_list = []
    for cs in course_skills:
        if cs.skill:
            academic_skills_list.append({
                "canonical_name": cs.skill.canonical_name,
                "category": cs.skill.category,
                "course_code": cs.course.course_code,
                "course_name": cs.course.course_name,
                "coverage_level": cs.coverage_level
            })

    # Gather job skills
    job_skills_list = []
    for js in job_role.skills:
        if js.skill:
            job_skills_list.append({
                "job_skill_id": js.id,
                "canonical_name": js.skill.canonical_name,
                "category": js.skill.category,
                "importance_weight": js.importance_weight,
                "required_proficiency": js.required_proficiency
            })

    # Run Matcher
    mapping_result = default_matcher.match_curriculum_to_job(
        academic_skills=academic_skills_list,
        job_skills=job_skills_list
    )

    return {
        "job_id": job_role.job_id,
        "job_title": job_role.title,
        "company_name": job_role.company_name,
        "matched_curriculum_skills": mapping_result["matched_pairs"],
        "unmapped_industry_skills": mapping_result["unmapped_job_skills"],
        "unweighted_coverage": mapping_result["unweighted_coverage"],
        "weighted_coverage": mapping_result["weighted_coverage"],
        "total_required_skills": mapping_result["total_job_skills"],
        "covered_skills_count": mapping_result["covered_job_skills"],
        "academic_courses_evaluated": len(courses)
    }

@router.get("/curriculum-coverage/{job_id}")
def get_curriculum_coverage(
    job_id: str,
    department: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Compute overall curriculum coverage for a job role."""
    req = MappingRunRequest(job_id=job_id, department=department)
    return map_curriculum_to_job(req, db)
