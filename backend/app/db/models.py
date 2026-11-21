import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, Text, DateTime, ForeignKey, Enum
)
from sqlalchemy.orm import relationship
from backend.app.db.database import Base

def generate_uuid():
    return str(uuid.uuid4())

class UserRole:
    STUDENT = "student"
    FACULTY = "faculty"
    PLACEMENT_OFFICER = "placement_officer"
    EMPLOYER = "employer"
    ADMIN = "admin"

class User(Base):
    __tablename__ = "users"

    user_id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(150), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default=UserRole.STUDENT)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    student_profile = relationship("Student", back_populates="user", uselist=False, cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user")

class Cohort(Base):
    __tablename__ = "cohorts"

    cohort_id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(150), nullable=False)
    department = Column(String(100), nullable=False)
    graduation_year = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    students = relationship("Student", back_populates="cohort")
    courses = relationship("Course", back_populates="cohort")

class Student(Base):
    __tablename__ = "students"

    student_id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, unique=True)
    cohort_id = Column(String(36), ForeignKey("cohorts.cohort_id", ondelete="SET NULL"), nullable=True)
    department = Column(String(100), nullable=False)
    roll_number = Column(String(50), nullable=True)
    registration_number = Column(String(50), nullable=True)

    # Relationships
    user = relationship("User", back_populates="student_profile")
    cohort = relationship("Cohort", back_populates="students")
    skills = relationship("StudentSkill", back_populates="student", cascade="all, delete-orphan")
    gap_results = relationship("GapResult", back_populates="student", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="student", cascade="all, delete-orphan")

