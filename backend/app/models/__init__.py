"""
Pydantic models for Transcendence API.
Defines data structures for personas, jobs, training, and analytics.
"""
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field, validator
from enum import Enum


class LanguageCode(str, Enum):
    """Supported language codes"""
    EN = "en"
    PT_BR = "pt-BR"


class PersonaReadinessLevel(str, Enum):
    """Readiness levels for persona assessment"""
    EXPLORING = "exploring"        # Just starting to explore
    INTERESTED = "interested"      # Interested but needs guidance
    PREPARING = "preparing"        # Actively preparing/learning
    READY = "ready"               # Ready for opportunities
    EXPERIENCED = "experienced"    # Has some experience


class GreenJobCategory(str, Enum):
    """Green job categories available in Brazil"""
    SOLAR = "solar"
    WIND = "wind"
    WASTE_MANAGEMENT = "waste_management"
    SUSTAINABLE_AGRICULTURE = "sustainable_agriculture"
    ELECTRIC_VEHICLES = "electric_vehicles"
    FORESTRY = "forestry"
    ESG_CONSULTING = "esg_consulting"
    RENEWABLE_ENERGY = "renewable_energy"
    WATER_MANAGEMENT = "water_management"
    GREEN_CONSTRUCTION = "green_construction"


class EducationLevel(str, Enum):
    """Education levels for persona profiling"""
    PRIMARY = "primary"
    SECONDARY = "secondary"
    TECHNICAL = "technical"
    UNDERGRADUATE = "undergraduate"
    GRADUATE = "graduate"


class BrazilianState(str, Enum):
    """Brazilian states for location-based recommendations"""
    AC = "AC"  # Acre
    AL = "AL"  # Alagoas
    AP = "AP"  # Amapá
    AM = "AM"  # Amazonas
    BA = "BA"  # Bahia
    CE = "CE"  # Ceará
    DF = "DF"  # Distrito Federal
    ES = "ES"  # Espírito Santo
    GO = "GO"  # Goiás
    MA = "MA"  # Maranhão
    MT = "MT"  # Mato Grosso
    MS = "MS"  # Mato Grosso do Sul
    MG = "MG"  # Minas Gerais
    PA = "PA"  # Pará
    PB = "PB"  # Paraíba
    PR = "PR"  # Paraná
    PE = "PE"  # Pernambuco
    PI = "PI"  # Piauí
    RJ = "RJ"  # Rio de Janeiro
    RN = "RN"  # Rio Grande do Norte
    RS = "RS"  # Rio Grande do Sul
    RO = "RO"  # Rondônia
    RR = "RR"  # Roraima
    SC = "SC"  # Santa Catarina
    SP = "SP"  # São Paulo
    SE = "SE"  # Sergipe
    TO = "TO"  # Tocantins


# Persona Models
class PersonaBase(BaseModel):
    """Base persona attributes"""
    name: str = Field(..., description="Persona name or identifier")
    age: int = Field(..., ge=16, le=24, description="Age between 16-24")
    location_state: BrazilianState = Field(..., description="Brazilian state")
    location_city: str = Field(..., description="City name")
    education_level: EducationLevel = Field(..., description="Current education level")
    preferred_language: LanguageCode = Field(default=LanguageCode.PT_BR, description="Preferred language")
    
    # Digital access
    has_smartphone: bool = Field(default=True, description="Has access to smartphone")
    has_internet: bool = Field(default=True, description="Has regular internet access")
    tech_comfort_level: int = Field(default=3, ge=1, le=5, description="Tech comfort (1-5 scale)")
    
    # Green interests
    green_interests: List[GreenJobCategory] = Field(default=[], description="Areas of green job interest")
    readiness_level: PersonaReadinessLevel = Field(..., description="Current readiness for green careers")
    
    # Constraints and goals
    time_availability: int = Field(default=10, ge=1, le=40, description="Hours per week available")
    budget_constraint: int = Field(default=0, ge=0, description="Monthly budget in BRL")
    career_goals: List[str] = Field(default=[], description="Career aspiration keywords")
    
    # Additional attributes
    learning_style: str = Field(default="mixed", description="Preferred learning approach")
    motivation_factors: List[str] = Field(default=[], description="What motivates this persona")


