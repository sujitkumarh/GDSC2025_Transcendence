"""
Router agent that analyzes requests and determines appropriate task routing.
Inspired by Project B's journey agent patterns.
"""
from typing import Dict, Any
import json
from .base_agent import BaseAgent
from app.models import Persona, AssistantRequest, LanguageCode
from app.services.mistral_provider import mistral_provider


class RouterAgent(BaseAgent):
    """
    Router agent that analyzes requests and determines appropriate task routing.
    Inspired by Project B's journey agent patterns.
    """
    
    def __init__(self):
        super().__init__(
            name="router_agent",
            description="Intelligent request routing and task classification for Brazilian youth green career guidance"
        )
    
    async def process(self, request: AssistantRequest, persona: Persona, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Route request to appropriate task type and gather initial analysis"""
        
        self.logger.info(f"🎯 Routing request for persona {persona.id}")
        
        # Build routing prompt
        routing_prompt = self._build_routing_prompt(request, persona)
        system_prompt = self.get_system_prompt(request.language)
        
        try:
            # Get AI analysis for routing
            response = await mistral_provider.generate_text(
                prompt=routing_prompt,
                system_prompt=system_prompt,
                temperature=0.3,  # Lower temperature for consistent routing
                max_tokens=300
            )
            
            # Parse AI response to determine routing
            routing_analysis = self._parse_routing_response(response["text"])
            
            self.logger.info(f"✅ Routed to {routing_analysis['recommended_task']} with confidence {routing_analysis['confidence']}")
            
            return {
                "agent": self.name,
                "recommended_task": routing_analysis["recommended_task"],
                "confidence": routing_analysis["confidence"],
                "reasoning": routing_analysis["reasoning"],
                "persona_insights": routing_analysis["persona_insights"],
                "suggested_agents": routing_analysis["suggested_agents"],
                "language": request.language,
                "processing_time_ms": response["duration_ms"]
            }
            
        except Exception as e:
            self.logger.error(f"❌ Routing failed: {e}")
            # Fallback routing based on simple rules
            return self._fallback_routing(request, persona)
    
    def _build_routing_prompt(self, request: AssistantRequest, persona: Persona) -> str:
        """Build prompt for routing analysis"""
        persona_context = self.format_persona_context(persona)
        
        return f"""
Analise esta solicitação de um jovem brasileiro interessado em carreiras verdes:

{persona_context}

Mensagem do usuário: "{request.message}"
Tipo de tarefa solicitada: {request.task_type}

Com base no perfil do jovem e na mensagem, determine:

1. Qual tipo de tarefa é mais apropriado:
   - AWARENESS: Conscientização geral sobre carreiras verdes
   - CAREER_EXPLORATION: Exploração específica de oportunidades de trabalho
   - SKILL_ASSESSMENT: Avaliação de habilidades e lacunas
   - LEARNING_GUIDANCE: Orientação sobre treinamentos e cursos
   - PATHWAY_PLANNING: Planejamento de carreira passo a passo

2. Insights sobre o perfil do jovem (readiness, motivação, limitações)
3. Agentes especializados que devem ser envolvidos
4. Confiança na recomendação (0-1)
5. Justificativa para a escolha

Responda em formato JSON:
{{
    "recommended_task": "tipo_de_tarefa",
    "confidence": 0.0-1.0,
    "reasoning": "explicação_da_escolha",
    "persona_insights": ["insight1", "insight2"],
    "suggested_agents": ["agent1", "agent2"]
}}
"""
    
    def _parse_routing_response(self, response_text: str) -> Dict[str, Any]:
        """Parse AI routing response"""
        try:
            # Try to extract JSON from response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                parsed = json.loads(json_str)
                
                # Validate and clean the response
                return {
                    "recommended_task": parsed.get("recommended_task", "AWARENESS"),
                    "confidence": min(max(float(parsed.get("confidence", 0.5)), 0.0), 1.0),
                    "reasoning": parsed.get("reasoning", "Análise automática baseada no perfil"),
                    "persona_insights": parsed.get("persona_insights", []),
                    "suggested_agents": parsed.get("suggested_agents", ["career_agent"])
                }
            else:
                raise ValueError("No JSON found in response")
                
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            self.logger.warning(f"⚠️ Failed to parse routing response: {e}")
            # Return default routing
            return {
                "recommended_task": "AWARENESS",
                "confidence": 0.5,
                "reasoning": "Fallback routing due to parsing error",
                "persona_insights": ["Perfil requer análise manual"],
                "suggested_agents": ["career_agent"]
            }
    
    def _fallback_routing(self, request: AssistantRequest, persona: Persona) -> Dict[str, Any]:
        """Fallback routing when AI analysis fails"""
        
        # Simple rule-based routing
        message_lower = request.message.lower()
        
        if any(word in message_lower for word in ["curso", "treinamento", "aprender", "estudar"]):
            task = "LEARNING_GUIDANCE"
            agents = ["learning_agent"]
        elif any(word in message_lower for word in ["emprego", "trabalho", "vaga", "carreira"]):
            task = "CAREER_EXPLORATION" 
            agents = ["career_agent"]
        elif any(word in message_lower for word in ["habilidade", "skill", "competência", "experiência"]):
            task = "SKILL_ASSESSMENT"
            agents = ["career_agent", "learning_agent"]
        elif any(word in message_lower for word in ["plano", "caminho", "próximos passos", "como começar"]):
            task = "PATHWAY_PLANNING"
            agents = ["guidance_agent"]
        else:
            task = "AWARENESS"
            agents = ["career_agent"]
        
        return {
            "agent": self.name,
            "recommended_task": task,
            "confidence": 0.7,
            "reasoning": "Roteamento baseado em regras de palavras-chave",
            "persona_insights": [f"Nível de prontidão: {persona.readiness_level}"],
            "suggested_agents": agents,
            "language": request.language,
            "processing_time_ms": 50
        }
    
    def get_system_prompt(self, language: LanguageCode) -> str:
        """Get system prompt for routing agent"""
        if language == LanguageCode.PT_BR:
            return """
Você é um agente especialista em orientação de carreira verde para jovens brasileiros. 
Sua função é analisar solicitações e determinar o melhor tipo de assistência.

Diretrizes:
- Considere o nível de prontidão do jovem (exploring, interested, preparing, ready, experienced)
- Avalie limitações de tempo, orçamento e localização
- Priorize oportunidades locais e acessíveis
- Seja empático e encorajador
- Foque em empregos verdes relevantes para o Brasil
- Considere o contexto socioeconômico brasileiro
- Responda sempre em português brasileiro amigável

Mantenha o foco em carreiras sustentáveis: energia solar/eólica, gestão de resíduos, 
agricultura sustentável, veículos elétricos, silvicultura, consultoria ESG.
"""
        else:
            return """
You are a routing agent specialized in green career guidance for Brazilian youth.
Your role is to analyze requests and determine the best type of assistance needed.

Guidelines:
- Consider the youth's readiness level (exploring, interested, preparing, ready, experienced)
- Evaluate time, budget, and location constraints
- Prioritize local and accessible opportunities
- Be empathetic and encouraging
- Focus on green jobs relevant to Brazil
- Consider Brazilian socioeconomic context
- Always respond in friendly Brazilian Portuguese when appropriate

Focus on sustainable careers: solar/wind energy, waste management, 
sustainable agriculture, electric vehicles, forestry, ESG consulting.
"""