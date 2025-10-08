"""
Persona repository for data persistence.
JSON-based storage with easy migration to database.
"""
import json
import os
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
from loguru import logger

from app.models import Persona, PersonaCreate, PersonaUpdate
from app.core.config import settings


class PersonaRepository:
    """JSON-based persona repository with future database migration support"""
    
    def __init__(self):
        self.data_dir = settings.DATA_DIR
        self.personas_file = os.path.join(self.data_dir, "personas.json")
        self._ensure_data_dir()
        self._personas_cache = {}
        self._load_personas()
    
    def _ensure_data_dir(self):
        """Ensure data directory exists"""
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Create empty personas file if it doesn't exist
        if not os.path.exists(self.personas_file):
            with open(self.personas_file, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
    
    def _load_personas(self):
        """Load personas from JSON file into cache"""
        try:
            with open(self.personas_file, 'r', encoding='utf-8') as f:
                personas_data = json.load(f)
                
            self._personas_cache = {}
            for persona_id, persona_dict in personas_data.items():
                # Convert datetime strings back to datetime objects
                if 'created_at' in persona_dict:
                    persona_dict['created_at'] = datetime.fromisoformat(persona_dict['created_at'])
                if 'updated_at' in persona_dict:
                    persona_dict['updated_at'] = datetime.fromisoformat(persona_dict['updated_at'])
                if 'last_interaction' in persona_dict and persona_dict['last_interaction']:
                    persona_dict['last_interaction'] = datetime.fromisoformat(persona_dict['last_interaction'])
                
                self._personas_cache[persona_id] = Persona(**persona_dict)
                
            logger.info(f"📦 Loaded {len(self._personas_cache)} personas from storage")
            
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.warning(f"⚠️ Could not load personas: {e}, starting with empty cache")
            self._personas_cache = {}
    
    def _save_personas(self):
        """Save personas cache to JSON file"""
        try:
            # Convert personas to serializable dict
            personas_dict = {}
            for persona_id, persona in self._personas_cache.items():
                persona_data = persona.dict()
                # Convert datetime objects to ISO strings
                if persona_data.get('created_at'):
                    persona_data['created_at'] = persona_data['created_at'].isoformat()
                if persona_data.get('updated_at'):
                    persona_data['updated_at'] = persona_data['updated_at'].isoformat()
                if persona_data.get('last_interaction'):
                    persona_data['last_interaction'] = persona_data['last_interaction'].isoformat()
                
                personas_dict[persona_id] = persona_data
            
            # Write to file with backup
            backup_file = f"{self.personas_file}.backup"
            if os.path.exists(self.personas_file):
                os.rename(self.personas_file, backup_file)
            
            with open(self.personas_file, 'w', encoding='utf-8') as f:
                json.dump(personas_dict, f, ensure_ascii=False, indent=2)
            
            # Remove backup on successful write
            if os.path.exists(backup_file):
                os.remove(backup_file)
                
            logger.debug(f"💾 Saved {len(personas_dict)} personas to storage")
            
        except Exception as e:
            logger.error(f"❌ Failed to save personas: {e}")
            # Restore backup if exists
            backup_file = f"{self.personas_file}.backup"
            if os.path.exists(backup_file):
                os.rename(backup_file, self.personas_file)
            raise
    
    async def get_persona(self, persona_id: str) -> Optional[Persona]:
        """Get persona by ID"""
        return self._personas_cache.get(persona_id)
    
    async def list_personas(
        self, 
        limit: int = 50, 
        offset: int = 0, 
        filters: Dict[str, Any] = None
    ) -> List[Persona]:
        """List personas with optional filtering and pagination"""
        personas = list(self._personas_cache.values())
        
        # Apply filters
        if filters:
            filtered_personas = []
            for persona in personas:
                match = True
                
                if filters.get('location_state') and persona.location_state != filters['location_state']:
                    match = False
                if filters.get('readiness_level') and persona.readiness_level != filters['readiness_level']:
                    match = False
                if filters.get('age_min') and persona.age < filters['age_min']:
                    match = False
                if filters.get('age_max') and persona.age > filters['age_max']:
                    match = False
                
                if match:
                    filtered_personas.append(persona)
            
            personas = filtered_personas
        
        # Sort by creation date (newest first)
        personas.sort(key=lambda p: p.created_at, reverse=True)
        
        # Apply pagination
        return personas[offset:offset + limit]
    
    async def create_persona(self, persona: Persona) -> Persona:
        """Create a new persona"""
        self._personas_cache[persona.id] = persona
        self._save_personas()
        logger.info(f"✅ Created persona {persona.id}")
        return persona
    
    async def update_persona(self, persona_id: str, persona_data: PersonaUpdate) -> Optional[Persona]:
        """Update an existing persona"""
        if persona_id not in self._personas_cache:
            return None
        
        persona = self._personas_cache[persona_id]
        
        # Update only provided fields
        update_dict = persona_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            if value is not None:
                setattr(persona, field, value)
        
        # Update timestamp
        persona.updated_at = datetime.utcnow()
        
        self._save_personas()
        logger.info(f"✅ Updated persona {persona_id}")
        return persona
    
    async def update_persona_metadata(self, persona_id: str, interaction_count: int, last_interaction: datetime):
        """Update persona interaction metadata"""
        if persona_id in self._personas_cache:
            persona = self._personas_cache[persona_id]
            persona.interaction_count = interaction_count
            persona.last_interaction = last_interaction
            persona.updated_at = datetime.utcnow()
            self._save_personas()
    
    async def delete_persona(self, persona_id: str) -> bool:
        """Delete a persona"""
        if persona_id in self._personas_cache:
            del self._personas_cache[persona_id]
            self._save_personas()
            logger.info(f"🗑️ Deleted persona {persona_id}")
            return True
        return False
    
    async def count_personas(self) -> int:
        """Get total count of personas"""
        return len(self._personas_cache)
    
    async def get_personas_by_state(self, state: str) -> List[Persona]:
        """Get all personas from a specific Brazilian state"""
        return [
            persona for persona in self._personas_cache.values()
            if persona.location_state == state
        ]
    
    async def get_personas_by_readiness(self, readiness_level: str) -> List[Persona]:
        """Get all personas with specific readiness level"""
        return [
            persona for persona in self._personas_cache.values()
            if persona.readiness_level == readiness_level
        ]
    
    async def search_personas(self, query: str) -> List[Persona]:
        """Search personas by name, location, or interests"""
        query_lower = query.lower()
        matching_personas = []
        
        for persona in self._personas_cache.values():
            if (query_lower in persona.name.lower() or
                query_lower in persona.location_city.lower() or
                query_lower in persona.location_state.lower() or
                any(query_lower in interest.lower() for interest in persona.green_interests) or
                any(query_lower in goal.lower() for goal in persona.career_goals)):
                matching_personas.append(persona)
        
        return matching_personas


# Global repository instance
persona_repository = PersonaRepository()