#!/usr/bin/env python3
"""
=============================================================================
Seed Database with Test Data
=============================================================================

Bu script test ma'lumotlari bilan DBni to'ldiradi:
- 1 Admin user
- 1 Company user
- 2 Student users
- 3 Jobs
- 2 Resumes
- 3 Applications

Usage:
    python seed_data.py
"""

import asyncio
import sys
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add parent directory to path
sys.path.insert(0, '.')

from app.config import settings
from app.models import User, UserRole, Resume, Job, Application
from app.models.base import Base

# =============================================================================
# DATABASE SETUP
# =============================================================================

engine = create_engine(str(settings.DATABASE_URL), echo=False)
SessionLocal = sessionmaker(bind=engine)

# =============================================================================
# SEED DATA
# =============================================================================

def seed_users(db):
    """Create test users."""
    print("Creating users...")
    
    users = []
    
    # Admin user
    admin = User(
        id=uuid4(),
        email="admin@smartcareer.uz",
        full_name="System Admin",
        phone="+998901111111",
        role=UserRole.ADMIN,
        is_active_account=True,
        is_verified=True,
    )
    admin.set_password("Admin123!")
    users.append(admin)
    
    # Company user
    company = User(
        id=uuid4(),
        email="hr@epam.com",
        full_name="EPAM HR Manager",
        phone="+998902222222",
        role=UserRole.COMPANY,
        company_name="EPAM Systems",
        company_website="https://epam.com",
        is_active_account=True,
        is_verified=True,
    )
    company.set_password("Company123!")
    users.append(company)
    
    # Student 1
    student1 = User(
        id=uuid4(),
        email="john@example.com",
        full_name="John Doe",
        phone="+998903333333",
        role=UserRole.STUDENT,
        is_active_account=True,
        is_verified=True,
    )
    student1.set_password("Student123!")
    users.append(student1)
    
    # Student 2
    student2 = User(
        id=uuid4(),
        email="jane@example.com",
        full_name="Jane Smith",
        phone="+998904444444",
        role=UserRole.STUDENT,
        is_active_account=True,
        is_verified=True,
    )
    student2.set_password("Student123!")
    users.append(student2)
    
    db.add_all(users)
    db.commit()
    
    print(f"✅ Created {len(users)} users")
    return users


