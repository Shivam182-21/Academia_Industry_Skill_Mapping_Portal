import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_tc01_login_valid_credentials():
    """TC-01: Log in with valid credentials reaches the correct dashboard."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "student@portal.edu", "password": "student123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["role"] == "student"

def test_tc02_login_invalid_credentials():
    """TC-02: Log in with invalid credentials returns 401 unauthorized."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "student@portal.edu", "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert "detail" in response.json()

def test_tc03_courses_listing():
    """TC-03: Curriculum courses listing with extracted skills."""
    response = client.get("/api/v1/curriculum/courses")
    assert response.status_code == 200
    courses = response.json()
    assert len(courses) >= 3
    assert any(c["course_code"] == "CS301" for c in courses)

def test_tc05_jobs_listing():
    """TC-05: Industry job roles listing with requirements and weights."""
    response = client.get("/api/v1/jobs/roles")
    assert response.status_code == 200
    roles = response.json()
    assert len(roles) >= 2
    assert any("Full Stack" in r["title"] for r in roles)

def test_tc06_curriculum_mapping():
    """TC-06: Compare curriculum and job skills with exact and semantic matches."""
    roles = client.get("/api/v1/jobs/roles").json()
    job_id = roles[0]["job_id"]
    
    response = client.post(
        "/api/v1/mapping/curriculum-to-job",
        json={"job_id": job_id}
    )
    assert response.status_code == 200
    mapping = response.json()
    assert "matched_curriculum_skills" in mapping
    assert "unmapped_industry_skills" in mapping
    assert "weighted_coverage" in mapping
    assert mapping["total_required_skills"] > 0

def test_tc08_student_gap_analysis_and_recommendations():
    """TC-08: Analyze student skill gap and get ranked recommendations."""
    # 1. Login as student
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": "shivam.student@portal.edu", "password": "student123"}
    )
    token = login_res.json()["access_token"]
    student_id = login_res.json()["student_id"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Get a job role
    roles = client.get("/api/v1/jobs/roles").json()
    job_id = roles[0]["job_id"]

    # 3. Analyze gap
    gap_res = client.post(
        "/api/v1/gap-analysis/student/analyze",
        json={"job_id": job_id, "student_id": student_id},
        headers=headers
    )
    assert gap_res.status_code == 200
    gap_data = gap_res.json()
    assert "weighted_coverage" in gap_data
    assert "missing" in gap_data

    # 4. Request recommendations
    rec_res = client.get(
        f"/api/v1/recommendations/for-job/{job_id}?student_id={student_id}",
        headers=headers
    )
    assert rec_res.status_code == 200
    rec_data = rec_res.json()
    assert "recommendations" in rec_data
    assert len(rec_data["recommendations"]) > 0

def test_tc09_tc10_cohort_analytics_and_export():
    """TC-09 & TC-10: View cohort analytics and export CSV report."""
    cohorts = client.get("/api/v1/analytics/cohorts").json()
    assert len(cohorts) > 0
    cohort_id = cohorts[0]["cohort_id"]

    # Summary
    summary = client.get(f"/api/v1/analytics/cohort/{cohort_id}/summary").json()
    assert "average_coverage" in summary
    assert "distribution" in summary
    assert "shortage_distribution" in summary

    # CSV Export
    csv_res = client.get(f"/api/v1/analytics/export/cohort/{cohort_id}?format=csv")
    assert csv_res.status_code == 200
    assert "text/csv" in csv_res.headers["content-type"]
    assert "ACADEMIA-INDUSTRY SKILL MAPPING" in csv_res.text

def test_tc11_access_restricted_data():
    """TC-11: Access restricted administrative data without admin role is denied."""
    # Login as student
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": "student@portal.edu", "password": "student123"}
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Attempt to view audit logs (Admin only)
    admin_res = client.get("/api/v1/admin/audit-logs", headers=headers)
    assert admin_res.status_code == 403

def test_tc12_model_evaluation_metrics():
    """TC-12: Evaluate against labeled dataset; Precision, Recall, F1 reported."""
    eval_res = client.get("/api/v1/evaluation/results")
    assert eval_res.status_code == 200
    data = eval_res.json()
    assert "proposed_nlp_pipeline" in data
    assert "keyword_baseline" in data
    assert data["proposed_nlp_pipeline"]["f1_score"] > 0
