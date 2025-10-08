"""
Learning content API routes.
Handles training programs and educational resources.
"""
from typing import List, Optional
from fastapi import APIRouter, Query, HTTPException
from loguru import logger

router = APIRouter()


@router.get("/programs")
async def list_training_programs(
    category: Optional[str] = Query(default=None, description="Filter by green job category"),
    free_only: bool = Query(default=False, description="Show only free programs"),
    location_state: Optional[str] = Query(default=None, description="Filter by Brazilian state"),
    limit: int = Query(default=20, le=100, description="Maximum number of programs to return")
):
    """List available training programs"""
    try:
        logger.info(f"📚 Listing training programs with filters: category={category}, free_only={free_only}")
        
        # Mock training programs data
        mock_programs = [
            {
                "id": "program_001",
                "title": "Instalação de Painéis Solares - Básico",
                "provider": "SENAI",
                "category": "solar",
                "duration_hours": 40,
                "cost_brl": 0,
                "is_free": True,
                "online_available": True,
                "location_state": "SP",
                "skills_gained": ["instalação", "manutenção", "segurança"],
                "certification": "Certificado SENAI"
            },
            {
                "id": "program_002", 
                "title": "Gestão de Resíduos Sólidos",
                "provider": "SEBRAE",
                "category": "waste_management",
                "duration_hours": 24,
                "cost_brl": 150,
                "is_free": False,
                "online_available": True,
                "location_state": "RJ",
                "skills_gained": ["gestão", "sustentabilidade", "logística"],
                "certification": "Certificado SEBRAE"
            }
        ]
        
        # Apply filters
        filtered_programs = mock_programs
        if category:
            filtered_programs = [p for p in filtered_programs if p["category"] == category]
        if free_only:
            filtered_programs = [p for p in filtered_programs if p["is_free"]]
        if location_state:
            filtered_programs = [p for p in filtered_programs if p["location_state"] == location_state]
        
        return {
            "programs": filtered_programs[:limit],
            "total": len(filtered_programs),
            "filters_applied": {
                "category": category,
                "free_only": free_only,
                "location_state": location_state
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to list training programs: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve training programs")


@router.get("/content")
async def get_awareness_content(
    topic: Optional[str] = Query(default=None, description="Filter by topic"),
    language: str = Query(default="pt-BR", description="Content language"),
    limit: int = Query(default=10, le=50, description="Maximum content items to return")
):
    """Get awareness and educational content"""
    try:
        logger.info(f"📖 Getting awareness content: topic={topic}, language={language}")
        
        # Mock content data
        mock_content = [
            {
                "id": "content_001",
                "title": "O que são Empregos Verdes?",
                "summary": "Introdução aos conceitos de emprego verde e economia sustentável no Brasil",
                "content_type": "article",
                "reading_time_minutes": 5,
                "topics": ["introdução", "conceitos"],
                "language": "pt-BR"
            },
            {
                "id": "content_002",
                "title": "Energia Solar no Brasil: Oportunidades",
                "summary": "Panorama do mercado de energia solar e oportunidades de carreira",
                "content_type": "video",
                "reading_time_minutes": 15,
                "topics": ["energia solar", "carreira"],
                "language": "pt-BR"
            }
        ]
        
        # Apply filters
        filtered_content = mock_content
        if topic:
            filtered_content = [c for c in filtered_content if topic in c["topics"]]
        if language:
            filtered_content = [c for c in filtered_content if c["language"] == language]
        
        return {
            "content": filtered_content[:limit],
            "total": len(filtered_content),
            "filters_applied": {
                "topic": topic,
                "language": language
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get awareness content: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve content")