def seed_resumes(db, students):
    """Create test resumes."""
    print("Creating resumes...")
    
    resumes = []
    
    # Resume 1
    resume1_content = {
        "personal_info": {
            "full_name": students[0].full_name,
            "email": students[0].email,
            "phone": students[0].phone,
            "location": "Tashkent, Uzbekistan",
            "linkedin": "https://linkedin.com/in/johndoe",
            "github": "https://github.com/johndoe",
        },
        "summary": "Experienced Python developer with 5+ years in backend development, API design, and cloud technologies.",
        "experience": [
            {
                "company": "TechCorp",
                "position": "Senior Backend Developer",
                "location": "Tashkent",
                "start_date": "2020-01-01",
                "end_date": None,
                "is_current": True,
                "description": "Leading backend team, designing scalable APIs, mentoring junior developers",
            },
            {
                "company": "StartupHub",
                "position": "Python Developer",
                "location": "Remote",
                "start_date": "2018-06-01",
                "end_date": "2019-12-31",
                "is_current": False,
                "description": "Developed microservices, worked with Django and FastAPI",
            },
        ],
        "education": [
            {
                "institution": "TUIT",
                "degree": "Bachelor",
                "field": "Computer Science",
                "location": "Tashkent",
                "start_date": "2014-09-01",
                "end_date": "2018-06-01",
                "gpa": "4.5",
            }
        ],
        "skills": ["Python", "FastAPI", "Django", "PostgreSQL", "Redis", "Docker", "AWS", "Git"],
        "languages": [
            {"language": "Uzbek", "level": "Native"},
            {"language": "English", "level": "Professional"},
            {"language": "Russian", "level": "Fluent"},
        ],
    }

    resume1 = Resume(
        status="published",
        id=uuid4(),
        user_id=students[0].id,
        title="Senior Python Developer",
        content=resume1_content,
        ats_score=92,
        view_count=45,
    )
    resumes.append(resume1)
    
    # Resume 2
    resume2_content = {
        "personal_info": {
            "full_name": students[1].full_name,
            "email": students[1].email,
            "phone": students[1].phone,
            "location": "Tashkent, Uzbekistan",
        },
        "summary": "Full-stack developer passionate about creating user-friendly web applications.",
        "experience": [
            {
                "company": "WebStudio",
                "position": "Full Stack Developer",
                "location": "Tashkent",
                "start_date": "2021-03-01",
                "end_date": None,
                "is_current": True,
                "description": "Building modern web apps with React and Node.js",
            }
        ],
        "education": [
            {
                "institution": "TUIT",
                "degree": "Bachelor",
                "field": "Software Engineering",
                "location": "Tashkent",
                "start_date": "2017-09-01",
                "end_date": "2021-06-01",
                "gpa": "4.2",
            }
        ],
        "skills": ["JavaScript", "TypeScript", "React", "Node.js", "Next.js", "MongoDB", "Docker"],
        "languages": [
            {"language": "Uzbek", "level": "Native"},
            {"language": "English", "level": "Intermediate"},
        ],
    }

    resume2 = Resume(
        status="published",
        id=uuid4(),
        user_id=students[1].id,
        title="Full Stack Developer",
        content=resume2_content,
        ats_score=85,
        view_count=32,
    )
    resumes.append(resume2)
    
    db.add_all(resumes)
    db.commit()
    
    print(f"✅ Created {len(resumes)} resumes")
    return resumes


def seed_jobs(db, company):
    """Create test jobs."""
    print("Creating jobs...")
    
    jobs = []
    
    # Job 1
    job1 = Job(
        status="active",
        id=uuid4(),
        company_id=company.id,
        title="Senior Backend Developer",
        description="We are looking for an experienced backend developer to join our team.",
        requirements=[
            "5+ years of Python experience",
            "Strong knowledge of FastAPI/Django",
            "Experience with PostgreSQL",
            "Understanding of microservices architecture",
        ],
        responsibilities=[
            "Design and implement RESTful APIs",
            "Write clean, maintainable code",
            "Mentor junior developers",
            "Participate in code reviews",
        ],
        salary_min=3000,
        salary_max=5000,
        salary_currency="USD",
        location="Tashkent, Uzbekistan",
        is_remote_allowed=True,
        job_type="full_time",
        experience_level="senior",
        # skills are already in requirements array above
        benefits=["Health insurance", "Remote work", "Professional development", "Flexible schedule"],
        views_count=156,
        applications_count=12,
        expires_at=datetime.now(timezone.utc) + timedelta(days=30),
    )
    jobs.append(job1)
    
    # Job 2
    job2 = Job(
        status="active",
        id=uuid4(),
        company_id=company.id,
        title="Full Stack Developer",
        description="Join our team to build modern web applications.",
        requirements=[
            "3+ years of full-stack development",
            "React/Next.js experience",
            "Node.js backend experience",
            "Understanding of REST APIs",
        ],
        responsibilities=[
            "Develop frontend and backend features",
            "Collaborate with design team",
            "Ensure code quality",
            "Deploy applications",
        ],
        salary_min=2000,
        salary_max=3500,
        salary_currency="USD",
        location="Tashkent, Uzbekistan",
        is_remote_allowed=False,
        job_type="full_time",
        experience_level="mid",
        benefits=["Health insurance", "Team lunches", "Learning budget"],
        views_count=203,
        applications_count=18,
        expires_at=datetime.now(timezone.utc) + timedelta(days=25),
    )
    jobs.append(job2)
    
    # Job 3
    job3 = Job(
        status="active",
        id=uuid4(),
        company_id=company.id,
        title="DevOps Engineer",
        description="Help us build and maintain robust infrastructure.",
        requirements=[
            "Experience with Docker and Kubernetes",
            "CI/CD pipeline setup",
            "AWS or Azure knowledge",
            "Scripting skills (Python/Bash)",
        ],
        responsibilities=[
            "Maintain infrastructure",
            "Set up monitoring and alerting",
            "Automate deployment processes",
            "Ensure system reliability",
        ],
        salary_min=2500,
        salary_max=4000,
        salary_currency="USD",
        location="Remote",
        is_remote_allowed=True,
        job_type="full_time",
        experience_level="mid",
        benefits=["Remote work", "Flexible hours", "Equipment provided"],
        views_count=89,
        applications_count=7,
        expires_at=datetime.now(timezone.utc) + timedelta(days=45),
    )
    jobs.append(job3)
    
    db.add_all(jobs)
    db.commit()
    
    print(f"✅ Created {len(jobs)} jobs")
    return jobs


