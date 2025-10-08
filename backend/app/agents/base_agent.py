"""
Base agent class with common functionality for all Transcendence agents.
"""
from typing import Dict, Any
from datetime import datetime
from loguru import logger

from app.models import Persona, AssistantRequest, LanguageCode


class BaseAgent:
    """Base agent class with common functionality"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.logger = logger.bind(agent=name)
        
    async def process(self, request: AssistantRequest, persona: Persona, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process a request and return response data"""
        raise NotImplementedError("Subclasses must implement process method")
    
    def get_system_prompt(self, language: LanguageCode) -> str:
        """Get system prompt for this agent in specified language"""
        raise NotImplementedError("Subclasses must implement get_system_prompt method")
    
    def format_persona_context(self, persona: Persona) -> str:
        """Format persona information for AI context"""
        return f"""
Persona: {persona.name}
Idade: {persona.age} anos
Localização: {persona.location_city}, {persona.location_state}
Educação: {persona.education_level}
Idioma Preferido: {persona.preferred_language}
Nível de Prontidão: {persona.readiness_level}
Interesses Verdes: {', '.join(persona.green_interests)}
Disponibilidade: {persona.time_availability} horas/semana
Orçamento: R$ {persona.budget_constraint}/mês
Objetivos: {', '.join(persona.career_goals)}
Acesso à Tecnologia: {'Smartphone' if persona.has_smartphone else 'Sem smartphone'}, {'Internet' if persona.has_internet else 'Sem internet'}
Conforto Tecnológico: {persona.tech_comfort_level}/5
"""