class Course(Base):
    __tablename__ = "courses"

    course_id = Column(String(36), primary_key=True, default=generate_uuid)
    course_code = Column(String(50), nullable=False, index=True)
    course_name = Column(String(200), nullable=False)
    semester = Column(Integer, nullable=False)
    department = Column(String(100), nullable=False)
    cohort_id = Column(String(36), ForeignKey("cohorts.cohort_id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    cohort = relationship("Cohort", back_populates="courses")
    curriculum_content = relationship("CurriculumContent", back_populates="course", uselist=False, cascade="all, delete-orphan")
    course_skills = relationship("CourseSkill", back_populates="course", cascade="all, delete-orphan")
    mappings = relationship("SkillMapping", back_populates="course", cascade="all, delete-orphan")

class CurriculumContent(Base):
    __tablename__ = "curriculum_content"

    content_id = Column(String(36), primary_key=True, default=generate_uuid)
    course_id = Column(String(36), ForeignKey("courses.course_id", ondelete="CASCADE"), nullable=False, unique=True)
    description = Column(Text, nullable=False)
    learning_outcomes = Column(Text, nullable=True)
    file_path = Column(String(255), nullable=True)
    uploaded_by = Column(String(36), ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    course = relationship("Course", back_populates="curriculum_content")

class Skill(Base):
    __tablename__ = "skills"

    skill_id = Column(String(36), primary_key=True, default=generate_uuid)
    canonical_name = Column(String(100), unique=True, nullable=False, index=True)
    category = Column(String(100), nullable=False)  # e.g., Programming, Database, Cloud/DevOps, Soft Skills
    aliases = Column(Text, nullable=True)  # JSON-encoded string of aliases e.g. ["JS", "ECMAScript"]
    description = Column(Text, nullable=True)

    # Relationships
    course_skills = relationship("CourseSkill", back_populates="skill")
    job_skills = relationship("JobSkill", back_populates="skill")
    student_skills = relationship("StudentSkill", back_populates="skill")
    resources = relationship("LearningResource", back_populates="skill")

class CourseSkill(Base):
    __tablename__ = "course_skills"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    course_id = Column(String(36), ForeignKey("courses.course_id", ondelete="CASCADE"), nullable=False)
    skill_id = Column(String(36), ForeignKey("skills.skill_id", ondelete="CASCADE"), nullable=False)
    coverage_level = Column(Float, default=1.0)  # 1.0 (Full), 0.5 (Partial)
    evidence_snippet = Column(Text, nullable=True)
    status = Column(String(50), default="approved")  # pending, approved, rejected
    approved_by = Column(String(36), ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True)

    # Relationships
    course = relationship("Course", back_populates="course_skills")
    skill = relationship("Skill", back_populates="course_skills")

class JobRole(Base):
    __tablename__ = "job_roles"

    job_id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(150), nullable=False, index=True)
    company_name = Column(String(150), nullable=True)
    industry = Column(String(100), nullable=False)
    experience_level = Column(String(50), default="Entry-Level / Fresher")
    description = Column(Text, nullable=False)
    created_by = Column(String(36), ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    skills = relationship("JobSkill", back_populates="job_role", cascade="all, delete-orphan")
    gap_results = relationship("GapResult", back_populates="job_role", cascade="all, delete-orphan")

class JobSkill(Base):
    __tablename__ = "job_skills"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    job_id = Column(String(36), ForeignKey("job_roles.job_id", ondelete="CASCADE"), nullable=False)
    skill_id = Column(String(36), ForeignKey("skills.skill_id", ondelete="CASCADE"), nullable=False)
    importance_weight = Column(Float, default=3.0)  # w_i in [1.0, 5.0]
    required_proficiency = Column(String(50), default="intermediate")  # beginner, intermediate, advanced

    # Relationships
    job_role = relationship("JobRole", back_populates="skills")
    skill = relationship("Skill", back_populates="job_skills")
    mappings = relationship("SkillMapping", back_populates="job_skill", cascade="all, delete-orphan")

class StudentSkill(Base):
    __tablename__ = "student_skills"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    student_id = Column(String(36), ForeignKey("students.student_id", ondelete="CASCADE"), nullable=False)
    skill_id = Column(String(36), ForeignKey("skills.skill_id", ondelete="CASCADE"), nullable=False)
    proficiency_level = Column(String(50), default="intermediate")
    evidence_source = Column(String(100), default="coursework")  # coursework, project, certification, assessment
    verified = Column(Boolean, default=False)
    verified_by = Column(String(36), ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True)

    # Relationships
    student = relationship("Student", back_populates="skills")
    skill = relationship("Skill", back_populates="student_skills")

class SkillMapping(Base):
    __tablename__ = "skill_mappings"

    mapping_id = Column(String(36), primary_key=True, default=generate_uuid)
    course_id = Column(String(36), ForeignKey("courses.course_id", ondelete="CASCADE"), nullable=False)
    job_skill_id = Column(String(36), ForeignKey("job_skills.id", ondelete="CASCADE"), nullable=False)
    confidence = Column(Float, default=1.0)
    mapping_type = Column(String(50), default="exact")  # exact, semantic, unmapped
    status = Column(String(50), default="approved")  # pending, approved, rejected
    reviewed_by = Column(String(36), ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True)

    # Relationships
    course = relationship("Course", back_populates="mappings")
    job_skill = relationship("JobSkill", back_populates="mappings")

class LearningResource(Base):
    __tablename__ = "learning_resources"

    resource_id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(200), nullable=False)
    provider = Column(String(100), nullable=False)  # Coursera, NPTEL, edX, FreeCodeCamp
    url = Column(String(500), nullable=False)
    skill_id = Column(String(36), ForeignKey("skills.skill_id", ondelete="CASCADE"), nullable=False)
    resource_type = Column(String(50), default="Course")  # Course, Certification, Tutorial, Book
    difficulty = Column(String(50), default="Intermediate")

    # Relationships
    skill = relationship("Skill", back_populates="resources")
    recommendations = relationship("Recommendation", back_populates="resource", cascade="all, delete-orphan")

class Recommendation(Base):
    __tablename__ = "recommendations"

    recommendation_id = Column(String(36), primary_key=True, default=generate_uuid)
    student_id = Column(String(36), ForeignKey("students.student_id", ondelete="CASCADE"), nullable=False)
    resource_id = Column(String(36), ForeignKey("learning_resources.resource_id", ondelete="CASCADE"), nullable=False)
    reason = Column(Text, nullable=False)
    rank = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    student = relationship("Student", back_populates="recommendations")
    resource = relationship("LearningResource", back_populates="recommendations")

class GapResult(Base):
    __tablename__ = "gap_results"

    result_id = Column(String(36), primary_key=True, default=generate_uuid)
    student_id = Column(String(36), ForeignKey("students.student_id", ondelete="CASCADE"), nullable=False)
    job_id = Column(String(36), ForeignKey("job_roles.job_id", ondelete="CASCADE"), nullable=False)
    unweighted_coverage = Column(Float, nullable=False)
    weighted_coverage = Column(Float, nullable=False)
    gap_score = Column(Float, nullable=False)
    details_json = Column(Text, nullable=True)  # Stores JSON list of demonstrated, partial, and missing skills
    evaluated_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    student = relationship("Student", back_populates="gap_results")
    job_role = relationship("JobRole", back_populates="gap_results")

class EvaluationRecord(Base):
    __tablename__ = "evaluation_records"

    eval_id = Column(String(36), primary_key=True, default=generate_uuid)
    dataset_version = Column(String(50), nullable=False)
    model_type = Column(String(100), nullable=False)  # NLP_Semantic_Pipeline vs Keyword_Baseline
    metric_name = Column(String(100), nullable=False)  # precision, recall, f1_score, mapping_precision, gap_coverage
    metric_value = Column(Float, nullable=False)
    sample_count = Column(Integer, default=0)
    evaluated_at = Column(DateTime, default=datetime.utcnow)
    details_json = Column(Text, nullable=True)

class AuditLog(Base):
    __tablename__ = "audit_logs"

    log_id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True)
    action = Column(String(100), nullable=False)
    entity_type = Column(String(100), nullable=False)
    entity_id = Column(String(100), nullable=True)
    details = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="audit_logs")
