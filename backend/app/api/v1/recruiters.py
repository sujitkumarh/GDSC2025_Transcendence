"""
Recruiter API endpoints for GDSC2025 Transcendence
Handles recruiter/company registration, authentication, and dashboard data
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
import pandas as pd
import json
import jwt
from datetime import datetime, timedelta
import os
from pathlib import Path

router = APIRouter(prefix="/recruiters", tags=["recruiters"])
security = HTTPBearer()

# JWT Configuration
SECRET_KEY = "your_secret_key_here"  # In production, use environment variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Data file path
DATA_DIR = Path(__file__).parent.parent.parent.parent / "data"
RECRUITERS_FILE = DATA_DIR / "RECRUITER.csv"

# Pydantic models
class RecruiterRegistration(BaseModel):
    email: EmailStr
    password: str
    company_name: str
    contact_person: str
    phone: Optional[str] = None
    company_size: Optional[str] = None
    industry: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None

class RecruiterLogin(BaseModel):
    email: EmailStr
    password: str

class JobPosting(BaseModel):
    title: str
    department: str
    location: str
    job_type: str  # Full-time, Part-time, Contract, Internship
    experience_level: str  # Entry, Mid, Senior
    skills_required: List[str]
    description: str
    responsibilities: List[str]
    requirements: List[str]
    salary_range: Optional[str] = None
    benefits: Optional[List[str]] = []

class Token(BaseModel):
    access_token: str
    token_type: str

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        return email
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

def load_recruiters_data():
    """Load recruiter data from CSV file"""
    try:
        if RECRUITERS_FILE.exists():
            return pd.read_csv(RECRUITERS_FILE)
        else:
            # Create empty DataFrame with required columns
            columns = ['id', 'email', 'password', 'company_name', 'contact_person', 'phone', 
                      'company_size', 'industry', 'website', 'description', 'created_at', 
                      'active_jobs', 'total_applications']
            return pd.DataFrame(columns=columns)
    except Exception as e:
        print(f"Error loading recruiters data: {e}")
        return pd.DataFrame()

def save_recruiters_data(df: pd.DataFrame):
    """Save recruiter data to CSV file"""
    try:
        df.to_csv(RECRUITERS_FILE, index=False)
    except Exception as e:
        print(f"Error saving recruiters data: {e}")

@router.post("/register", response_model=Token)
async def register_recruiter(recruiter: RecruiterRegistration):
    """Register a new recruiter/company"""
    df = load_recruiters_data()
    
    # Check if email already exists
    if not df.empty and recruiter.email in df['email'].values:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new recruiter record
    new_id = 1 if df.empty else df['id'].max() + 1
    new_recruiter = {
        'id': new_id,
        'email': recruiter.email,
        'password': recruiter.password,  # In production, hash the password
        'company_name': recruiter.company_name,
        'contact_person': recruiter.contact_person,
        'phone': recruiter.phone,
        'company_size': recruiter.company_size,
        'industry': recruiter.industry,
        'website': recruiter.website,
        'description': recruiter.description,
        'created_at': datetime.now().isoformat(),
        'active_jobs': 0,
        'total_applications': 0
    }
    
    # Add to DataFrame and save
    df = pd.concat([df, pd.DataFrame([new_recruiter])], ignore_index=True)
    save_recruiters_data(df)
    
    # Create access token
    access_token = create_access_token(data={"sub": recruiter.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
async def login_recruiter(recruiter: RecruiterLogin):
    """Authenticate recruiter and return token"""
    df = load_recruiters_data()
    
    if df.empty:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Find recruiter by email
    recruiter_row = df[df['email'] == recruiter.email]
    if recruiter_row.empty or recruiter_row.iloc[0]['password'] != recruiter.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Create access token
    access_token = create_access_token(data={"sub": recruiter.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/profile")
async def get_recruiter_profile(current_user: str = Depends(verify_token)):
    """Get recruiter profile information"""
    df = load_recruiters_data()
    
    if df.empty:
        raise HTTPException(status_code=404, detail="Recruiter not found")
    
    recruiter_row = df[df['email'] == current_user]
    if recruiter_row.empty:
        raise HTTPException(status_code=404, detail="Recruiter not found")
    
    recruiter = recruiter_row.iloc[0]
    
    return {
        "id": recruiter['id'],
        "email": recruiter['email'],
        "company_name": recruiter['company_name'],
        "contact_person": recruiter['contact_person'],
        "phone": recruiter['phone'],
        "company_size": recruiter['company_size'],
        "industry": recruiter['industry'],
        "website": recruiter['website'],
        "description": recruiter['description']
    }

@router.get("/dashboard/stats")
async def get_dashboard_stats(current_user: str = Depends(verify_token)):
    """Get dashboard statistics for recruiter"""
    df = load_recruiters_data()
    
    if df.empty:
        raise HTTPException(status_code=404, detail="Recruiter not found")
    
    recruiter_row = df[df['email'] == current_user]
    if recruiter_row.empty:
        raise HTTPException(status_code=404, detail="Recruiter not found")
    
    recruiter = recruiter_row.iloc[0]
    
    # Mock statistics - in real app, this would come from jobs/applications tables
    return {
        "active_jobs": recruiter.get('active_jobs', 3),
        "total_applications": recruiter.get('total_applications', 47),
        "interviews_scheduled": 8,
        "candidates_hired": 2,
        "recent_activities": [
            {"type": "application", "candidate": "João Silva", "position": "Frontend Developer", "date": "2025-10-15"},
            {"type": "interview", "candidate": "Maria Santos", "position": "Full Stack Developer", "date": "2025-10-16"},
            {"type": "job_posted", "position": "Backend Developer", "date": "2025-10-14"},
            {"type": "hire", "candidate": "Pedro Costa", "position": "UI/UX Designer", "date": "2025-10-13"}
        ]
    }

@router.get("/jobs")
async def get_recruiter_jobs(current_user: str = Depends(verify_token)):
    """Get all jobs posted by the recruiter"""
    # Mock job data - in real app, this would come from jobs table
    return [
        {
            "id": 1,
            "title": "Senior Frontend Developer",
            "department": "Engineering",
            "location": "São Paulo, SP",
            "job_type": "Full-time",
            "experience_level": "Senior",
            "status": "Active",
            "applications_count": 23,
            "posted_date": "2025-10-10",
            "views": 156
        },
        {
            "id": 2,
            "title": "Full Stack Developer",
            "department": "Engineering",
            "location": "Remote",
            "job_type": "Full-time",
            "experience_level": "Mid",
            "status": "Active",
            "applications_count": 31,
            "posted_date": "2025-10-08",
            "views": 203
        },
        {
            "id": 3,
            "title": "Product Manager",
            "department": "Product",
            "location": "Rio de Janeiro, RJ",
            "job_type": "Full-time",
            "experience_level": "Senior",
            "status": "Draft",
            "applications_count": 0,
            "posted_date": "2025-10-15",
            "views": 0
        }
    ]

@router.post("/jobs")
async def create_job_posting(job: JobPosting, current_user: str = Depends(verify_token)):
    """Create a new job posting"""
    # In real app, this would save to jobs table
    job_data = {
        "id": 4,  # This would be auto-generated
        "recruiter_email": current_user,
        "title": job.title,
        "department": job.department,
        "location": job.location,
        "job_type": job.job_type,
        "experience_level": job.experience_level,
        "skills_required": job.skills_required,
        "description": job.description,
        "responsibilities": job.responsibilities,
        "requirements": job.requirements,
        "salary_range": job.salary_range,
        "benefits": job.benefits,
        "status": "Active",
        "created_date": datetime.now().isoformat(),
        "applications_count": 0
    }
    
    return {"message": "Job posted successfully", "job_id": job_data["id"]}

@router.get("/candidates/search")
async def search_candidates(
    skills: Optional[str] = None,
    experience_min: Optional[int] = None,
    location: Optional[str] = None,
    current_user: str = Depends(verify_token)
):
    """Search for candidates based on criteria"""
    # Mock candidate search results - in real app, this would query candidates database
    return [
        {
            "id": 1,
            "name": "Ana Silva",
            "title": "Frontend Developer",
            "experience_years": 3,
            "location": "São Paulo, SP",
            "skills": ["React", "TypeScript", "CSS", "JavaScript"],
            "match_percentage": 92,
            "availability": "Available",
            "profile_summary": "Passionate frontend developer with expertise in React and modern web technologies."
        },
        {
            "id": 2,
            "name": "Carlos Santos",
            "title": "Full Stack Developer",
            "experience_years": 5,
            "location": "Rio de Janeiro, RJ",
            "skills": ["Python", "React", "Node.js", "PostgreSQL"],
            "match_percentage": 88,
            "availability": "Open to opportunities",
            "profile_summary": "Experienced full stack developer with a focus on scalable web applications."
        },
        {
            "id": 3,
            "name": "Lucia Oliveira",
            "title": "Software Engineer",
            "experience_years": 2,
            "location": "Belo Horizonte, MG",
            "skills": ["Java", "Spring", "React", "MySQL"],
            "match_percentage": 85,
            "availability": "Available",
            "profile_summary": "Junior software engineer eager to contribute to innovative projects."
        }
    ]

@router.get("/analytics")
async def get_recruitment_analytics(current_user: str = Depends(verify_token)):
    """Get recruitment analytics and insights"""
    return {
        "job_performance": [
            {"job_title": "Frontend Developer", "applications": 23, "views": 156, "conversion_rate": 14.7},
            {"job_title": "Full Stack Developer", "applications": 31, "views": 203, "conversion_rate": 15.3},
            {"job_title": "Product Manager", "applications": 0, "views": 0, "conversion_rate": 0}
        ],
        "application_trends": {
            "last_30_days": [
                {"date": "2025-10-01", "applications": 3},
                {"date": "2025-10-02", "applications": 5},
                {"date": "2025-10-03", "applications": 2},
                {"date": "2025-10-04", "applications": 7},
                {"date": "2025-10-05", "applications": 4},
                {"date": "2025-10-06", "applications": 6},
                {"date": "2025-10-07", "applications": 8}
            ]
        },
        "top_skills_demand": [
            {"skill": "React", "jobs_requiring": 2, "candidates_with": 45},
            {"skill": "Python", "jobs_requiring": 1, "candidates_with": 32},
            {"skill": "TypeScript", "jobs_requiring": 2, "candidates_with": 28},
            {"skill": "Node.js", "jobs_requiring": 1, "candidates_with": 23}
        ],
        "diversity_metrics": {
            "gender_distribution": {"male": 65, "female": 32, "other": 3},
            "experience_distribution": {"entry": 25, "mid": 45, "senior": 30}
        }
    }