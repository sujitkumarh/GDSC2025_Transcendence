"""
Career agent that maps personas to green job families and opportunities.
Specialized in Brazilian green job market analysis.
"""
from typing import Dict, Any
from .base_agent import BaseAgent
from app.models import Persona, AssistantRequest, LanguageCode
from app.services.mistral_provider import mistral_provider


class CareerAgent(BaseAgent):
    """
    Career agent that maps personas to green job families and opportunities.
    Specialized in Brazilian green job market analysis.
    """
    
    def __init__(self):
        super().__init__(
            name="career_agent", 
            description="Green job discovery and career mapping for Brazilian youth"
        )
    
    async def process(self, request: AssistantRequest, persona: Persona, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process career exploration and job matching"""
        
        self.logger.info(f"💼 Processing career guidance for persona {persona.id}")
        
        career_prompt = self._build_career_prompt(request, persona, context)
        system_prompt = self.get_system_prompt(request.language)
        
        try:
            response = await mistral_provider.generate_text(
                prompt=career_prompt,
                system_prompt=system_prompt,
                temperature=0.6,
                max_tokens=600
            )
            
            return {
                "agent": self.name,
                "career_guidance": response["text"],
                "processing_time_ms": response["duration_ms"],
                "model_used": response["model"],
                "language": request.language
            }
            
        except Exception as e:
            self.logger.error(f"❌ Career processing failed: {e}")
            return {
                "agent": self.name,
                "career_guidance": self._get_fallback_career_advice(persona, request.language),
                "processing_time_ms": 100,
                "model_used": "fallback",
                "language": request.language
            }
    
    def _build_career_prompt(self, request: AssistantRequest, persona: Persona, context: Dict[str, Any]) -> str:
        """Build career-specific prompt"""
        persona_context = self.format_persona_context(persona)
        
        return f"""
Como especialista em carreiras verdes no Brasil, forneça orientação personalizada para este jovem:

{persona_context}

Solicitação: "{request.message}"

Considerando o perfil do jovem, forneça:

1. Análise das oportunidades de carreira verde mais adequadas para seu perfil
2. Setores em crescimento no Brasil que se alinham com seus interesses
3. Papéis de entrada (junior/trainee) disponíveis em sua região
4. Requisitos realistas considerando sua educação e experiência atual
5. Perspectivas de crescimento e desenvolvimento na carreira
6. Empresas ou setores específicos para focar em {persona.location_state}

Seja específico sobre:
- Oportunidades em energia renovável, gestão de resíduos, agricultura sustentável
- Salários típicos para posições iniciantes
- Progressão de carreira realista
- Como superar lacunas de habilidades

Mantenha o tom encorajador e prático, focando em próximos passos concretos.
"""
    
    def _get_fallback_career_advice(self, persona: Persona, language: LanguageCode) -> str:
        """Provide fallback career advice when AI fails"""
        if language == LanguageCode.PT_BR:
            return f"""
Com base no seu perfil em {persona.location_state}, aqui estão algumas oportunidades verdes promissoras:

🌞 **Energia Solar**: O Brasil tem grande potencial solar. Considere cursos de instalação e manutenção de painéis solares.

🌱 **Agricultura Sustentável**: Oportunidades em agricultura orgânica e tecnologias agrícolas sustentáveis.

♻️ **Gestão de Resíduos**: Setor em crescimento com necessidade de profissionais para reciclagem e economia circular.

🌿 **Consultoria ESG**: Empresas precisam de profissionais para sustentabilidade corporativa.

**Próximos passos recomendados:**
1. Pesquise programas de capacitação locais no SENAI ou instituições regionais
2. Conecte-se com empresas verdes em sua região
3. Considere começar com estágios ou trabalho voluntário
4. Desenvolva habilidades em sustentabilidade e tecnologias verdes

Lembre-se: o setor verde no Brasil está crescendo rapidamente, oferecendo boas oportunidades para jovens motivados!
"""
        else:
            return f"""
Based on your profile in {persona.location_state}, here are promising green opportunities:

🌞 **Solar Energy**: Brazil has great solar potential. Consider solar panel installation and maintenance courses.

🌱 **Sustainable Agriculture**: Opportunities in organic farming and sustainable agricultural technologies.

♻️ **Waste Management**: Growing sector needing professionals for recycling and circular economy.

🌿 **ESG Consulting**: Companies need sustainability professionals.

**Recommended next steps:**
1. Research local training programs at SENAI or regional institutions
2. Connect with green companies in your region
3. Consider starting with internships or volunteer work
4. Develop skills in sustainability and green technologies

Remember: Brazil's green sector is growing rapidly, offering good opportunities for motivated youth!
"""
    
    def get_system_prompt(self, language: LanguageCode) -> str:
        """Get career agent system prompt"""
        if language == LanguageCode.PT_BR:
            return """
Você é um especialista em carreiras verdes no Brasil, com foco em orientar jovens de 16-24 anos.

Expertise:
- Mercado de trabalho verde brasileiro
- Oportunidades regionais por estado
- Requisitos de entrada para diferentes setores
- Progressão de carreira realista
- Salários e benefícios típicos
- Programas de capacitação disponíveis

Abordagem:
- Seja prático e realista sobre oportunidades
- Considere limitações socioeconômicas
- Foque em setores em crescimento no Brasil
- Adapte recomendações à região do jovem
- Seja encorajador mas honesto sobre desafios
- Enfatize oportunidades de desenvolvimento
- Use linguagem acessível e empática

Setores prioritários: energia renovável, gestão de resíduos, agricultura sustentável, 
veículos elétricos, silvicultura, construção sustentável, consultoria ESG.
"""
        else:
            return """
You are a green career specialist in Brazil, focused on guiding youth aged 16-24.

Expertise:
- Brazilian green job market
- Regional opportunities by state
- Entry requirements for different sectors
- Realistic career progression
- Typical salaries and benefits
- Available training programs

Approach:
- Be practical and realistic about opportunities
- Consider socioeconomic limitations
- Focus on growing sectors in Brazil
- Adapt recommendations to youth's region
- Be encouraging but honest about challenges
- Emphasize development opportunities
- Use accessible and empathetic language

Priority sectors: renewable energy, waste management, sustainable agriculture,
electric vehicles, forestry, sustainable construction, ESG consulting.
"""