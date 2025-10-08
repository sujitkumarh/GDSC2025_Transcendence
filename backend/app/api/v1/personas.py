"""
API routes for persona management.
Handles CRUD operations for youth personas.
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Depends
from datetime import datetime
import uuid
from loguru import logger

from app.models import (
    Persona, PersonaCreate, PersonaUpdate, SuccessResponse, ErrorResponse
)
from app.repositories.persona_repository import persona_repository
from app.telemetry.events import event_logger

router = APIRouter()


@router.get("/", response_model=List[Persona])
async def list_personas(
    limit: int = Query(default=50, le=100, description="Maximum number of personas to return"),
    offset: int = Query(default=0, ge=0, description="Number of personas to skip"),
    state: Optional[str] = Query(default=None, description="Filter by Brazilian state"),
    readiness_level: Optional[str] = Query(default=None, description="Filter by readiness level")
):
    """List all personas with optional filtering"""
    try:
        logger.info(f"📋 Listing personas with limit={limit}, offset={offset}")
        
        personas = await persona_repository.list_personas(
            limit=limit,
            offset=offset,
            filters={
                "location_state": state,
                "readiness_level": readiness_level
            }
        )
        
        await event_logger.log_event("personas_listed", {
            "count": len(personas),
            "limit": limit,
            "offset": offset,
            "filters": {"state": state, "readiness_level": readiness_level}
        })
        
        return personas
        
    except Exception as e:
        logger.error(f"❌ Failed to list personas: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve personas")


@router.get("/{persona_id}", response_model=Persona)
async def get_persona(persona_id: str):
    """Get a specific persona by ID"""
    try:
        logger.info(f"🔍 Getting persona {persona_id}")
        
        persona = await persona_repository.get_persona(persona_id)
        if not persona:
            raise HTTPException(status_code=404, detail="Persona not found")
        
        await event_logger.log_event("persona_retrieved", {
            "persona_id": persona_id,
            "persona_name": persona.name
        })
        
        return persona
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get persona {persona_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve persona")


@router.post("/", response_model=Persona)
async def create_persona(persona_data: PersonaCreate):
    """Create a new persona"""
    try:
        logger.info(f"➕ Creating new persona: {persona_data.name}")
        
        # Generate unique ID
        persona_id = str(uuid.uuid4())
        
        # Create persona object
        persona = Persona(
            id=persona_id,
            **persona_data.dict(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Save to repository
        created_persona = await persona_repository.create_persona(persona)
        
        await event_logger.log_event("persona_created", {
            "persona_id": persona_id,
            "persona_name": persona_data.name,
            "location": f"{persona_data.location_city}, {persona_data.location_state}",
            "readiness_level": persona_data.readiness_level,
            "green_interests": persona_data.green_interests
        })
        
        logger.info(f"✅ Created persona {persona_id}")
        return created_persona
        
    except Exception as e:
        logger.error(f"❌ Failed to create persona: {e}")
        raise HTTPException(status_code=500, detail="Failed to create persona")


@router.put("/{persona_id}", response_model=Persona)
async def update_persona(persona_id: str, persona_data: PersonaUpdate):
    """Update an existing persona"""
    try:
        logger.info(f"📝 Updating persona {persona_id}")
        
        # Check if persona exists
        existing_persona = await persona_repository.get_persona(persona_id)
        if not existing_persona:
            raise HTTPException(status_code=404, detail="Persona not found")
        
        # Update persona
        updated_persona = await persona_repository.update_persona(persona_id, persona_data)
        
        await event_logger.log_event("persona_updated", {
            "persona_id": persona_id,
            "updated_fields": [k for k, v in persona_data.dict().items() if v is not None]
        })
        
        logger.info(f"✅ Updated persona {persona_id}")
        return updated_persona
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to update persona {persona_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update persona")


@router.delete("/{persona_id}", response_model=SuccessResponse)
async def delete_persona(persona_id: str):
    """Delete a persona"""
    try:
        logger.info(f"🗑️ Deleting persona {persona_id}")
        
        # Check if persona exists
        existing_persona = await persona_repository.get_persona(persona_id)
        if not existing_persona:
            raise HTTPException(status_code=404, detail="Persona not found")
        
        # Delete persona
        await persona_repository.delete_persona(persona_id)
        
        await event_logger.log_event("persona_deleted", {
            "persona_id": persona_id,
            "persona_name": existing_persona.name
        })
        
        logger.info(f"✅ Deleted persona {persona_id}")
        return SuccessResponse(message=f"Persona {persona_id} deleted successfully")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to delete persona {persona_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete persona")


@router.get("/{persona_id}/interactions")
async def get_persona_interactions(persona_id: str):
    """Get interaction history for a persona"""
    try:
        logger.info(f"📊 Getting interactions for persona {persona_id}")
        
        # Check if persona exists
        persona = await persona_repository.get_persona(persona_id)
        if not persona:
            raise HTTPException(status_code=404, detail="Persona not found")
        
        # Get interactions from event logger
        interactions = await event_logger.get_persona_interactions(persona_id)
        
        return {
            "persona_id": persona_id,
            "interaction_count": len(interactions),
            "interactions": interactions
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get interactions for persona {persona_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve interactions")