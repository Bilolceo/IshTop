"""
=============================================================================
API VERSION 1
=============================================================================

All v1 API routes are registered here.
"""

from fastapi import APIRouter
from app.api.v1.routes import auth, users, resumes, jobs, applications, admin, payments, ai_powered, analytics

# Create main v1 router
api_router = APIRouter()

# Include all route modules
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"]
)

api_router.include_router(
    users.router,
    prefix="/users",
    tags=["Users"]
)

api_router.include_router(
    resumes.router,
    prefix="/resumes",
    tags=["Resumes"]
)

api_router.include_router(
    jobs.router,
    prefix="/jobs",
    tags=["Jobs"]
)

api_router.include_router(
    applications.router,
    prefix="/applications",
    tags=["Applications"]
)

# AI-Powered Features Router - Revolutionary career services
api_router.include_router(
    ai_powered.router,
    prefix="",
    tags=["AI-Powered"]
)

# Admin Router - Admin dashboard and management
api_router.include_router(
    admin.router,
    prefix="/admin",
    tags=["Admin"]
)

# Payment Router - Subscription and billing
api_router.include_router(
    payments.router,
    prefix="/payments",
    tags=["Payments"]
)

# Analytics Router - Enterprise analytics and business intelligence
api_router.include_router(
    analytics.router,
    prefix="",
    tags=["Analytics"]
)












