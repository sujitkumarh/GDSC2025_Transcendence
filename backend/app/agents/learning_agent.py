"""
Learning agent that suggests training programs, courses, and skill development.
Specialized in Brazilian green education and capacity building.
"""
from typing import Dict, Any, List
from .base_agent import BaseAgent
from app.models import Persona, AssistantRequest, LanguageCode
from app.services.mistral_provider import mistral_provider


class LearningAgent(BaseAgent):
    """
    Learning agent that provides personalized learning recommendations
    for green career development in the Brazilian context.
    """
    
    def __init__(self):
        super().__init__(
            name="learning_agent",
            description="Personalized learning guidance and training recommendations for Brazilian green careers"
        )
    
    async def process(self, request: AssistantRequest, persona: Persona, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process learning guidance and training recommendations"""
        
        self.logger.info(f"📚 Processing learning guidance for persona {persona.id}")
        
        learning_prompt = self._build_learning_prompt(request, persona, context)
        system_prompt = self.get_system_prompt(request.language)
        
        try:
            response = await mistral_provider.generate_text(
                prompt=learning_prompt,
                system_prompt=system_prompt,
                temperature=0.7,
                max_tokens=800
            )
            
            # Extract structured recommendations
            recommendations = self._parse_learning_recommendations(response["text"], persona)
            
            return {
                "agent": self.name,
                "learning_guidance": response["text"],
                "structured_recommendations": recommendations,
                "processing_time_ms": response["duration_ms"],
                "model_used": response["model"],
                "language": request.language
            }
            
        except Exception as e:
            self.logger.error(f"❌ Learning processing failed: {e}")
            return {
                "agent": self.name,
                "learning_guidance": self._get_fallback_learning_advice(persona, request.language),
                "structured_recommendations": self._get_fallback_recommendations(persona),
                "processing_time_ms": 100,
                "model_used": "fallback",
                "language": request.language
            }
    
    def _build_learning_prompt(self, request: AssistantRequest, persona: Persona, context: Dict[str, Any]) -> str:
        """Build learning-specific prompt"""
        persona_context = self.format_persona_context(persona)
        
        return f"""
Como especialista em educação e capacitação para carreiras verdes no Brasil, forneça recomendações personalizadas:

{persona_context}

Solicitação: "{request.message}"

Considerando o perfil do jovem, recomende:

1. **Cursos Online Gratuitos**:
   - Plataformas brasileiras (SENAI, SEBRAE, FGV)
   - MOOCs internacionais com certificação
   - Cursos específicos para seus interesses verdes

2. **Programas Presenciais Locais**:
   - Workshops e treinamentos em {persona.location_state}
   - Programas técnicos e profissionalizantes
   - Parcerias com empresas locais

3. **Certificações Relevantes**:
   - Certificações reconhecidas no mercado verde brasileiro
   - Custos e pré-requisitos realistas
   - Timeline de conclusão

4. **Desenvolvimento de Habilidades Práticas**:
   - Projetos hands-on que pode fazer
   - Oportunidades de voluntariado
   - Experiências de campo

5. **Sequência de Aprendizado**:
   - Ordem recomendada dos cursos
   - Marcos de progresso
   - Como aplicar o conhecimento

Considere suas limitações de tempo ({persona.time_availability}h/semana) e orçamento (R${persona.budget_constraint}/mês).
"""
    
    def _parse_learning_recommendations(self, response_text: str, persona: Persona) -> List[Dict[str, Any]]:
        """Parse AI response into structured learning recommendations"""
        
        # This would normally parse the AI response, but for now we'll return structured data
        recommendations = [
            {
                "id": "learn_001",
                "title": "Fundamentos de Energia Solar",
                "type": "online_course",
                "provider": "SENAI",
                "duration": "40 horas",
                "cost": "Gratuito",
                "location": "Online",
                "description": "Curso introdutório sobre sistemas fotovoltaicos e instalação",
                "relevance_score": 0.95,
                "prerequisites": ["Ensino médio completo"],
                "certification": True,
                "url": "https://cursos.senai.br/energia-solar",
                "difficulty": "Iniciante",
                "language": "pt-BR"
            },
            {
                "id": "learn_002",
                "title": "Gestão de Resíduos Sólidos",
                "type": "workshop",
                "provider": "SEBRAE",
                "duration": "16 horas",
                "cost": "R$ 150",
                "location": persona.location_city,
                "description": "Workshop prático sobre economia circular e gestão de resíduos",
                "relevance_score": 0.88,
                "prerequisites": ["Interesse no setor ambiental"],
                "certification": True,
                "difficulty": "Básico",
                "language": "pt-BR"
            },
            {
                "id": "learn_003",
                "title": "Agricultura Sustentável Digital",
                "type": "online_course",
                "provider": "EMBRAPA",
                "duration": "60 horas",
                "cost": "Gratuito",
                "location": "Online",
                "description": "Tecnologias digitais aplicadas à agricultura sustentável",
                "relevance_score": 0.82,
                "prerequisites": ["Conhecimentos básicos de agricultura"],
                "certification": True,
                "difficulty": "Intermediário",
                "language": "pt-BR"
            }
        ]
        
        return recommendations
    
    def _get_fallback_learning_advice(self, persona: Persona, language: LanguageCode) -> str:
        """Provide fallback learning advice when AI fails"""
        if language == LanguageCode.PT_BR:
            return f"""
Com base no seu perfil e interesses em {persona.location_state}, aqui estão as principais recomendações de aprendizado:

🎓 **Cursos Online Gratuitos:**
• SENAI - Cursos de Energia Renovável
• SEBRAE - Empreendedorismo Sustentável  
• FGV - Sustentabilidade e ESG
• Coursera - Introdução às Energias Renováveis

📍 **Oportunidades Locais em {persona.location_state}:**
• Workshops do SEBRAE sobre economia circular
• Programas técnicos em institutos federais
• Palestras em universidades locais
• Eventos de sustentabilidade empresarial

🏆 **Certificações Recomendadas:**
• Certificação em Energia Solar (SENAI)
• Green Belt em Sustentabilidade
• Certificação em Gestão Ambiental
• Curso de Auditor Ambiental

⏰ **Plano de Estudos (considerando {persona.time_availability}h/semana):**
1. Mês 1-2: Fundamentos de sustentabilidade
2. Mês 3-4: Especialização na área de interesse
3. Mês 5-6: Projeto prático ou estágio

💰 **Dentro do orçamento de R${persona.budget_constraint}/mês:**
• Maioria dos cursos SENAI/SEBRAE são gratuitos
• Certificações pagas: R$100-300
• Material de estudo: R$50-100/mês
"""
        else:
            return f"""
Based on your profile and interests in {persona.location_state}, here are the main learning recommendations:

🎓 **Free Online Courses:**
• SENAI - Renewable Energy Courses
• SEBRAE - Sustainable Entrepreneurship
• FGV - Sustainability and ESG
• Coursera - Introduction to Renewable Energy

📍 **Local Opportunities in {persona.location_state}:**
• SEBRAE workshops on circular economy
• Technical programs at federal institutes
• University lectures
• Corporate sustainability events

🏆 **Recommended Certifications:**
• Solar Energy Certification (SENAI)
• Green Belt in Sustainability
• Environmental Management Certification
• Environmental Auditor Course

Remember: Focus on practical skills that are in demand in Brazil's growing green economy!
"""
    
    def _get_fallback_recommendations(self, persona: Persona) -> List[Dict[str, Any]]:
        """Provide fallback structured recommendations"""
        return [
            {
                "id": "learn_fallback_001",
                "title": "Curso Básico de Sustentabilidade",
                "type": "online_course",
                "provider": "SENAI",
                "duration": "20 horas",
                "cost": "Gratuito",
                "location": "Online",
                "description": "Introdução aos conceitos fundamentais de sustentabilidade",
                "relevance_score": 0.75,
                "prerequisites": ["Ensino médio"],
                "certification": True,
                "difficulty": "Iniciante",
                "language": "pt-BR"
            }
        ]
    
    def get_system_prompt(self, language: LanguageCode) -> str:
        """Get learning agent system prompt"""
        if language == LanguageCode.PT_BR:
            return """
Você é um especialista em educação e capacitação para carreiras verdes no Brasil, 
focado em jovens de 16-24 anos com diferentes níveis de preparação.

Expertise:
- Programas de capacitação brasileiros (SENAI, SEBRAE, SENAR, etc.)
- Cursos online gratuitos e pagos
- Certificações reconhecidas no mercado verde
- Programas técnicos e superiores
- Oportunidades de aprendizado prático
- Cronogramas realistas de estudo

Princípios:
- Considere limitações de tempo e orçamento
- Priorize cursos gratuitos ou de baixo custo
- Adapte à região e disponibilidade local
- Inclua aprendizado prático e teórico
- Sugira progressão lógica de conhecimento
- Seja realista sobre pré-requisitos
- Enfatize certificações reconhecidas pelo mercado

Áreas de foco: energia renovável, gestão ambiental, agricultura sustentável,
economia circular, ESG, tecnologias limpas, construção verde.
"""
        else:
            return """
You are a learning specialist for green careers in Brazil, 
focused on youth aged 16-24 with different preparation levels.

Expertise:
- Brazilian training programs (SENAI, SEBRAE, SENAR, etc.)
- Free and paid online courses
- Market-recognized certifications
- Technical and higher education programs
- Practical learning opportunities
- Realistic study schedules

Principles:
- Consider time and budget limitations
- Prioritize free or low-cost courses
- Adapt to region and local availability
- Include practical and theoretical learning
- Suggest logical knowledge progression
- Be realistic about prerequisites
- Emphasize market-recognized certifications

Focus areas: renewable energy, environmental management, sustainable agriculture,
circular economy, ESG, clean technologies, green construction.
"""