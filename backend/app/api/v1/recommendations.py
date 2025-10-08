"""
Recommendations API routes.
Handles job and training recommendations for personas.
"""
from typing import List, Optional
from fastapi import APIRouter, Query, HTTPException
from loguru import logger

router = APIRouter()


@router.get("/jobs/{persona_id}")
async def get_job_recommendations(
    persona_id: str,
    limit: int = Query(default=5, le=20, description="Maximum number of recommendations")
):
    """Get job recommendations for a persona"""
    try:
        logger.info(f"💼 Getting job recommendations for persona {persona_id}")
        
        # Mock job recommendations
        mock_jobs = [
            {
                "id": "job_001",
                "title": "Técnico em Energia Solar Júnior",
                "company": "SolarTech Brasil",
                "category": "solar",
                "location": "São Paulo, SP",
                "salary_range": "R$ 2.500 - R$ 3.500",
                "experience_required": 0,
                "remote_possible": False,
                "relevance_score": 0.95,
                "match_reasons": [
                    "Interesse em energia solar",
                    "Localização compatível",
                    "Nível de experiência adequado"
                ]
            },
            {
                "id": "job_002",
                "title": "Assistente de Gestão Ambiental",
                "company": "EcoConsulting",
                "category": "esg_consulting",
                "location": "Rio de Janeiro, RJ",
                "salary_range": "R$ 2.200 - R$ 3.000",
                "experience_required": 0,
                "remote_possible": True,
                "relevance_score": 0.87,
                "match_reasons": [
                    "Interesse em sustentabilidade",
                    "Trabalho remoto disponível",
                    "Posição de entrada"
                ]
            }
        ]
        
        return {
            "persona_id": persona_id,
            "recommendations": mock_jobs[:limit],
            "total_available": len(mock_jobs),
            "generated_at": "2025-01-01T10:00:00Z"
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get job recommendations: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate job recommendations")


@router.get("/training/{persona_id}")
async def get_training_recommendations(
    persona_id: str,
    limit: int = Query(default=5, le=20, description="Maximum number of recommendations")
):
    """Get training recommendations for a persona"""
    try:
        logger.info(f"📚 Getting training recommendations for persona {persona_id}")
        
        # Mock training recommendations
        mock_training = [
            {
                "id": "training_001",
                "title": "Curso Básico de Energia Solar",
                "provider": "SENAI",
                "duration_hours": 40,
                "cost_brl": 0,
                "is_free": True,
                "online_available": True,
                "relevance_score": 0.92,
                "match_reasons": [
                    "Alinhado com interesse em energia solar",
                    "Gratuito",
                    "Disponível online"
                ]
            },
            {
                "id": "training_002",
                "title": "Fundamentos de Sustentabilidade",
                "provider": "Coursera",
                "duration_hours": 20,
                "cost_brl": 79,
                "is_free": False,
                "online_available": True,
                "relevance_score": 0.85,
                "match_reasons": [
                    "Base sólida em conceitos verdes",
                    "Certificação reconhecida",
                    "Flexibilidade de horário"
                ]
            }
        ]
        
        return {
            "persona_id": persona_id,
            "recommendations": mock_training[:limit],
            "total_available": len(mock_training),
            "generated_at": "2025-01-01T10:00:00Z"
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get training recommendations: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate training recommendations")


@router.post("/feedback")
async def submit_recommendation_feedback(
    recommendation_id: str,
    persona_id: str,
    feedback_type: str,  # "helpful", "not_helpful", "applied", "saved"
    rating: Optional[int] = Query(default=None, ge=1, le=5, description="Rating from 1-5")
):
    """Submit feedback on a recommendation"""
    try:
        logger.info(f"👍 Recording feedback for recommendation {recommendation_id}")
        
        # In a real system, this would save to database
        feedback_data = {
            "recommendation_id": recommendation_id,
            "persona_id": persona_id,
            "feedback_type": feedback_type,
            "rating": rating,
            "timestamp": "2025-01-01T10:00:00Z"
        }
        
        return {
            "success": True,
            "message": "Feedback recorded successfully",
            "feedback": feedback_data
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to record feedback: {e}")
        raise HTTPException(status_code=500, detail="Failed to record feedback")