import json
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.db.models import Student, JobRole, StudentSkill, Skill, GapResult, User, UserRole
from backend.app.api.deps import get_current_user, require_role
from backend.app.nlp.gap_analyzer import default_gap_analyzer

router = APIRouter(prefix="/gap-analysis", tags=["Student Skill-Gap Analysis"])

class GapAnalysisRequest(BaseModel):
    job_id: str
    student_id: Optional[str] = None  # Optional if logged in as student

class AddStudentSkillEvidenceRequest(BaseModel):
    skill_name: str
    proficiency_level: str = "intermediate"  # beginner, intermediate, advanced
    evidence_source: str = "project"  # coursework, project, certification, assessment
    evidence_details: Optional[str] = "Student project / repository evidence"

@router.post("/student/analyze")
def analyze_student_skill_gap(
    request: GapAnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Evaluates individual student skills against job profile requirements (FR-05).
    Calculates:
    - Unweighted Coverage & Gap %
    - Weighted Coverage & Gap % (wi in [1, 5], ci in {1.0, 0.5, 0.0})
    - Categorized skills: Demonstrated, Partially Demonstrated, Missing.
    """
    # Determine student ID
    target_student_id = request.student_id
    if not target_student_id:
        if current_user.student_profile:
            target_student_id = current_user.student_profile.student_id
        else:
            raise HTTPException(
                status_code=400,
                detail="Student ID is required when not logged in as a student."
            )

    student = db.query(Student).filter(Student.student_id == target_student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student record not found.")

    job_role = db.query(JobRole).filter(JobRole.job_id == request.job_id).first()
    if not job_role:
        raise HTTPException(status_code=404, detail="Target job role not found.")

    # Check if student has any evidence
    student_skills_db = student.skills
    if not student_skills_db:
        # Flow from SRS Section 8.1 Alternative Flow:
        # "If student skill evidence is missing, the system shall explain that a personalized
        # competency assessment cannot yet be completed."
        return {
            "status": "NO_EVIDENCE",
            "message": "Personalized competency assessment cannot yet be completed because no student skill evidence has been submitted or verified. Please add coursework or project evidence.",
            "student_id": student.student_id,
            "job_id": job_role.job_id,
            "job_title": job_role.title,
            "unweighted_coverage": 0.0,
            "unweighted_gap": 100.0,
            "weighted_coverage": 0.0,
            "weighted_gap": 100.0,
            "demonstrated": [],
            "partially_demonstrated": [],
            "missing": [
                {
                    "canonical_name": js.skill.canonical_name if js.skill else "Unknown",
                    "category": js.skill.category if js.skill else "General",
                    "importance_weight": js.importance_weight,
                    "required_proficiency": js.required_proficiency,
                    "coverage_score": 0.0
                }
                for js in job_role.skills
            ]
        }

    # Format job skills
    job_skills_data = [
        {
            "canonical_name": js.skill.canonical_name if js.skill else "Unknown",
            "category": js.skill.category if js.skill else "General",
            "importance_weight": js.importance_weight,
            "required_proficiency": js.required_proficiency
        }
        for js in job_role.skills
    ]

    # Format student skills
    student_skills_data = [
        {
            "canonical_name": ss.skill.canonical_name if ss.skill else "Unknown",
            "proficiency_level": ss.proficiency_level,
            "evidence_source": ss.evidence_source,
            "verified": ss.verified
        }
        for ss in student_skills_db
    ]

    # Run Analysis
    gap_result = default_gap_analyzer.analyze_student_gap(
        job_skills=job_skills_data,
        student_skills=student_skills_data
    )

    # Persist or update GapResult
    existing_gap = db.query(GapResult).filter(
        GapResult.student_id == student.student_id,
        GapResult.job_id == job_role.job_id
    ).first()

    details_payload = json.dumps({
        "demonstrated": gap_result["demonstrated"],
        "partially_demonstrated": gap_result["partially_demonstrated"],
        "missing": gap_result["missing"]
    })

    if existing_gap:
        existing_gap.unweighted_coverage = gap_result["unweighted_coverage"]
        existing_gap.weighted_coverage = gap_result["weighted_coverage"]
        existing_gap.gap_score = gap_result["weighted_gap"]
        existing_gap.details_json = details_payload
        existing_gap.evaluated_at = datetime.utcnow()
    else:
        new_gap = GapResult(
            student_id=student.student_id,
            job_id=job_role.job_id,
            unweighted_coverage=gap_result["unweighted_coverage"],
            weighted_coverage=gap_result["weighted_coverage"],
            gap_score=gap_result["weighted_gap"],
            details_json=details_payload
        )
        db.add(new_gap)

    db.commit()

    return {
        "status": "SUCCESS",
        "student_id": student.student_id,
        "student_name": student.user.name if student.user else "Student",
        "job_id": job_role.job_id,
        "job_title": job_role.title,
        "company_name": job_role.company_name,
        "unweighted_coverage": gap_result["unweighted_coverage"],
        "unweighted_gap": gap_result["unweighted_gap"],
        "weighted_coverage": gap_result["weighted_coverage"],
        "weighted_gap": gap_result["weighted_gap"],
        "demonstrated": gap_result["demonstrated"],
        "partially_demonstrated": gap_result["partially_demonstrated"],
        "missing": gap_result["missing"],
        "demonstrated_count": gap_result["demonstrated_count"],
        "partial_count": gap_result["partial_count"],
        "missing_count": gap_result["missing_count"],
        "total_required_skills": gap_result["total_required_skills"]
    }

@router.get("/student/skills")
def get_student_skills(
    student_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve verified and demonstrated skills for a student."""
    target_student_id = student_id
    if not target_student_id:
        if current_user.student_profile:
            target_student_id = current_user.student_profile.student_id
        else:
            raise HTTPException(status_code=400, detail="Student ID required.")

    student = db.query(Student).filter(Student.student_id == target_student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found.")

    return [
        {
            "id": ss.id,
            "skill_id": ss.skill_id,
            "canonical_name": ss.skill.canonical_name if ss.skill else "Unknown",
            "category": ss.skill.category if ss.skill else "General",
            "proficiency_level": ss.proficiency_level,
            "evidence_source": ss.evidence_source,
            "verified": ss.verified
        }
        for ss in student.skills
    ]

@router.post("/student/skills")
def add_student_skill(
    request: AddStudentSkillEvidenceRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add demonstrated skill evidence for a student."""
    if not current_user.student_profile:
        raise HTTPException(status_code=400, detail="Only student users can add personal skill evidence.")

    student = current_user.student_profile

    # Look up canonical skill
    skill = db.query(Skill).filter(Skill.canonical_name.ilike(request.skill_name.strip())).first()
    if not skill:
        skill = Skill(
            canonical_name=request.skill_name.strip(),
            category="Technical Skills",
            aliases=json.dumps([request.skill_name.lower()]),
            description="Student submitted skill evidence"
        )
        db.add(skill)
        db.flush()

    # Check if already present
    existing = db.query(StudentSkill).filter(
        StudentSkill.student_id == student.student_id,
        StudentSkill.skill_id == skill.skill_id
    ).first()

    if existing:
        existing.proficiency_level = request.proficiency_level
        existing.evidence_source = request.evidence_source
    else:
        db.add(StudentSkill(
            student_id=student.student_id,
            skill_id=skill.skill_id,
            proficiency_level=request.proficiency_level,
            evidence_source=request.evidence_source,
            verified=True  # Auto-verified in prototype
        ))

    db.commit()

    return {"message": f"Skill '{skill.canonical_name}' added to student profile."}