class PersonaCreate(PersonaBase):
    """Persona creation model"""
    pass


class PersonaUpdate(BaseModel):
    """Persona update model with optional fields"""
    name: Optional[str] = None
    age: Optional[int] = Field(None, ge=16, le=24)
    location_state: Optional[BrazilianState] = None
    location_city: Optional[str] = None
    education_level: Optional[EducationLevel] = None
    preferred_language: Optional[LanguageCode] = None
    has_smartphone: Optional[bool] = None
    has_internet: Optional[bool] = None
    tech_comfort_level: Optional[int] = Field(None, ge=1, le=5)
    green_interests: Optional[List[GreenJobCategory]] = None
    readiness_level: Optional[PersonaReadinessLevel] = None
    time_availability: Optional[int] = Field(None, ge=1, le=40)
    budget_constraint: Optional[int] = Field(None, ge=0)
    career_goals: Optional[List[str]] = None
    learning_style: Optional[str] = None
    motivation_factors: Optional[List[str]] = None


class Persona(PersonaBase):
    """Full persona model with metadata"""
    id: str = Field(..., description="Unique persona identifier")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    interaction_count: int = Field(default=0, description="Number of assistant interactions")
    last_interaction: Optional[datetime] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# Job and Opportunity Models
class GreenJobBase(BaseModel):
    """Base green job opportunity"""
    title: str = Field(..., description="Job title")
    category: GreenJobCategory = Field(..., description="Green job category")
    description: str = Field(..., description="Job description")
    location_state: BrazilianState = Field(..., description="Job location state")
    location_city: str = Field(..., description="Job location city")
    
    # Requirements
    min_education: EducationLevel = Field(..., description="Minimum education required")
    required_skills: List[str] = Field(default=[], description="Required skills")
    preferred_skills: List[str] = Field(default=[], description="Preferred skills")
    experience_required: int = Field(default=0, ge=0, description="Years of experience required")
    
    # Job details
    employment_type: str = Field(default="full-time", description="Employment type")
    salary_min: Optional[int] = Field(None, ge=0, description="Minimum salary in BRL")
    salary_max: Optional[int] = Field(None, ge=0, description="Maximum salary in BRL")
    remote_possible: bool = Field(default=False, description="Remote work possible")
    
    # Metadata
    company: str = Field(..., description="Company name")
    contact_info: str = Field(..., description="Application contact")
    source_url: Optional[str] = Field(None, description="Original job posting URL")
    tags: List[str] = Field(default=[], description="Additional tags")


class GreenJob(GreenJobBase):
    """Full green job model with metadata"""
    id: str = Field(..., description="Unique job identifier")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    relevance_score: Optional[float] = Field(None, ge=0, le=1, description="Relevance score for persona")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# Learning and Training Models
class TrainingProgramBase(BaseModel):
    """Base training program"""
    title: str = Field(..., description="Training program title")
    description: str = Field(..., description="Program description")
    provider: str = Field(..., description="Training provider")
    category: GreenJobCategory = Field(..., description="Related green job category")
    
    # Program details
    duration_hours: int = Field(..., ge=1, description="Duration in hours")
    difficulty_level: int = Field(..., ge=1, le=5, description="Difficulty level (1-5)")
    cost_brl: int = Field(default=0, ge=0, description="Cost in BRL")
    is_free: bool = Field(default=False, description="Is the program free")
    
    # Requirements
    prerequisites: List[str] = Field(default=[], description="Prerequisites")
    min_education: EducationLevel = Field(..., description="Minimum education required")
    
    # Access
    online_available: bool = Field(default=True, description="Available online")
    location_state: Optional[BrazilianState] = Field(None, description="In-person location state")
    location_city: Optional[str] = Field(None, description="In-person location city")
    
    # Outcomes
    skills_gained: List[str] = Field(default=[], description="Skills gained from program")
    certification: Optional[str] = Field(None, description="Certification awarded")
    employment_rate: Optional[float] = Field(None, ge=0, le=1, description="Employment rate after completion")
    
    # Contact
    enrollment_url: Optional[str] = Field(None, description="Enrollment URL")
    contact_info: str = Field(..., description="Contact information")


