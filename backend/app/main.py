from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from backend.app.core.config import settings
from backend.app.db.database import engine, Base
from backend.app.seed import seed_database
from backend.app.api.routers import (
    auth, curriculum, jobs, mapping, gap_analysis,
    recommendations, analytics, evaluation, admin
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure tables are created and initial seed data exists
    Base.metadata.create_all(bind=engine)
    try:
        seed_database()
    except Exception as e:
        print(f"Startup seed notice: {e}")
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="Smart India Hackathon 2026 (SIH26044) · Group G29: Academia–Industry Skill Mapping and Placement Portal",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers under /api/v1
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(curriculum.router, prefix=settings.API_V1_STR)
app.include_router(jobs.router, prefix=settings.API_V1_STR)
app.include_router(mapping.router, prefix=settings.API_V1_STR)
app.include_router(gap_analysis.router, prefix=settings.API_V1_STR)
app.include_router(recommendations.router, prefix=settings.API_V1_STR)
app.include_router(analytics.router, prefix=settings.API_V1_STR)
app.include_router(evaluation.router, prefix=settings.API_V1_STR)
app.include_router(admin.router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {
        "portal": settings.PROJECT_NAME,
        "event": "Smart India Hackathon 2026",
        "group": "G29",
        "status": "online",
        "docs_url": "/docs",
        "api_version": settings.PROJECT_VERSION,
        "team_members": [
            {"name": "Shivam Chandel", "roll": "RK3P25ORA20", "reg": "12522547"},
            {"name": "Navneet Kumar", "roll": "RK3P25ORB37", "reg": "12518540"}
        ]
    }
