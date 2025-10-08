"""
Guidance agent that creates actionable step-by-step pathways for green career development.
Provides structured planning and milestone tracking for Brazilian youth.
"""
from typing import Dict, Any, List
from datetime import datetime, timedelta
from .base_agent import BaseAgent
from app.models import Persona, AssistantRequest, LanguageCode
from app.services.mistral_provider import mistral_provider


class GuidanceAgent(BaseAgent):
    """
    Guidance agent that creates personalized, actionable pathways
    for green career development in the Brazilian context.
    """
    
    def __init__(self):
        super().__init__(
            name="guidance_agent",
            description="Personalized pathway planning and step-by-step guidance for Brazilian green careers"
        )
    
    async def process(self, request: AssistantRequest, persona: Persona, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process guidance request and create actionable pathway"""
        
        self.logger.info(f"🛤️ Processing guidance pathway for persona {persona.id}")
        
        guidance_prompt = self._build_guidance_prompt(request, persona, context)
        system_prompt = self.get_system_prompt(request.language)
        
        try:
            response = await mistral_provider.generate_text(
                prompt=guidance_prompt,
                system_prompt=system_prompt,
                temperature=0.7,
                max_tokens=1000
            )
            
            # Create structured pathway
            pathway = self._create_structured_pathway(response["text"], persona, request)
            
            return {
                "agent": self.name,
                "guidance_text": response["text"],
                "structured_pathway": pathway,
                "processing_time_ms": response["duration_ms"],
                "model_used": response["model"],
                "language": request.language
            }
            
        except Exception as e:
            self.logger.error(f"❌ Guidance processing failed: {e}")
            return {
                "agent": self.name,
                "guidance_text": self._get_fallback_guidance_advice(persona, request.language),
                "structured_pathway": self._get_fallback_pathway(persona),
                "processing_time_ms": 100,
                "model_used": "fallback",
                "language": request.language
            }
    
    def _build_guidance_prompt(self, request: AssistantRequest, persona: Persona, context: Dict[str, Any]) -> str:
        """Build guidance-specific prompt"""
        persona_context = self.format_persona_context(persona)
        
        return f"""
Como conselheiro de carreira especializado em sustentabilidade no Brasil, crie um plano de ação personalizado:

{persona_context}

Solicitação: "{request.message}"

Crie um plano de desenvolvimento de carreira estruturado considerando:

1. **Avaliação da Situação Atual**:
   - Pontos fortes do perfil
   - Lacunas a serem preenchidas
   - Oportunidades imediatas

2. **Definição de Objetivos** (baseado nos interesses do jovem):
   - Objetivo de curto prazo (3-6 meses)
   - Objetivo de médio prazo (6-12 meses)
   - Visão de longo prazo (1-2 anos)

3. **Plano de Ação Detalhado**:
   - 6-8 passos específicos e mensuráveis
   - Cronograma realista para cada etapa
   - Recursos necessários (tempo, dinheiro, materiais)
   - Marcos de progresso

4. **Estratégias Específicas para {persona.location_state}**:
   - Aproveitamento de oportunidades locais
   - Rede de contatos regional
   - Recursos e instituições disponíveis

5. **Superação de Obstáculos**:
   - Limitações identificadas no perfil
   - Estratégias para contornar restrições
   - Planos alternativos

6. **Métricas de Sucesso**:
   - Como medir progresso
   - Indicadores de que está no caminho certo
   - Quando reavaliar o plano

Considere:
- Disponibilidade de tempo: {persona.time_availability} horas/semana
- Orçamento: R$ {persona.budget_constraint}/mês
- Nível de prontidão: {persona.readiness_level}
- Acesso à tecnologia: {'Limitado' if not persona.has_smartphone or not persona.has_internet else 'Completo'}
"""
    
    def _create_structured_pathway(self, response_text: str, persona: Persona, request: AssistantRequest) -> Dict[str, Any]:
        """Create structured pathway from AI response"""
        
        # Calculate dates for milestones
        start_date = datetime.now()
        
        pathway = {
            "pathway_id": f"path_{persona.id}_{int(start_date.timestamp())}",
            "title": f"Jornada Verde para {persona.name}",
            "description": "Plano personalizado para desenvolvimento de carreira sustentável",
            "created_date": start_date.isoformat(),
            "estimated_duration": "6-12 meses",
            "total_estimated_cost": f"R$ {min(persona.budget_constraint * 6, 2000)} - R$ {persona.budget_constraint * 12}",
            "difficulty_level": self._assess_difficulty(persona),
            "target_persona": {
                "name": persona.name,
                "location": f"{persona.location_city}, {persona.location_state}",
                "readiness_level": persona.readiness_level,
                "interests": persona.green_interests
            },
            "objectives": {
                "short_term": "Desenvolver conhecimentos fundamentais e identificar oportunidades específicas",
                "medium_term": "Adquirir experiência prática e construir rede de contatos profissionais",
                "long_term": "Estabelecer-se profissionalmente no setor verde brasileiro"
            },
            "steps": self._generate_pathway_steps(persona),
            "milestones": self._generate_milestones(persona),
            "resources": self._generate_resources(persona),
            "success_metrics": [
                "Completar pelo menos 2 cursos/certificações por trimestre",
                "Estabelecer contatos com 5-10 profissionais do setor",
                "Participar de pelo menos 1 projeto prático",
                "Candidatar-se a 3-5 oportunidades relevantes"
            ],
            "potential_obstacles": self._identify_obstacles(persona),
            "support_network": [
                "Mentores do setor sustentável",
                "Colegas de cursos e workshops",
                "Profissionais em redes sociais profissionais",
                "Comunidades online de sustentabilidade"
            ]
        }
        
        return pathway
    
    def _assess_difficulty(self, persona: Persona) -> str:
        """Assess pathway difficulty based on persona profile"""
        if persona.readiness_level in ["ready", "experienced"]:
            return "Intermediário"
        elif persona.readiness_level in ["interested", "preparing"]:
            return "Básico-Intermediário"
        else:
            return "Básico"
    
    def _generate_pathway_steps(self, persona: Persona) -> List[Dict[str, Any]]:
        """Generate specific pathway steps"""
        steps = [
            {
                "step": 1,
                "title": "Autoavaliação e Definição de Foco",
                "description": "Identificar pontos fortes, interesses específicos e definir área de foco principal",
                "duration": "1-2 semanas",
                "cost": "Gratuito",
                "actions": [
                    "Completar testes vocacionais online",
                    "Pesquisar sobre diferentes áreas verdes",
                    "Definir 2-3 áreas prioritárias de interesse",
                    "Mapear habilidades atuais vs. necessárias"
                ],
                "deliverables": ["Relatório de autoavaliação", "Lista de áreas prioritárias"],
                "success_criteria": "Ter clareza sobre direção preferida"
            },
            {
                "step": 2,
                "title": "Capacitação Fundamental",
                "description": "Adquirir conhecimentos básicos em sustentabilidade e área de interesse",
                "duration": "4-6 semanas",
                "cost": "R$ 0 - R$ 300",
                "actions": [
                    "Inscrever-se em curso básico de sustentabilidade (SENAI/SEBRAE)",
                    "Participar de webinars do setor",
                    "Ler artigos e relatórios setoriais",
                    "Seguir influenciadores e empresas do setor"
                ],
                "deliverables": ["Certificado de curso básico", "Portfolio de conhecimentos"],
                "success_criteria": "Compreender fundamentos da área escolhida"
            },
            {
                "step": 3,
                "title": "Networking e Conexões",
                "description": "Construir rede de contatos profissionais no setor verde",
                "duration": "2-4 semanas (contínuo)",
                "cost": "R$ 50 - R$ 150",
                "actions": [
                    "Participar de eventos virtuais do setor",
                    "Conectar-se com profissionais no LinkedIn",
                    "Ingressar em grupos e comunidades online",
                    "Participar de meetups locais"
                ],
                "deliverables": ["Lista de 20+ contatos profissionais", "Participação ativa em comunidades"],
                "success_criteria": "Ter conversas regulares com profissionais do setor"
            },
            {
                "step": 4,
                "title": "Experiência Prática",
                "description": "Ganhar experiência hands-on através de projetos ou voluntariado",
                "duration": "6-8 semanas",
                "cost": "R$ 100 - R$ 500",
                "actions": [
                    "Candidatar-se a programas de voluntariado ambiental",
                    "Desenvolver projeto pessoal relacionado à área",
                    "Buscar estágios ou trabalhos temporários",
                    "Participar de hackathons ou competições"
                ],
                "deliverables": ["Portfolio de projetos", "Referências profissionais"],
                "success_criteria": "Ter experiência documentada na área"
            },
            {
                "step": 5,
                "title": "Especialização Técnica",
                "description": "Desenvolver habilidades técnicas específicas para a área escolhida",
                "duration": "8-12 semanas",
                "cost": f"R$ {min(persona.budget_constraint * 2, 800)} - R$ {min(persona.budget_constraint * 4, 1500)}",
                "actions": [
                    "Fazer curso técnico específico da área",
                    "Obter certificações reconhecidas pelo mercado",
                    "Participar de workshops práticos",
                    "Desenvolver projeto técnico complexo"
                ],
                "deliverables": ["Certificações técnicas", "Projeto técnico completo"],
                "success_criteria": "Ter competências técnicas demandadas pelo mercado"
            },
            {
                "step": 6,
                "title": "Busca Ativa por Oportunidades",
                "description": "Aplicar conhecimentos e rede para encontrar oportunidades profissionais",
                "duration": "4-8 semanas (contínuo)",
                "cost": "R$ 100 - R$ 300",
                "actions": [
                    "Atualizar currículo com novas competências",
                    "Candidatar-se a vagas relevantes",
                    "Propor projetos para empresas locais",
                    "Considerar empreendedorismo verde"
                ],
                "deliverables": ["Currículo otimizado", "Candidaturas ativas"],
                "success_criteria": "Ter oportunidades concretas de trabalho ou projetos"
            }
        ]
        
        return steps
    
    def _generate_milestones(self, persona: Persona) -> List[Dict[str, Any]]:
        """Generate pathway milestones"""
        return [
            {
                "milestone": "Conhecimento Fundamental",
                "description": "Compreender os fundamentos da área verde escolhida",
                "target_date": (datetime.now() + timedelta(weeks=8)).strftime("%Y-%m-%d"),
                "success_indicators": ["Certificado básico obtido", "Capacidade de explicar conceitos fundamentais"]
            },
            {
                "milestone": "Rede Profissional Estabelecida",
                "description": "Ter contatos ativos no setor verde",
                "target_date": (datetime.now() + timedelta(weeks=12)).strftime("%Y-%m-%d"),
                "success_indicators": ["20+ conexões relevantes", "Participação regular em eventos"]
            },
            {
                "milestone": "Experiência Prática Documentada",
                "description": "Ter portfólio de projetos ou experiências práticas",
                "target_date": (datetime.now() + timedelta(weeks=16)).strftime("%Y-%m-%d"),
                "success_indicators": ["Projeto completo no portfólio", "Referências profissionais"]
            },
            {
                "milestone": "Competência Técnica Reconhecida",
                "description": "Ter habilidades técnicas demandadas pelo mercado",
                "target_date": (datetime.now() + timedelta(weeks=24)).strftime("%Y-%m-%d"),
                "success_indicators": ["Certificações técnicas", "Competências validadas por profissionais"]
            },
            {
                "milestone": "Oportunidade Profissional Concreta",
                "description": "Ter oportunidade real de trabalho ou projeto na área",
                "target_date": (datetime.now() + timedelta(weeks=32)).strftime("%Y-%m-%d"),
                "success_indicators": ["Oferta de trabalho", "Projeto remunerado", "Proposta aceita"]
            }
        ]
    
    def _generate_resources(self, persona: Persona) -> Dict[str, List[str]]:
        """Generate resources specific to persona's location and interests"""
        return {
            "instituicoes_ensino": [
                "SENAI - Cursos técnicos e de capacitação",
                "SEBRAE - Empreendedorismo e gestão",
                "SENAR - Agricultura sustentável",
                f"Universidades em {persona.location_state}",
                "IFES - Institutos Federais de Educação"
            ],
            "plataformas_online": [
                "Coursera - Cursos internacionais com certificação",
                "EdX - Cursos de universidades renomadas",
                "FGV Online - Cursos de sustentabilidade",
                "ESALQ/USP - Agricultura sustentável",
                "CEBDS - Conselho Empresarial Brasileiro para o Desenvolvimento Sustentável"
            ],
            "eventos_networking": [
                f"Eventos de sustentabilidade em {persona.location_state}",
                "Feira Brasileira de Energia Solar",
                "Congresso Brasileiro de Gestão Ambiental",
                "Semana Nacional do Meio Ambiente",
                "Meetups locais de sustentabilidade"
            ],
            "organizacoes_apoio": [
                "WWF Brasil",
                "Greenpeace Brasil",
                "Instituto Ethos",
                "FBDS - Fundação Brasileira para o Desenvolvimento Sustentável",
                f"Secretaria de Meio Ambiente de {persona.location_state}"
            ],
            "ferramentas_online": [
                "LinkedIn - Networking profissional",
                "GitHub - Portfolio de projetos técnicos",
                "Behance - Portfolio visual/design",
                "ResearchGate - Artigos acadêmicos",
                "Google Scholar - Pesquisas científicas"
            ]
        }
    
    def _identify_obstacles(self, persona: Persona) -> List[Dict[str, str]]:
        """Identify potential obstacles and mitigation strategies"""
        obstacles = []
        
        if persona.budget_constraint < 200:
            obstacles.append({
                "obstacle": "Limitação orçamentária",
                "mitigation": "Focar em cursos gratuitos (SENAI, SEBRAE) e bolsas de estudo"
            })
        
        if persona.time_availability < 10:
            obstacles.append({
                "obstacle": "Pouco tempo disponível",
                "mitigation": "Priorizar cursos online flexíveis e micro-learning"
            })
        
        if not persona.has_internet or not persona.has_smartphone:
            obstacles.append({
                "obstacle": "Acesso limitado à tecnologia",
                "mitigation": "Usar lan houses, bibliotecas públicas e programas presenciais"
            })
        
        if persona.readiness_level == "exploring":
            obstacles.append({
                "obstacle": "Falta de direcionamento específico",
                "mitigation": "Começar com cursos introdutórios amplos para descobrir preferências"
            })
        
        return obstacles
    
    def _get_fallback_guidance_advice(self, persona: Persona, language: LanguageCode) -> str:
        """Provide fallback guidance advice when AI fails"""
        if language == LanguageCode.PT_BR:
            return f"""
Plano de Desenvolvimento Personalizado para {persona.name}

🎯 **Objetivo Principal**: Desenvolver carreira sustentável em {persona.location_state}

📋 **Plano de Ação (6 meses):**

**Fase 1 - Fundação (Mês 1-2):**
• Complete curso básico de sustentabilidade (SENAI/SEBRAE)
• Identifique área específica de interesse
• Comece a seguir empresas verdes locais
• Participe de webinars gratuitos do setor

**Fase 2 - Desenvolvimento (Mês 3-4):**
• Faça curso técnico na área escolhida
• Participe de eventos de networking online
• Conecte-se com profissionais no LinkedIn
• Inicie projeto pessoal relacionado à área

**Fase 3 - Aplicação (Mês 5-6):**
• Busque oportunidades de voluntariado/estágio
• Candidate-se a vagas júnior
• Apresente projeto em eventos locais
• Considere empreendedorismo verde

🎯 **Marcos de Progresso:**
□ Certificação básica em sustentabilidade
□ 20+ conexões profissionais relevantes
□ Projeto prático concluído
□ Primeira oportunidade profissional

💰 **Investimento**: R$ {persona.budget_constraint * 3} - R$ {persona.budget_constraint * 6}
⏰ **Tempo**: {persona.time_availability} horas/semana
"""
        else:
            return f"""
Personalized Development Plan for {persona.name}

🎯 **Main Goal**: Develop sustainable career in {persona.location_state}

📋 **Action Plan (6 months):**

**Phase 1 - Foundation (Month 1-2):**
• Complete basic sustainability course (SENAI/SEBRAE)
• Identify specific area of interest
• Start following local green companies
• Participate in free sector webinars

**Phase 2 - Development (Month 3-4):**
• Take technical course in chosen area
• Participate in online networking events
• Connect with professionals on LinkedIn
• Start personal project related to the area

**Phase 3 - Application (Month 5-6):**
• Seek volunteer/internship opportunities
• Apply for junior positions
• Present project at local events
• Consider green entrepreneurship

Remember: Focus on practical skills and local opportunities in Brazil's growing green economy!
"""
    
    def _get_fallback_pathway(self, persona: Persona) -> Dict[str, Any]:
        """Provide fallback structured pathway"""
        return {
            "pathway_id": f"path_fallback_{persona.id}",
            "title": f"Caminho Verde Básico para {persona.name}",
            "description": "Plano básico de desenvolvimento de carreira sustentável",
            "estimated_duration": "6 meses",
            "steps": [
                {
                    "step": 1,
                    "title": "Aprender Fundamentos",
                    "duration": "4 semanas",
                    "cost": "Gratuito"
                },
                {
                    "step": 2,
                    "title": "Desenvolver Habilidades",
                    "duration": "8 semanas",
                    "cost": "R$ 200-500"
                },
                {
                    "step": 3,
                    "title": "Buscar Oportunidades",
                    "duration": "4 semanas",
                    "cost": "R$ 100-200"
                }
            ]
        }
    
    def get_system_prompt(self, language: LanguageCode) -> str:
        """Get guidance agent system prompt"""
        if language == LanguageCode.PT_BR:
            return """
Você é um conselheiro de carreira especializado em orientação para carreiras verdes no Brasil,
com foco em jovens de 16-24 anos de diferentes backgrounds socioeconômicos.

Expertise:
- Planejamento de carreira estruturado e realista
- Conhecimento profundo do mercado verde brasileiro
- Metodologias de desenvolvimento profissional
- Estratégias de superação de barreiras socioeconômicas
- Networking e construção de relacionamentos profissionais

Abordagem de Orientação:
- Criar planos específicos, mensuráveis e alcançáveis
- Considerar limitações reais (tempo, dinheiro, localização)
- Incluir marcos de progresso claros
- Adaptar estratégias ao perfil individual
- Ser empático mas realista sobre desafios
- Focar em ações concretas e próximos passos
- Incluir estratégias de superação de obstáculos

Princípios:
- Todo jovem tem potencial para carreira verde
- Pequenos passos consistentes levam a grandes resultados
- Networking e experiência prática são fundamentais
- Aprendizado contínuo é essencial no setor verde
- Oportunidades locais são prioritárias
- Empreendedorismo pode ser uma alternativa viável
"""
        else:
            return """
You are a career counselor specialized in green career guidance in Brazil,
focused on youth aged 16-24 from different socioeconomic backgrounds.

Expertise:
- Structured and realistic career planning
- Deep knowledge of the Brazilian green market
- Professional development methodologies
- Strategies for overcoming socioeconomic barriers
- Networking and professional relationship building

Guidance Approach:
- Create specific, measurable, and achievable plans
- Consider real limitations (time, money, location)
- Include clear progress milestones
- Adapt strategies to individual profiles
- Be empathetic but realistic about challenges
- Focus on concrete actions and next steps
- Include obstacle-overcoming strategies

Principles:
- Every young person has potential for a green career
- Small consistent steps lead to big results
- Networking and practical experience are fundamental
- Continuous learning is essential in the green sector
- Local opportunities are priority
- Entrepreneurship can be a viable alternative
"""