class TrainingProgram(TrainingProgramBase):
    """Full training program model with metadata"""
    id: str = Field(..., description="Unique training program identifier")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    relevance_score: Optional[float] = Field(None, ge=0, le=1, description="Relevance score for persona")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# Assistant and Interaction Models
class AssistantTaskType(str, Enum):
    """Types of assistant tasks"""
    AWARENESS = "awareness"           # General green career awareness
    CAREER_EXPLORATION = "career_exploration"  # Specific job exploration
    SKILL_ASSESSMENT = "skill_assessment"      # Skills gap analysis
    LEARNING_GUIDANCE = "learning_guidance"    # Training recommendations
    PATHWAY_PLANNING = "pathway_planning"      # Step-by-step guidance


class AssistantRequest(BaseModel):
    """Request to the assistant system"""
    persona_id: Optional[str] = Field(None, description="Existing persona ID")
    persona_data: Optional[PersonaCreate] = Field(None, description="New persona data")
    task_type: AssistantTaskType = Field(..., description="Type of assistance requested")
    message: str = Field(..., description="User message or query")
    language: LanguageCode = Field(default=LanguageCode.EN, description="Response language")
    context: Dict[str, Any] = Field(default={}, description="Additional context")


class AssistantResponse(BaseModel):
    """Response from the assistant system"""
    response: str = Field(..., description="Assistant response message")
    recommendations: List[Dict[str, Any]] = Field(default=[], description="Structured recommendations")
    next_steps: List[str] = Field(default=[], description="Suggested next actions")
    persona_id: str = Field(..., description="Persona ID used for response")
    agent_used: str = Field(..., description="Primary agent that handled the request")
    language: LanguageCode = Field(..., description="Response language")
    confidence_score: float = Field(..., ge=0, le=1, description="Confidence in recommendations")
    reasoning: str = Field(..., description="Explanation of reasoning")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# Analytics Models
class InteractionEvent(BaseModel):
    """Individual interaction event for analytics"""
    id: str = Field(..., description="Unique event ID")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    persona_id: str = Field(..., description="Associated persona ID")
    event_type: str = Field(..., description="Type of interaction")
    task_type: AssistantTaskType = Field(..., description="Task type")
    agent_used: str = Field(..., description="Agent that handled interaction")
    language: LanguageCode = Field(..., description="Language used")
    success: bool = Field(..., description="Whether interaction was successful")
    duration_ms: int = Field(..., ge=0, description="Interaction duration in milliseconds")
    user_feedback: Optional[int] = Field(None, ge=1, le=5, description="User feedback score")
    metadata: Dict[str, Any] = Field(default={}, description="Additional event metadata")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class AnalyticsSummary(BaseModel):
    """Summary analytics for dashboard"""
    total_personas: int = Field(..., description="Total number of personas")
    total_interactions: int = Field(..., description="Total interactions")
    unique_active_personas: int = Field(..., description="Active personas in period")
    avg_interactions_per_persona: float = Field(..., description="Average interactions per persona")
    success_rate: float = Field(..., ge=0, le=1, description="Overall success rate")
    popular_categories: List[Dict[str, Union[str, int]]] = Field(default=[], description="Popular green job categories")
    language_distribution: Dict[str, int] = Field(default={}, description="Language usage distribution")
    readiness_distribution: Dict[str, int] = Field(default={}, description="Readiness level distribution")
    top_recommendations: List[Dict[str, Any]] = Field(default=[], description="Most recommended items")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# Error and Response Models
class ErrorResponse(BaseModel):
    """Standard error response"""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class SuccessResponse(BaseModel):
    """Standard success response"""
    success: bool = Field(default=True, description="Operation success status")
    message: str = Field(..., description="Success message")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }