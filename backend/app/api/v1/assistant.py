"""
API routes for assistant interactions.
Handles multi-agent orchestration for green career guidance.
"""
from typing import Dict, Any
from fastapi import APIRouter, HTTPException
from datetime import datetime
import uuid
from loguru import logger

from app.models import (
    AssistantRequest, AssistantResponse, AssistantTaskType, LanguageCode,
    Persona, PersonaCreate
)
from app.agents import get_agent, RouterAgent, CareerAgent
from app.repositories.persona_repository import PersonaRepository
from app.telemetry.events import EventLogger
from app.core.config import settings

router = APIRouter()

# Initialize services (will be properly injected later)
persona_repo = PersonaRepository()
event_logger = EventLogger()


@router.post("/", response_model=AssistantResponse)
async def process_request(request: AssistantRequest):
    """
    Process an assistant request through multi-agent orchestration
    """
    try:
        logger.info(f"🤖 Processing assistant request: {request.task_type}")
        
        # Get or create persona
        persona = await _get_or_create_persona(request)
        
        # Start orchestration
        start_time = datetime.utcnow()
        
        # 1. Route the request
        router_agent = RouterAgent()
        routing_result = await router_agent.process(request, persona)
        
        # 2. Process with recommended agent
        recommended_task = routing_result["recommended_task"]
        suggested_agents = routing_result["suggested_agents"]
        
        # For now, use the first suggested agent
        primary_agent_name = suggested_agents[0] if suggested_agents else "career_agent"
        primary_agent = get_agent(primary_agent_name)
        
        # Update request task type based on routing
        request.task_type = AssistantTaskType(recommended_task)
        
        # Process with primary agent
        agent_result = await primary_agent.process(request, persona, context=routing_result)
        
        # 3. Build response
        end_time = datetime.utcnow()
        processing_time = int((end_time - start_time).total_seconds() * 1000)
        
        response = AssistantResponse(
            response=agent_result.get("career_guidance", "Guidance processed successfully"),
            recommendations=[],  # Will be populated by recommendation service
            next_steps=_generate_next_steps(persona, routing_result),
            persona_id=persona.id,
            agent_used=primary_agent_name,
            language=request.language,
            confidence_score=routing_result.get("confidence", 0.8),
            reasoning=routing_result.get("reasoning", "Multi-agent analysis completed")
        )
        
        # 4. Log interaction
        await event_logger.log_event("assistant_interaction", {
            "persona_id": persona.id,
            "task_type": request.task_type,
            "agent_used": primary_agent_name,
            "language": request.language,
            "processing_time_ms": processing_time,
            "confidence": response.confidence_score,
            "success": True
        })
        
        # 5. Update persona interaction count
        persona.interaction_count += 1
        persona.last_interaction = datetime.utcnow()
        await persona_repo.update_persona_metadata(persona.id, persona.interaction_count, persona.last_interaction)
        
        logger.info(f"✅ Assistant request processed in {processing_time}ms")
        return response
        
    except Exception as e:
        logger.error(f"❌ Assistant request failed: {e}")
        
        # Log error event
        await event_logger.log_event("assistant_error", {
            "error": str(e),
            "task_type": request.task_type if request else "unknown",
            "language": request.language if request else "unknown"
        })
        
        raise HTTPException(
            status_code=500, 
            detail="Failed to process assistant request"
        )


@router.post("/chat", response_model=AssistantResponse)
async def chat_interface(request: AssistantRequest):
    """
    Simplified chat interface for conversational interactions
    """
    try:
        logger.info("💬 Processing chat request")
        
        # For chat, we default to awareness/general guidance
        if not request.task_type:
            request.task_type = AssistantTaskType.AWARENESS
        
        return await process_request(request)
        
    except Exception as e:
        logger.error(f"❌ Chat request failed: {e}")
        raise HTTPException(status_code=500, detail="Chat processing failed")


@router.get("/health")
async def assistant_health():
    """Health check for assistant services"""
    try:
        # Test agent availability
        router_agent = RouterAgent()
        career_agent = CareerAgent()
        
        # Test persona repository
        persona_count = await persona_repo.count_personas()
        
        return {
            "status": "healthy",
            "agents": {
                "router_agent": "available",
                "career_agent": "available"
            },
            "persona_count": persona_count,
            "mock_mode": settings.MOCK_MODE,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Assistant health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


async def _get_or_create_persona(request: AssistantRequest) -> Persona:
    """Get existing persona or create new one from request data"""
    
    # If persona_id provided, try to get existing persona
    if request.persona_id:
        persona = await persona_repo.get_persona(request.persona_id)
        if persona:
            return persona
        else:
            logger.warning(f"⚠️ Persona {request.persona_id} not found, creating new one")
    
    # Create new persona from request data
    if request.persona_data:
        persona_id = str(uuid.uuid4())
        persona = Persona(
            id=persona_id,
            **request.persona_data.dict(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        created_persona = await persona_repo.create_persona(persona)
        logger.info(f"✅ Created new persona {persona_id}")
        return created_persona
    
    # Create default persona for anonymous requests
    else:
        persona_id = str(uuid.uuid4())
        default_persona = Persona(
            id=persona_id,
            name="Jovem Anônimo",
            age=20,
            location_state="SP",
            location_city="São Paulo",
            education_level="secondary",
            preferred_language=request.language,
            readiness_level="exploring",
            green_interests=[],
            time_availability=10,
            budget_constraint=0,
            career_goals=[],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        created_persona = await persona_repo.create_persona(default_persona)
        logger.info(f"✅ Created anonymous persona {persona_id}")
        return created_persona


def _generate_next_steps(persona: Persona, routing_result: Dict[str, Any]) -> list:
    """Generate contextual next steps based on persona and routing analysis"""
    
    next_steps = []
    task_type = routing_result.get("recommended_task", "AWARENESS")
    
    if task_type == "AWARENESS":
        next_steps = [
            "Explore setores verdes em crescimento no Brasil",
            "Identifique suas áreas de interesse específicas",
            "Pesquise oportunidades em sua região"
        ]
    elif task_type == "CAREER_EXPLORATION":
        next_steps = [
            "Analise vagas específicas em empresas verdes locais",
            "Conecte-se com profissionais da área no LinkedIn",
            "Participe de eventos e webinars do setor"
        ]
    elif task_type == "SKILL_ASSESSMENT":
        next_steps = [
            "Faça uma autoavaliação de habilidades técnicas",
            "Identifique lacunas de conhecimento prioritárias",
            "Busque feedback de profissionais experientes"
        ]
    elif task_type == "LEARNING_GUIDANCE":
        next_steps = [
            "Pesquise cursos gratuitos online sobre sustentabilidade",
            "Considere certificações reconhecidas pelo mercado",
            "Explore programas de capacitação do SENAI"
        ]
    elif task_type == "PATHWAY_PLANNING":
        next_steps = [
            "Defina metas de curto e longo prazo",
            "Crie um cronograma de desenvolvimento",
            "Identifique marcos de progresso mensuráveis"
        ]
    
    # Add persona-specific suggestions
    if persona.budget_constraint == 0:
        next_steps.append("Procure oportunidades gratuitas de desenvolvimento")
    
    if persona.tech_comfort_level < 3:
        next_steps.append("Desenvolva habilidades digitais básicas")
    
    return next_steps