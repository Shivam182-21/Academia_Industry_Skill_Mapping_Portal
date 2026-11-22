from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.db.models import User, Student, UserRole
from backend.app.core.security import verify_password, get_password_hash, create_access_token
from backend.app.api.deps import get_current_user
from backend.app.core.audit import log_audit_event

router = APIRouter(prefix="/auth", tags=["Authentication & Profile"])

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str = UserRole.STUDENT
    department: str = "Computer Science & Engineering"
    roll_number: Optional[str] = None
    registration_number: Optional[str] = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    name: str
    email: str
    role: str
    student_id: Optional[str] = None
    cohort_id: Optional[str] = None

@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate user with email and password, returning JWT access token."""
    user = db.query(User).filter(User.email == request.email.strip().lower()).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )
    
    if not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated."
        )

    # Fetch student ID if student role
    student_id = None
    cohort_id = None
    if user.student_profile:
        student_id = user.student_profile.student_id
        cohort_id = user.student_profile.cohort_id

    access_token = create_access_token(subject=user.user_id, role=user.role)
    
    # Audit log
    log_audit_event(db, user_id=user.user_id, action="USER_LOGIN", entity_type="USER", entity_id=user.user_id)

    return TokenResponse(
        access_token=access_token,
        user_id=user.user_id,
        name=user.name,
        email=user.email,
        role=user.role,
        student_id=student_id,
        cohort_id=cohort_id
    )

@router.post("/register", response_model=TokenResponse)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new user account."""
    existing = db.query(User).filter(User.email == request.email.lower()).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists."
        )
    
    user = User(
        name=request.name,
        email=request.email.lower(),
        password_hash=get_password_hash(request.password),
        role=request.role
    )
    db.add(user)
    db.flush()

    student_id = None
    cohort_id = None
    if request.role == UserRole.STUDENT:
        # Default student association
        student = Student(
            user_id=user.user_id,
            department=request.department,
            roll_number=request.roll_number,
            registration_number=request.registration_number
        )
        db.add(student)
        db.flush()
        student_id = student.student_id

    db.commit()

    log_audit_event(db, user_id=user.user_id, action="USER_REGISTER", entity_type="USER", entity_id=user.user_id)

    access_token = create_access_token(subject=user.user_id, role=user.role)
    return TokenResponse(
        access_token=access_token,
        user_id=user.user_id,
        name=user.name,
        email=user.email,
        role=user.role,
        student_id=student_id,
        cohort_id=cohort_id
    )

@router.get("/me")
def get_current_user_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve authenticated user profile and relevant identifiers."""
    student_info = None
    if current_user.student_profile:
        student_info = {
            "student_id": current_user.student_profile.student_id,
            "cohort_id": current_user.student_profile.cohort_id,
            "department": current_user.student_profile.department,
            "roll_number": current_user.student_profile.roll_number,
            "registration_number": current_user.student_profile.registration_number
        }
    
    return {
        "user_id": current_user.user_id,
        "name": current_user.name,
        "email": current_user.email,
        "role": current_user.role,
        "student": student_info
    }

@router.get("/demo-users")
def get_demo_users():
    """Provides evaluator convenience logins for all 5 roles."""
    return [
        {
            "role": "student",
            "name": "Shivam Chandel (SIH Team Lead)",
            "email": "shivam.student@portal.edu",
            "password": "student123",
            "note": "Student from CSE Cohort with verified project & coursework skills"
        },
        {
            "role": "student",
            "name": "Navneet Kumar (SIH Team Member)",
            "email": "navneet.student@portal.edu",
            "password": "student123",
            "note": "Student with machine learning and health informatics skills"
        },
        {
            "role": "faculty",
            "name": "Dr. Rajesh Sharma",
            "email": "faculty@portal.edu",
            "password": "faculty123",
            "note": "Faculty for reviewing curriculum skills and syllabus uploads"
        },
        {
            "role": "placement_officer",
            "name": "Prof. Sunita Verma",
            "email": "placement@portal.edu",
            "password": "placement123",
            "note": "Placement Officer analyzing cohort readiness & shortage heatmaps"
        },
        {
            "role": "employer",
            "name": "Vikramaditya Rao (TechCorp)",
            "email": "partner@techcorp.com",
            "password": "partner123",
            "note": "Industry Partner posting JDs and setting skill weights"
        },
        {
            "role": "admin",
            "name": "System Administrator",
            "email": "admin@portal.edu",
            "password": "admin123",
            "note": "System Admin managing users, audit logs, and benchmark evaluations"
        }
    ]