def seed_applications(db, jobs, students, resumes):
    """Create test applications."""
    print("Creating applications...")
    
    applications = []
    
    # Application 1: Student 1 -> Job 1
    app1 = Application(
        id=uuid4(),
        job_id=jobs[0].id,
        user_id=students[0].id,
        resume_id=resumes[0].id,
        status="interview",
        cover_letter="I am very interested in this position and believe my experience aligns well with your requirements.",
        match_score=92,
        interview_at=datetime.now(timezone.utc) + timedelta(days=3),
    )
    applications.append(app1)
    
    # Application 2: Student 1 -> Job 2
    app2 = Application(
        id=uuid4(),
        job_id=jobs[1].id,
        user_id=students[0].id,
        resume_id=resumes[0].id,
        status="pending",
        cover_letter="I would love to contribute to your team as a full-stack developer.",
        match_score=75,
    )
    applications.append(app2)
    
    # Application 3: Student 2 -> Job 2
    app3 = Application(
        id=uuid4(),
        job_id=jobs[1].id,
        user_id=students[1].id,
        resume_id=resumes[1].id,
        status="reviewing",
        cover_letter="My skills in React and Node.js make me a great fit for this role.",
        match_score=88,
    )
    applications.append(app3)
    
    db.add_all(applications)
    db.commit()
    
    print(f"✅ Created {len(applications)} applications")
    return applications


def main():
    """Run all seed functions."""
    print("\n" + "="*70)
    print("🌱 SEEDING DATABASE")
    print("="*70 + "\n")
    
    # Create tables if they don't exist
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created\n")
    
    # Create session
    db = SessionLocal()
    
    try:
        # Check if data already exists
        existing_users = db.query(User).count()
        if existing_users > 0:
            response = input(f"⚠️  Database already has {existing_users} users. Continue? (y/N): ")
            if response.lower() != 'y':
                print("Aborted.")
                return
            
            # Clear existing data
            print("\nClearing existing data...")
            db.query(Application).delete()
            db.query(Job).delete()
            db.query(Resume).delete()
            db.query(User).delete()
            db.commit()
            print("✅ Data cleared\n")
        
        # Seed data
        users = seed_users(db)
        admin = users[0]
        company = users[1]
        students = users[2:]
        
        resumes = seed_resumes(db, students)
        jobs = seed_jobs(db, company)
        applications = seed_applications(db, jobs, students, resumes)
        
        print("\n" + "="*70)
        print("✅ DATABASE SEEDED SUCCESSFULLY!")
        print("="*70)
        print("\n📝 Test Accounts:")
        print(f"   Admin:    admin@smartcareer.uz / Admin123!")
        print(f"   Company:  hr@epam.com / Company123!")
        print(f"   Student1: john@example.com / Student123!")
        print(f"   Student2: jane@example.com / Student123!")
        print("\n🚀 Start the server: uvicorn app.main:app --reload")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()









