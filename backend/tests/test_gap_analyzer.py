import pytest
from backend.app.nlp.gap_analyzer import default_gap_analyzer

def test_unweighted_and_weighted_gap_calculation():
    job_skills = [
        {"canonical_name": "Python", "importance_weight": 5.0, "required_proficiency": "advanced"},
        {"canonical_name": "FastAPI", "importance_weight": 4.0, "required_proficiency": "intermediate"},
        {"canonical_name": "Docker & Containerization", "importance_weight": 4.0, "required_proficiency": "intermediate"},
        {"canonical_name": "SQL & Relational Databases", "importance_weight": 3.0, "required_proficiency": "intermediate"}
    ]
    # Total weight = 5 + 4 + 4 + 3 = 16.0

    student_skills = [
        {"canonical_name": "Python", "proficiency_level": "advanced", "evidence_source": "coursework", "verified": True},
        # FastAPI: student only has beginner proficiency (below intermediate required) -> partially demonstrated (c_i = 0.5)
        {"canonical_name": "FastAPI", "proficiency_level": "beginner", "evidence_source": "project", "verified": True},
        {"canonical_name": "SQL & Relational Databases", "proficiency_level": "intermediate", "evidence_source": "coursework", "verified": True}
        # Docker is completely missing -> c_i = 0.0
    ]

    analysis = default_gap_analyzer.analyze_student_gap(job_skills, student_skills)

    # Check categorization
    assert len(analysis["demonstrated"]) == 2  # Python, SQL
    assert len(analysis["partially_demonstrated"]) == 1  # FastAPI
    assert len(analysis["missing"]) == 1  # Docker

    # Unweighted coverage: (2 full + 0.5 partial) / 4 = 2.5 / 4 = 62.5%
    assert analysis["unweighted_coverage"] == 62.5
    assert analysis["unweighted_gap"] == 37.5

    # Weighted coverage:
    # Python (5.0 * 1.0) = 5.0
    # FastAPI (4.0 * 0.5) = 2.0
    # Docker (4.0 * 0.0) = 0.0
    # SQL (3.0 * 1.0) = 3.0
    # Sum w_i c_i = 5.0 + 2.0 + 0.0 + 3.0 = 10.0
    # Weighted coverage = (10.0 / 16.0) * 100 = 62.5%
    assert analysis["weighted_coverage"] == 62.5
    assert analysis["weighted_gap"] == 37.5

def test_recommendation_ranking_priority():
    job_skills = [
        {"canonical_name": "Python", "importance_weight": 5.0, "required_proficiency": "intermediate"},
        {"canonical_name": "Docker & Containerization", "importance_weight": 5.0, "required_proficiency": "intermediate"},
        {"canonical_name": "Git & Version Control", "importance_weight": 2.0, "required_proficiency": "intermediate"}
    ]
    student_skills = [
        {"canonical_name": "Python", "proficiency_level": "intermediate", "evidence_source": "coursework", "verified": True}
    ]
    # Gaps: Docker (missing, weight 5.0), Git (missing, weight 2.0)

    analysis = default_gap_analyzer.analyze_student_gap(job_skills, student_skills)

    catalog = [
        {"resource_id": "r1", "title": "Git Basics", "skill_name": "Git & Version Control", "provider": "Coursera"},
        {"resource_id": "r2", "title": "Mastering Docker", "skill_name": "Docker & Containerization", "provider": "FreeCodeCamp"}
    ]

    ranked = default_gap_analyzer.rank_recommendations(analysis, catalog)

    assert len(ranked) == 2
    # Docker has higher importance weight (5.0 vs 2.0), so it must be ranked #1
    assert ranked[0]["resource_id"] == "r2"
    assert ranked[0]["rank"] == 1
    assert ranked[1]["resource_id"] == "r1"
    assert ranked[1]["rank"] == 2
