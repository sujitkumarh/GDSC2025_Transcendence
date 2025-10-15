"""
Candidate API endpoints for GDSC2025 Transcendence
Handles candidate registration, authentication, and dashboard data
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

router = APIRouter(prefix="/candidates", tags=["candidates"])
security = HTTPBearer()

# JWT Configuration
SECRET_KEY = "your_secret_key_here"  # In production, use environment variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Data file path
DATA_DIR = Path(__file__).parent.parent.parent.parent / "data"
CANDIDATES_FILE = DATA_DIR / "JOB_SEEKER.csv"

# Pydantic models
class CandidateRegistration(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    phone: Optional[str] = None
    skills: Optional[List[str]] = []
    experience_years: Optional[int] = 0
    preferred_location: Optional[str] = None

class CandidateLogin(BaseModel):
    email: EmailStr
    password: str

class CandidateProfile(BaseModel):
    first_name: str
    last_name: str
    phone: Optional[str] = None
    skills: List[str] = []
    experience_years: int = 0
    preferred_location: Optional[str] = None
    resume_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None

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

def load_candidates_data():
    """Load candidate data from CSV file"""
    try:
        if CANDIDATES_FILE.exists():
            return pd.read_csv(CANDIDATES_FILE)
        else:
            # Create empty DataFrame with required columns
            columns = ['id', 'email', 'password', 'first_name', 'last_name', 'phone', 
                      'skills', 'experience_years', 'preferred_location', 'resume_url', 
                      'linkedin_url', 'github_url', 'created_at', 'applications_count']
            return pd.DataFrame(columns=columns)
    except Exception as e:
        print(f"Error loading candidates data: {e}")
        return pd.DataFrame()

def save_candidates_data(df: pd.DataFrame):
    """Save candidate data to CSV file"""
    try:
        df.to_csv(CANDIDATES_FILE, index=False)
    except Exception as e:
        print(f"Error saving candidates data: {e}")

@router.post("/register", response_model=Token)
async def register_candidate(candidate: CandidateRegistration):
    """Register a new candidate"""
    df = load_candidates_data()
    
    # Check if email already exists
    if not df.empty and candidate.email in df['email'].values:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new candidate record
    new_id = 1 if df.empty else df['id'].max() + 1
    new_candidate = {
        'id': new_id,
        'email': candidate.email,
        'password': candidate.password,  # In production, hash the password
        'first_name': candidate.first_name,
        'last_name': candidate.last_name,
        'phone': candidate.phone,
        'skills': json.dumps(candidate.skills),
        'experience_years': candidate.experience_years,
        'preferred_location': candidate.preferred_location,
        'resume_url': '',
        'linkedin_url': '',
        'github_url': '',
        'created_at': datetime.now().isoformat(),
        'applications_count': 0
    }
    
    # Add to DataFrame and save
    df = pd.concat([df, pd.DataFrame([new_candidate])], ignore_index=True)
    save_candidates_data(df)
    
    # Create access token
    access_token = create_access_token(data={"sub": candidate.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
async def login_candidate(candidate: CandidateLogin):
    """Authenticate candidate and return token"""
    df = load_candidates_data()
    
    if df.empty:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Find candidate by email
    candidate_row = df[df['email'] == candidate.email]
    if candidate_row.empty or candidate_row.iloc[0]['password'] != candidate.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Create access token
    access_token = create_access_token(data={"sub": candidate.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/profile")
async def get_candidate_profile(current_user: str = Depends(verify_token)):
    """Get candidate profile information"""
    df = load_candidates_data()
    
    if df.empty:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    candidate_row = df[df['email'] == current_user]
    if candidate_row.empty:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    candidate = candidate_row.iloc[0]
    skills = json.loads(candidate['skills']) if candidate['skills'] else []
    
    return {
        "id": candidate['id'],
        "email": candidate['email'],
        "first_name": candidate['first_name'],
        "last_name": candidate['last_name'],
        "phone": candidate['phone'],
        "skills": skills,
        "experience_years": candidate['experience_years'],
        "preferred_location": candidate['preferred_location'],
        "resume_url": candidate['resume_url'],
        "linkedin_url": candidate['linkedin_url'],
        "github_url": candidate['github_url']
    }

@router.put("/profile")
async def update_candidate_profile(profile: CandidateProfile, current_user: str = Depends(verify_token)):
    """Update candidate profile information"""
    df = load_candidates_data()
    
    if df.empty:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    # Find candidate by email
    candidate_idx = df[df['email'] == current_user].index
    if candidate_idx.empty:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    # Update candidate data
    idx = candidate_idx[0]
    df.loc[idx, 'first_name'] = profile.first_name
    df.loc[idx, 'last_name'] = profile.last_name
    df.loc[idx, 'phone'] = profile.phone
    df.loc[idx, 'skills'] = json.dumps(profile.skills)
    df.loc[idx, 'experience_years'] = profile.experience_years
    df.loc[idx, 'preferred_location'] = profile.preferred_location
    df.loc[idx, 'resume_url'] = profile.resume_url or ''
    df.loc[idx, 'linkedin_url'] = profile.linkedin_url or ''
    df.loc[idx, 'github_url'] = profile.github_url or ''
    
    save_candidates_data(df)
    
    return {"message": "Profile updated successfully"}

@router.get("/dashboard/stats")
async def get_dashboard_stats(current_user: str = Depends(verify_token)):
    """Get dashboard statistics for candidate"""
    df = load_candidates_data()
    
    if df.empty:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    candidate_row = df[df['email'] == current_user]
    if candidate_row.empty:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    candidate = candidate_row.iloc[0]
    
    # Mock statistics - in real app, this would come from applications/interviews tables
    return {
        "applications_sent": candidate.get('applications_count', 0),
        "interviews_scheduled": 2,
        "profile_views": 15,
        "skill_match_percentage": 78,
        "recent_activities": [
            {"type": "application", "company": "Tech Corp", "position": "Frontend Developer", "date": "2025-10-14"},
            {"type": "interview", "company": "Green Tech", "position": "Full Stack Developer", "date": "2025-10-16"},
            {"type": "profile_view", "company": "EcoSolutions", "date": "2025-10-15"}
        ]
    }

@router.get("/jobs/recommendations")
async def get_job_recommendations(current_user: str = Depends(verify_token)):
    """Get personalized job recommendations"""
    # Mock job recommendations - in real app, this would use AI/ML algorithms
    return [
        {
            "id": 1,
            "title": "Frontend Developer",
            "company": "GreenTech Solutions",
            "location": "São Paulo, SP",
            "type": "Full-time",
            "match_percentage": 95,
            "skills_required": ["React", "TypeScript", "Tailwind CSS"],
            "description": "Join our mission to create sustainable technology solutions.",
            "posted_date": "2025-10-14"
        },
        {
            "id": 2,
            "title": "Full Stack Developer",
            "company": "EcoInnovate",
            "location": "Rio de Janeiro, RJ",
            "type": "Remote",
            "match_percentage": 87,
            "skills_required": ["Python", "FastAPI", "React"],
            "description": "Build the future of green technology with our innovative team.",
            "posted_date": "2025-10-13"
        },
        {
            "id": 3,
            "title": "Software Engineer",
            "company": "Sustainable Tech",
            "location": "Belo Horizonte, MG",
            "type": "Hybrid",
            "match_percentage": 82,
            "skills_required": ["JavaScript", "Node.js", "MongoDB"],
            "description": "Help us create technology that makes a positive environmental impact.",
            "posted_date": "2025-10-12"
        }
    ]