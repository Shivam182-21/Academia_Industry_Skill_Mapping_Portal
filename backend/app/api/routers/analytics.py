import io
import csv
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from collections import Counter

from backend.app.db.database import get_db
from backend.app.db.models import Cohort, Student, JobRole, StudentSkill, Skill, User, UserRole
from backend.app.api.deps import get_current_user, require_role
from backend.app.nlp.gap_analyzer import default_gap_analyzer

router = APIRouter(prefix="/analytics", tags=["Cohort Analytics & Placement Reporting"])

@router.get("/cohorts")
def list_cohorts(db: Session = Depends(get_db)):
    """List all cohorts with student counts."""
    cohorts = db.query(Cohort).all()
    results = []
    for c in cohorts:
        results.append({
            "cohort_id": c.cohort_id,
            "name": c.name,
            "department": c.department,
            "graduation_year": c.graduation_year,
            "student_count": len(c.students)
        })
    return results

@router.get("/cohort/{cohort_id}/summary")
def get_cohort_readiness_summary(
    cohort_id: str,
    job_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Cohort-wide placement readiness analysis (FR-07).
    Calculates readiness distributions:
    - High Readiness (>= 75% coverage)
    - Moderate Readiness (50% to 74% coverage)
    - Needs Upskilling (< 50% coverage)
    - Average cohort coverage %
    """
    cohort = db.query(Cohort).filter(Cohort.cohort_id == cohort_id).first()
    if not cohort:
        raise HTTPException(status_code=404, detail="Cohort not found.")

    # Target job role or default to first job role
    if job_id:
        job = db.query(JobRole).filter(JobRole.job_id == job_id).first()
    else:
        job = db.query(JobRole).first()

    if not job:
        raise HTTPException(status_code=404, detail="No job role available for benchmark analysis.")

    job_skills_data = [
        {
            "canonical_name": js.skill.canonical_name if js.skill else "Unknown",
            "category": js.skill.category if js.skill else "General",
            "importance_weight": js.importance_weight,
            "required_proficiency": js.required_proficiency
        }
        for js in job.skills
    ]

    students = cohort.students
    total_students = len(students)

    high_readiness = []
    moderate_readiness = []
    needs_upskilling = []
    coverage_sum = 0.0

    skill_gap_counter = Counter()

    for s in students:
        s_skills_data = [
            {
                "canonical_name": ss.skill.canonical_name if ss.skill else "Unknown",
                "proficiency_level": ss.proficiency_level,
                "evidence_source": ss.evidence_source,
                "verified": ss.verified
            }
            for ss in s.skills
        ]

        analysis = default_gap_analyzer.analyze_student_gap(job_skills_data, s_skills_data)
        cov = analysis["weighted_coverage"]
        coverage_sum += cov

        student_summary = {
            "student_id": s.student_id,
            "name": s.user.name if s.user else "Student",
            "roll_number": s.roll_number,
            "registration_number": s.registration_number,
            "weighted_coverage": cov,
            "unweighted_coverage": analysis["unweighted_coverage"],
            "missing_skills_count": len(analysis["missing"]),
            "demonstrated_count": len(analysis["demonstrated"])
        }

        if cov >= 75.0:
            high_readiness.append(student_summary)
        elif cov >= 50.0:
            moderate_readiness.append(student_summary)
        else:
            needs_upskilling.append(student_summary)

        # Count missing skills for shortage heatmap
        for m in analysis["missing"]:
            skill_gap_counter[m["canonical_name"]] += 1

    avg_coverage = round(coverage_sum / total_students, 2) if total_students > 0 else 0.0

    # Format top skill shortages
    shortage_distribution = [
        {
            "skill_name": skill_name,
            "missing_students_count": count,
            "shortage_percentage": round(count / total_students * 100, 1) if total_students > 0 else 0
        }
        for skill_name, count in skill_gap_counter.most_common(8)
    ]

    return {
        "cohort_id": cohort.cohort_id,
        "cohort_name": cohort.name,
        "department": cohort.department,
        "graduation_year": cohort.graduation_year,
        "target_job_id": job.job_id,
        "target_job_title": job.title,
        "total_students": total_students,
        "average_coverage": avg_coverage,
        "distribution": {
            "high_readiness_count": len(high_readiness),
            "high_readiness_pct": round(len(high_readiness) / total_students * 100, 1) if total_students else 0,
            "moderate_readiness_count": len(moderate_readiness),
            "moderate_readiness_pct": round(len(moderate_readiness) / total_students * 100, 1) if total_students else 0,
            "needs_upskilling_count": len(needs_upskilling),
            "needs_upskilling_pct": round(len(needs_upskilling) / total_students * 100, 1) if total_students else 0
        },
        "shortage_distribution": shortage_distribution,
        "students": {
            "high_readiness": high_readiness,
            "moderate_readiness": moderate_readiness,
            "needs_upskilling": needs_upskilling
        }
    }

@router.get("/export/cohort/{cohort_id}")
def export_cohort_report(
    cohort_id: str,
    format: str = "csv",
    job_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Downloadable Cohort Placement Readiness Report (FR-07).
    Supports format=csv and format=pdf.
    """
    summary_data = get_cohort_readiness_summary(cohort_id=cohort_id, job_id=job_id, db=db)

    if format.lower() == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header info
        writer.writerow(["ACADEMIA-INDUSTRY SKILL MAPPING & PLACEMENT READINESS REPORT"])
        writer.writerow(["Cohort:", summary_data["cohort_name"]])
        writer.writerow(["Department:", summary_data["department"]])
        writer.writerow(["Graduation Year:", summary_data["graduation_year"]])
        writer.writerow(["Target Job Role:", summary_data["target_job_title"]])
        writer.writerow(["Average Coverage %:", f"{summary_data['average_coverage']}%"])
        writer.writerow(["Generated At:", datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")])
        writer.writerow([])

        # Table: Student Readiness Breakdown
        writer.writerow([
            "Roll Number", "Registration Number", "Student Name",
            "Readiness Tier", "Weighted Coverage (%)", "Unweighted Coverage (%)",
            "Demonstrated Skills", "Missing Skills Count"
        ])

        for tier_name, tier_list in [
            ("High Readiness (>=75%)", summary_data["students"]["high_readiness"]),
            ("Moderate Readiness (50-74%)", summary_data["students"]["moderate_readiness"]),
            ("Needs Upskilling (<50%)", summary_data["students"]["needs_upskilling"])
        ]:
            for s in tier_list:
                writer.writerow([
                    s["roll_number"] or "N/A",
                    s["registration_number"] or "N/A",
                    s["name"],
                    tier_name,
                    f"{s['weighted_coverage']}%",
                    f"{s['unweighted_coverage']}%",
                    s["demonstrated_count"],
                    s["missing_skills_count"]
                ])

        writer.writerow([])
        writer.writerow(["AGGREGATE COHORT SKILL SHORTAGES"])
        writer.writerow(["Skill Name", "Students Missing", "Shortage % of Cohort"])
        for shortage in summary_data["shortage_distribution"]:
            writer.writerow([
                shortage["skill_name"],
                shortage["missing_students_count"],
                f"{shortage['shortage_percentage']}%"
            ])

        output.seek(0)
        filename = f"cohort_report_{cohort_id[:8]}_{datetime.utcnow().strftime('%Y%m%d')}.csv"
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    else:
        # Generate formatted printable summary
        return summary_data
