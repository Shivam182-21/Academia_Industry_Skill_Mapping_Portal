"""
Database Seeder for Academia–Industry Skill Mapping and Placement Portal.
Populates realistic demonstration data for SIH 2026 - Group G29.
"""

import json
from sqlalchemy.orm import Session
from backend.app.db.database import engine, Base, SessionLocal
from backend.app.db.models import (
    User, UserRole, Student, Cohort, Course, CurriculumContent,
    Skill, CourseSkill, JobRole, JobSkill, StudentSkill,
    SkillMapping, LearningResource, GapResult, EvaluationRecord, AuditLog
)
from backend.app.core.security import get_password_hash
from backend.app.nlp.taxonomy import CANONICAL_SKILLS
from backend.app.nlp.evaluator import default_evaluator

def seed_database():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    try:
        # Check if already seeded
        if db.query(User).filter_by(email="student@portal.edu").first():
            print("Database already contains seed data. Skipping re-seeding.")
            return

        print("Seeding canonical skills catalog...")
        skill_map = {}
        for item in CANONICAL_SKILLS:
            skill = Skill(
                canonical_name=item["canonical_name"],
                category=item["category"],
                aliases=json.dumps(item["aliases"]),
                description=item["description"]
            )
            db.add(skill)
            db.flush()
            skill_map[item["canonical_name"]] = skill

        print("Seeding cohorts...")
        cohort_cse = Cohort(
            name="B.Tech Computer Science & Engineering (2023–2027)",
            department="Computer Science & Engineering",
            graduation_year=2027
        )
        cohort_ayush = Cohort(
            name="B.Tech Ayush Informatics & HealthTech (2023–2027)",
            department="Ayush Informatics & HealthTech",
            graduation_year=2027
        )
        db.add_all([cohort_cse, cohort_ayush])
        db.flush()

        print("Seeding users across all 5 roles...")
        # 1. Students (including Team Members from Group G29)
        u_shivam = User(
            name="Shivam Chandel",
            email="shivam.student@portal.edu",
            password_hash=get_password_hash("student123"),
            role=UserRole.STUDENT
        )
        u_shivam_gmail = User(
            name="Shivam Chandel",
            email="chandels0708@gmail.com",
            password_hash=get_password_hash("student123"),
            role=UserRole.STUDENT
        )
        u_nayneet = User(
            name="Navneet Kumar",
            email="nayneet.student@portal.edu",
            password_hash=get_password_hash("student123"),
            role=UserRole.STUDENT
        )
        u_student_generic = User(
            name="Aarav Sharma",
            email="student@portal.edu",
            password_hash=get_password_hash("student123"),
            role=UserRole.STUDENT
        )
        
        # 2. Faculty
        u_faculty = User(
            name="Dr. Rajesh Sharma",
            email="faculty@portal.edu",
            password_hash=get_password_hash("faculty123"),
            role=UserRole.FACULTY
        )

        # 3. Placement Officer
        u_placement = User(
            name="Prof. Sunita Verma",
            email="placement@portal.edu",
            password_hash=get_password_hash("placement123"),
            role=UserRole.PLACEMENT_OFFICER
        )

        # 4. Industry Partner / Employer
        u_employer = User(
            name="Vikramaditya Rao (TechCorp)",
            email="partner@techcorp.com",
            password_hash=get_password_hash("partner123"),
            role=UserRole.EMPLOYER
        )

        # 5. Admin
        u_admin = User(
            name="System Administrator",
            email="admin@portal.edu",
            password_hash=get_password_hash("admin123"),
            role=UserRole.ADMIN
        )

        db.add_all([u_shivam, u_shivam_gmail, u_nayneet, u_student_generic, u_faculty, u_placement, u_employer, u_admin])
        db.flush()

        # Seed student profiles
        student_shivam = Student(
            user_id=u_shivam.user_id,
            cohort_id=cohort_cse.cohort_id,
            department="Computer Science & Engineering",
            roll_number="RK3P25ORA20",
            registration_number="12522547"
        )
        student_nayneet = Student(
            user_id=u_nayneet.user_id,
            cohort_id=cohort_cse.cohort_id,
            department="Computer Science & Engineering",
            roll_number="RK3P25ORB37",
            registration_number="12518540"
        )
        student_generic = Student(
            user_id=u_student_generic.user_id,
            cohort_id=cohort_ayush.cohort_id,
            department="Ayush Informatics & HealthTech",
            roll_number="AY3P25ORC11",
            registration_number="12519988"
        )
        db.add_all([student_shivam, student_nayneet, student_generic])
        db.flush()

        print("Seeding academic courses & curriculum content...")
        # Course 1: DSA
        c_dsa = Course(
            course_code="CS301",
            course_name="Data Structures and Algorithms",
            semester=3,
            department="Computer Science & Engineering",
            cohort_id=cohort_cse.cohort_id
        )
        db.add(c_dsa)
        db.flush()
        cc_dsa = CurriculumContent(
            course_id=c_dsa.course_id,
            description="Fundamental data structures including arrays, linked lists, trees, graphs, sorting and searching algorithms, algorithmic complexity with Python implementations.",
            learning_outcomes="Understand Big-O complexity, implement graph traversals (BFS/DFS), write clean algorithmic code in Python.",
            uploaded_by=u_faculty.user_id
        )
        db.add(cc_dsa)

        # Course 2: DBMS
        c_dbms = Course(
            course_code="CS302",
            course_name="Database Management Systems & SQL",
            semester=4,
            department="Computer Science & Engineering",
            cohort_id=cohort_cse.cohort_id
        )
        db.add(c_dbms)
        db.flush()
        cc_dbms = CurriculumContent(
            course_id=c_dbms.course_id,
            description="Relational database design, ER modeling, SQL querying, transactions, ACID properties, normalization, indexing with PostgreSQL.",
            learning_outcomes="Design relational schemas, optimize complex multi-table SQL queries, understand transaction isolation.",
            uploaded_by=u_faculty.user_id
        )
        db.add(cc_dbms)

        # Course 3: Web Tech
        c_web = Course(
            course_code="CS303",
            course_name="Web Technologies & REST APIs",
            semester=5,
            department="Computer Science & Engineering",
            cohort_id=cohort_cse.cohort_id
        )
        db.add(c_web)
        db.flush()
        cc_web = CurriculumContent(
            course_id=c_web.course_id,
            description="Developing web backends with FastAPI, RESTful API design, frontend responsive styling with React.js and HTML5/CSS, Git version control.",
            learning_outcomes="Build asynchronous REST APIs, connect frontend React clients, collaborate via Git branches.",
            uploaded_by=u_faculty.user_id
        )
        db.add(cc_web)

        # Course 4: Ayush Health Informatics
        c_ayush = Course(
            course_code="AI301",
            course_name="Ayush Health Informatics & Clinical Data",
            semester=5,
            department="Ayush Informatics & HealthTech",
            cohort_id=cohort_ayush.cohort_id
        )
        db.add(c_ayush)
        db.flush()
        cc_ayush = CurriculumContent(
            course_id=c_ayush.course_id,
            description="Digital healthcare records (EHR/EMR), HL7 FHIR standards, machine learning on clinical records, herbal database analysis using Python and SQL.",
            learning_outcomes="Analyze health data, query clinical repositories, apply machine learning models to healthcare datasets.",
            uploaded_by=u_faculty.user_id
        )
        db.add(cc_ayush)
        db.flush()

        # Link Course Skills
        cs_links = [
            (c_dsa, "Data Structures & Algorithms", 1.0, "Core syllabus topic in CS301 Unit 1-4"),
            (c_dsa, "Python", 0.8, "Laboratory implementations in Python"),
            (c_dbms, "SQL & Relational Databases", 1.0, "Complete coverage of relational schema & SQL queries in CS302"),
            (c_web, "RESTful APIs & Web Services", 1.0, "Building REST endpoints with FastAPI in CS303"),
            (c_web, "FastAPI", 0.9, "Hands-on API framework chosen in CS303"),
            (c_web, "React.js", 0.85, "Component UI development in CS303 Unit 4"),
            (c_web, "JavaScript", 0.9, "ES6+ programming syntax in web lab"),
            (c_web, "Git & Version Control", 0.95, "Version control mandatory for course project submission"),
            (c_web, "HTML5 & Modern CSS", 1.0, "Web fundamentals in CS303 Unit 1"),
            (c_ayush, "Health Informatics & EHR Standards", 1.0, "Primary focus of AI301 Ayush Informatics curriculum"),
            (c_ayush, "Machine Learning", 0.8, "Predictive modeling on health datasets Unit 5"),
            (c_ayush, "Python", 0.9, "Data analysis script assignments"),
            (c_ayush, "SQL & Relational Databases", 0.8, "Querying medical records databases")
        ]
        for course_obj, skill_name, cov, snippet in cs_links:
            if skill_name in skill_map:
                db.add(CourseSkill(
                    course_id=course_obj.course_id,
                    skill_id=skill_map[skill_name].skill_id,
                    coverage_level=cov,
                    evidence_snippet=snippet,
                    status="approved",
                    approved_by=u_faculty.user_id
                ))
        db.flush()

        print("Seeding industry job roles & skill requirements...")
        # Role 1: Full Stack Developer
        job_fsd = JobRole(
            title="Full Stack Software Engineer",
            company_name="TechCorp Solutions",
            industry="Information Technology & Software Services",
            experience_level="Entry-Level / 0–2 Years",
            description="Looking for a Full Stack Software Engineer to build scalable cloud web applications using modern web stacks.",
            created_by=u_employer.user_id
        )
        # Role 2: Ayush Health Data Analyst
        job_ayush = JobRole(
            title="Ayush Health Informatics & AI Specialist",
            company_name="Ayush Digital Mission / National Health Portal",
            industry="Healthcare Technology & Informatics",
            experience_level="Entry-Level / Graduate",
            description="Seeking an informatics analyst to develop intelligent data mapping systems for clinical Ayush research records.",
            created_by=u_employer.user_id
        )
        # Role 3: Cloud & DevOps Engineer
        job_devops = JobRole(
            title="Junior DevOps & Cloud Platform Engineer",
            company_name="CloudMatrix Systems",
            industry="Cloud Computing & Infrastructure",
            experience_level="Fresher / 0–1 Years",
            description="Manage containerized deployments, automated CI/CD pipelines, and cloud Linux infrastructure.",
            created_by=u_employer.user_id
        )
        db.add_all([job_fsd, job_ayush, job_devops])
        db.flush()

        # Job Required Skills with importance weights w_i in [1, 5]
        js_fsd_data = [
            ("Python", 5.0, "advanced"),
            ("FastAPI", 4.0, "intermediate"),
            ("SQL & Relational Databases", 5.0, "advanced"),
            ("React.js", 4.5, "intermediate"),
            ("JavaScript", 4.5, "intermediate"),
            ("RESTful APIs & Web Services", 5.0, "advanced"),
            ("Docker & Containerization", 4.0, "intermediate"),      # Likely gap for student!
            ("Continuous Integration & Deployment (CI/CD)", 3.5, "beginner"),  # Likely gap!
            ("Git & Version Control", 4.0, "intermediate"),
            ("Software Testing & QA", 3.5, "intermediate")           # Likely gap!
        ]
        for sname, weight, prof in js_fsd_data:
            if sname in skill_map:
                db.add(JobSkill(
                    job_id=job_fsd.job_id,
                    skill_id=skill_map[sname].skill_id,
                    importance_weight=weight,
                    required_proficiency=prof
                ))

        js_ayush_data = [
            ("Health Informatics & EHR Standards", 5.0, "advanced"),
            ("Python", 5.0, "advanced"),
            ("Machine Learning", 4.5, "intermediate"),
            ("Natural Language Processing (NLP)", 4.0, "intermediate"), # Gap!
            ("SQL & Relational Databases", 4.0, "intermediate"),
            ("Git & Version Control", 3.0, "beginner")
        ]
        for sname, weight, prof in js_ayush_data:
            if sname in skill_map:
                db.add(JobSkill(
                    job_id=job_ayush.job_id,
                    skill_id=skill_map[sname].skill_id,
                    importance_weight=weight,
                    required_proficiency=prof
                ))
        db.flush()

        print("Seeding student demonstrated skills with verified evidence...")
        # Shivam Chandel demonstrated skills
        shivam_skills = [
            ("Python", "advanced", "coursework", True),
            ("Data Structures & Algorithms", "advanced", "coursework", True),
            ("SQL & Relational Databases", "intermediate", "coursework", True),
            ("RESTful APIs & Web Services", "intermediate", "project", True),
            ("FastAPI", "intermediate", "project", True),
            ("React.js", "intermediate", "project", True),
            ("JavaScript", "intermediate", "coursework", True),
            ("Git & Version Control", "intermediate", "coursework", True),
            ("HTML5 & Modern CSS", "advanced", "coursework", True)
            # Notice: Docker, CI/CD, Software Testing are missing! Real gap!
        ]
        for sname, prof, src, ver in shivam_skills:
            if sname in skill_map:
                db.add(StudentSkill(
                    student_id=student_shivam.student_id,
                    skill_id=skill_map[sname].skill_id,
                    proficiency_level=prof,
                    evidence_source=src,
                    verified=ver,
                    verified_by=u_faculty.user_id
                ))

        # Navneet Kumar demonstrated skills
        nayneet_skills = [
            ("Python", "advanced", "coursework", True),
            ("SQL & Relational Databases", "advanced", "project", True),
            ("Data Structures & Algorithms", "intermediate", "coursework", True),
            ("Machine Learning", "intermediate", "project", True),
            ("Health Informatics & EHR Standards", "intermediate", "coursework", True),
            ("Git & Version Control", "intermediate", "coursework", True)
        ]
        for sname, prof, src, ver in nayneet_skills:
            if sname in skill_map:
                db.add(StudentSkill(
                    student_id=student_nayneet.student_id,
                    skill_id=skill_map[sname].skill_id,
                    proficiency_level=prof,
                    evidence_source=src,
                    verified=ver,
                    verified_by=u_faculty.user_id
                ))
        db.flush()

        print("Seeding curated learning resources...")
        learning_resources_data = [
            {
                "title": "Docker for Developers: From Containers to Production",
                "provider": "FreeCodeCamp / Docker Official",
                "url": "https://docs.docker.com/get-started/",
                "skill_name": "Docker & Containerization",
                "resource_type": "Course & Hands-on Lab",
                "difficulty": "Intermediate"
            },
            {
                "title": "Automated Testing in Python with PyTest & GitHub Actions CI/CD",
                "provider": "Coursera & NPTEL",
                "url": "https://www.coursera.org/learn/test-driven-development",
                "skill_name": "Software Testing & QA",
                "resource_type": "Certification Course",
                "difficulty": "Intermediate"
            },
            {
                "title": "Continuous Integration and Continuous Delivery (CI/CD) Foundations",
                "provider": "edX / Linux Foundation",
                "url": "https://www.edx.org/learn/devops",
                "skill_name": "Continuous Integration & Deployment (CI/CD)",
                "resource_type": "Course",
                "difficulty": "Beginner to Intermediate"
            },
            {
                "title": "Natural Language Processing with Python and spaCy",
                "provider": "DeepLearning.AI / Coursera",
                "url": "https://www.deeplearning.ai/courses/natural-language-processing-specialization/",
                "skill_name": "Natural Language Processing (NLP)",
                "resource_type": "Specialization",
                "difficulty": "Advanced"
            },
            {
                "title": "Cloud Computing Infrastructure Fundamentals (AWS/Azure)",
                "provider": "NPTEL / Swayam",
                "url": "https://nptel.ac.in/courses/106/105/106105167/",
                "skill_name": "Cloud Computing (AWS/GCP/Azure)",
                "resource_type": "Academic Certification",
                "difficulty": "Intermediate"
            }
        ]
        for res in learning_resources_data:
            sname = res["skill_name"]
            if sname in skill_map:
                db.add(LearningResource(
                    title=res["title"],
                    provider=res["provider"],
                    url=res["url"],
                    skill_id=skill_map[sname].skill_id,
                    resource_type=res["resource_type"],
                    difficulty=res["difficulty"]
                ))
        db.flush()

        print("Running initial model evaluation benchmark to record ground truth metrics...")
        eval_result = default_evaluator.evaluate_extraction_on_dataset()
        nlp_pipeline_metrics = eval_result["proposed_nlp_pipeline"]
        baseline_metrics = eval_result["keyword_baseline"]

        # Record proposed NLP metrics
        for metric in ["precision", "recall", "f1_score", "mapping_precision", "gap_coverage"]:
            db.add(EvaluationRecord(
                dataset_version=eval_result["dataset_info"]["version"],
                model_type="NLP_Semantic_Pipeline",
                metric_name=metric,
                metric_value=nlp_pipeline_metrics[metric],
                sample_count=eval_result["dataset_info"]["sample_count"],
                details_json=json.dumps(eval_result["error_samples"])
            ))

        # Record baseline metrics
        for metric in ["precision", "recall", "f1_score"]:
            db.add(EvaluationRecord(
                dataset_version=eval_result["dataset_info"]["version"],
                model_type="Keyword_Baseline",
                metric_name=metric,
                metric_value=baseline_metrics[metric],
                sample_count=eval_result["dataset_info"]["sample_count"],
                details_json=None
            ))

        # Initial audit log
        db.add(AuditLog(
            user_id=u_admin.user_id,
            action="SYSTEM_INIT_SEED",
            entity_type="SYSTEM",
            entity_id="ALL",
            details="Populated seed cohorts, canonical skills, users, syllabi, job roles, and ground truth benchmark results."
        ))

        db.commit()
        print("Database successfully seeded with realistic demonstration data!")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
