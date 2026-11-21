import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.db.models import Course, CurriculumContent, CourseSkill, Skill, Cohort, User, UserRole
from backend.app.api.deps import get_current_user, require_role
from backend.app.nlp.extractor import default_extractor
from backend.app.core.audit import log_audit_event

router = APIRouter(prefix="/curriculum", tags=["Academic Curriculum Management"])

class CourseCreateRequest(BaseModel):
    course_code: str
    course_name: str
    semester: int
    department: str
    cohort_id: Optional[str] = None
    description: str
    learning_outcomes: Optional[str] = None

class SkillReviewRequest(BaseModel):
    coverage_level: float = 1.0  # 1.0 (Full), 0.5 (Partial)
    status: str = "approved"     # approved, rejected

class AddCourseSkillRequest(BaseModel):
    skill_name: str
    coverage_level: float = 1.0
    evidence_snippet: Optional[str] = "Manually verified by faculty"

@router.get("/courses")
def list_courses(
    department: Optional[str] = None,
    cohort_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Retrieve list of courses with extracted skills and curriculum content."""
    query = db.query(Course)
    if department:
        query = query.filter(Course.department == department)
    if cohort_id:
        query = query.filter(Course.cohort_id == cohort_id)
    
    courses = query.all()
    results = []

    for c in courses:
        content = c.curriculum_content
        skills = []
        for cs in c.course_skills:
            skills.append({
                "course_skill_id": cs.id,
                "skill_id": cs.skill_id,
                "canonical_name": cs.skill.canonical_name if cs.skill else "Unknown",
                "category": cs.skill.category if cs.skill else "General",
                "coverage_level": cs.coverage_level,
                "evidence_snippet": cs.evidence_snippet,
                "status": cs.status
            })

        results.append({
            "course_id": c.course_id,
            "course_code": c.course_code,
            "course_name": c.course_name,
            "semester": c.semester,
            "department": c.department,
            "cohort_name": c.cohort.name if c.cohort else "General",
            "description": content.description if content else "",
            "learning_outcomes": content.learning_outcomes if content else "",
            "skills": skills,
            "skill_count": len(skills)
        })

    return results

@router.post("/courses")
def create_course(
    request: CourseCreateRequest,
    current_user: User = Depends(require_role([UserRole.FACULTY, UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    """Add a new academic course and automatically extract technical skills from syllabus."""
    course = Course(
        course_code=request.course_code.strip().upper(),
        course_name=request.course_name.strip(),
        semester=request.semester,
        department=request.department.strip(),
        cohort_id=request.cohort_id
    )
    db.add(course)
    db.flush()

    content = CurriculumContent(
        course_id=course.course_id,
        description=request.description,
        learning_outcomes=request.learning_outcomes,
        uploaded_by=current_user.user_id
    )
    db.add(content)
    db.flush()

    # Automatically extract skills using NLP Extractor
    full_text = f"{request.description} {request.learning_outcomes or ''}"
    extracted = default_extractor.extract_skills(full_text)

    for item in extracted:
        # Check if canonical skill exists or create it
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

        db.add(CourseSkill(
            course_id=course.course_id,
            skill_id=skill.skill_id,
            coverage_level=1.0,
            evidence_snippet=item.get("evidence_snippet", "Extracted from course description"),
            status="pending",
            approved_by=None
        ))

    db.commit()

    log_audit_event(
        db,
        user_id=current_user.user_id,
        action="COURSE_CREATED",
        entity_type="COURSE",
        entity_id=course.course_id,
        details={"code": course.course_code, "extracted_skills": len(extracted)}
    )

    return {
        "message": "Course created and skills extracted successfully.",
        "course_id": course.course_id,
        "course_code": course.course_code,
        "extracted_skills_count": len(extracted)
    }

@router.post("/courses/{course_id}/extract-skills")
def extract_skills_for_course(
    course_id: str,
    current_user: User = Depends(require_role([UserRole.FACULTY, UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    """Trigger the NLP extractor on existing course description and learning outcomes."""
    course = db.query(Course).filter(Course.course_id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found.")
    
    content = course.curriculum_content
    if not content or not content.description:
        raise HTTPException(status_code=400, detail="Course has no syllabus description to process.")

    full_text = f"{content.description} {content.learning_outcomes or ''}"
    extracted = default_extractor.extract_skills(full_text)

    added_count = 0
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

        # Check if already linked
        existing = db.query(CourseSkill).filter(
            CourseSkill.course_id == course.course_id,
            CourseSkill.skill_id == skill.skill_id
        ).first()

        if not existing:
            db.add(CourseSkill(
                course_id=course.course_id,
                skill_id=skill.skill_id,
                coverage_level=1.0,
                evidence_snippet=item.get("evidence_snippet"),
                status="pending",
                approved_by=None
            ))
            added_count += 1

    db.commit()

    return {
        "message": f"Skill extraction completed. {added_count} new skills identified.",
        "total_extracted": len(extracted),
        "newly_added": added_count
    }

@router.put("/courses/{course_id}/skills/{course_skill_id}")
def review_course_skill(
    course_id: str,
    course_skill_id: str,
    review: SkillReviewRequest,
    current_user: User = Depends(require_role([UserRole.FACULTY, UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    """Faculty reviews, approves, rejects, or adjusts coverage for an extracted course skill."""
    cs = db.query(CourseSkill).filter(
        CourseSkill.id == course_skill_id,
        CourseSkill.course_id == course_id
    ).first()

    if not cs:
        raise HTTPException(status_code=404, detail="Course skill mapping record not found.")

    cs.coverage_level = review.coverage_level
    cs.status = review.status
    cs.approved_by = current_user.user_id

    db.commit()

    log_audit_event(
        db,
        user_id=current_user.user_id,
        action="SKILL_REVIEW_UPDATED",
        entity_type="COURSE_SKILL",
        entity_id=cs.id,
        details={"status": cs.status, "coverage": cs.coverage_level}
    )

    return {
        "message": f"Course skill {review.status} successfully.",
        "course_skill_id": cs.id,
        "status": cs.status,
        "coverage_level": cs.coverage_level
    }
