"""
Safety agent responsible for content moderation and safety checks.
Ensures all interactions are appropriate and safe for young users.
"""
from typing import Dict, Any, List
import re
from .base_agent import BaseAgent
from app.models import Persona, AssistantRequest, LanguageCode
from app.services.mistral_provider import mistral_provider


class SafetyAgent(BaseAgent):
    """
    Safety agent that monitors and moderates content for inappropriate material,
    ensuring safe interactions for Brazilian youth aged 16-24.
    """
    
    def __init__(self):
        super().__init__(
            name="safety_agent",
            description="Content moderation and safety validation for youth interactions"
        )
        
        # Define safety keywords and patterns
        self.unsafe_patterns = {
            "violence": [
                r'\b(violência|agressão|briga|pancada|machuc|matar|morrer|suicid)\b',
                r'\b(violence|aggression|fight|hurt|kill|die|suicide)\b'
            ],
            "inappropriate_content": [
                r'\b(sexo|sexual|pornografia|nude|despir)\b',
                r'\b(sex|sexual|pornography|nude|naked)\b'
            ],
            "illegal_activities": [
                r'\b(drogas|maconha|cocaína|tráfico|roubo|furto)\b',
                r'\b(drugs|marijuana|cocaine|trafficking|theft|steal)\b'
            ],
            "financial_scams": [
                r'\b(esquema|pirâmide|dinheiro fácil|ganhar muito|sem esforço)\b',
                r'\b(scheme|pyramid|easy money|get rich|no effort)\b'
            ],
            "personal_info": [
                r'\b(cpf|rg|endereço|telefone|senha|cartão)\b',
                r'\b(ssn|address|phone|password|credit card)\b'
            ]
        }
        
        # Positive safety indicators
        self.positive_indicators = [
            "sustentabilidade", "meio ambiente", "carreira", "educação", 
            "curso", "trabalho", "profissional", "desenvolvimento",
            "sustainability", "environment", "career", "education",
            "course", "work", "professional", "development"
        ]
    
    async def process(self, request: AssistantRequest, persona: Persona, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process safety validation for user request and potential response"""
        
        self.logger.info(f"🛡️ Running safety check for persona {persona.id}")
        
        # Quick pattern-based safety check
        quick_check = self._quick_safety_check(request.message)
        
        if quick_check["is_safe"]:
            # If quick check passes, run comprehensive AI-based safety analysis
            safety_result = await self._comprehensive_safety_check(request, persona, context)
        else:
            # If quick check fails, return immediate unsafe result
            safety_result = {
                "is_safe": False,
                "safety_score": 0.2,
                "risk_categories": quick_check["risk_categories"],
                "safety_message": self._get_safety_message(quick_check["risk_categories"], request.language),
                "action_required": "block_request"
            }
        
        return {
            "agent": self.name,
            "safety_result": safety_result,
            "checked_content": {
                "user_message": request.message,
                "message_length": len(request.message),
                "language_detected": request.language
            },
            "processing_time_ms": 150,
            "model_used": "safety_rules_ai" if quick_check["is_safe"] else "safety_rules",
            "check_timestamp": context.get("timestamp") if context else None
        }
    
    def _quick_safety_check(self, message: str) -> Dict[str, Any]:
        """Perform quick pattern-based safety check"""
        
        message_lower = message.lower()
        risk_categories = []
        
        # Check against unsafe patterns
        for category, patterns in self.unsafe_patterns.items():
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    risk_categories.append(category)
                    break
        
        # Check for positive indicators
        positive_score = sum(1 for indicator in self.positive_indicators 
                           if indicator in message_lower)
        
        # Calculate basic safety score
        risk_score = len(risk_categories)
        total_score = max(0, positive_score - risk_score * 2)
        is_safe = risk_score == 0 and total_score >= 0
        
        return {
            "is_safe": is_safe,
            "risk_categories": risk_categories,
            "positive_score": positive_score,
            "total_score": total_score
        }
    
    async def _comprehensive_safety_check(self, request: AssistantRequest, persona: Persona, context: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive AI-based safety analysis"""
        
        safety_prompt = self._build_safety_prompt(request, persona)
        system_prompt = self.get_system_prompt(request.language)
        
        try:
            response = await mistral_provider.generate_text(
                prompt=safety_prompt,
                system_prompt=system_prompt,
                temperature=0.1,  # Low temperature for consistent safety decisions
                max_tokens=300
            )
            
            # Parse AI safety response
            safety_analysis = self._parse_safety_response(response["text"])
            
            return safety_analysis
            
        except Exception as e:
            self.logger.error(f"❌ Comprehensive safety check failed: {e}")
            # Conservative fallback - if AI check fails, allow with warning
            return {
                "is_safe": True,
                "safety_score": 0.7,
                "risk_categories": [],
                "safety_message": "Análise de segurança simplificada aplicada",
                "action_required": "proceed_with_caution",
                "fallback_used": True
            }
    
    def _build_safety_prompt(self, request: AssistantRequest, persona: Persona) -> str:
        """Build prompt for AI safety analysis"""
        
        return f"""
Analise a segurança do seguinte pedido de um jovem brasileiro de {persona.age} anos:

PERFIL DO USUÁRIO:
- Idade: {persona.age} anos
- Localização: {persona.location_city}, {persona.location_state}
- Contexto: Buscando orientação sobre carreiras verdes

MENSAGEM PARA ANÁLISE:
"{request.message}"

Avalie os seguintes aspectos de segurança:

1. **Conteúdo Apropriado**: A mensagem é adequada para jovens?
2. **Riscos Identificados**: Há menções a atividades perigosas/ilegais?
3. **Informações Pessoais**: Há exposição de dados sensíveis?
4. **Intenção Maliciosa**: A mensagem parece ter intenções inadequadas?
5. **Contexto Educacional**: A mensagem está relacionada ao desenvolvimento profissional?

Responda no formato:
SEGURANÇA: [SEGURO/MODERADO/INSEGURO]
PONTUAÇÃO: [0.0-1.0]
RISCOS: [lista de categorias de risco, ou "nenhum"]
RECOMENDAÇÃO: [PERMITIR/REVISAR/BLOQUEAR]
JUSTIFICATIVA: [breve explicação da decisão]
"""
    
    def _parse_safety_response(self, response_text: str) -> Dict[str, Any]:
        """Parse AI safety response into structured format"""
        
        try:
            lines = response_text.strip().split('\n')
            result = {
                "is_safe": True,
                "safety_score": 0.8,
                "risk_categories": [],
                "action_required": "proceed",
                "ai_justification": response_text
            }
            
            for line in lines:
                line = line.strip()
                
                if line.startswith("SEGURANÇA:"):
                    safety_level = line.split(":", 1)[1].strip().upper()
                    result["is_safe"] = safety_level == "SEGURO"
                    
                elif line.startswith("PONTUAÇÃO:"):
                    try:
                        score = float(line.split(":", 1)[1].strip())
                        result["safety_score"] = max(0.0, min(1.0, score))
                    except ValueError:
                        pass
                        
                elif line.startswith("RISCOS:"):
                    risks_text = line.split(":", 1)[1].strip().lower()
                    if risks_text != "nenhum" and risks_text != "none":
                        result["risk_categories"] = [r.strip() for r in risks_text.split(",")]
                        
                elif line.startswith("RECOMENDAÇÃO:"):
                    recommendation = line.split(":", 1)[1].strip().upper()
                    if recommendation == "BLOQUEAR":
                        result["action_required"] = "block_request"
                        result["is_safe"] = False
                    elif recommendation == "REVISAR":
                        result["action_required"] = "proceed_with_caution"
                    else:
                        result["action_required"] = "proceed"
            
            # Generate appropriate safety message
            if not result["is_safe"]:
                result["safety_message"] = self._get_safety_message(
                    result["risk_categories"], 
                    LanguageCode.PT_BR
                )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error parsing safety response: {e}")
            # Conservative fallback
            return {
                "is_safe": True,
                "safety_score": 0.7,
                "risk_categories": [],
                "action_required": "proceed_with_caution",
                "safety_message": "Análise de segurança parcial realizada",
                "parse_error": str(e)
            }
    
    def _get_safety_message(self, risk_categories: List[str], language: LanguageCode) -> str:
        """Generate appropriate safety message based on detected risks"""
        
        if language == LanguageCode.PT_BR:
            if "violence" in risk_categories:
                return "Esta conversa contém conteúdo relacionado à violência. Vamos focar em oportunidades positivas de carreira verde!"
            
            elif "inappropriate_content" in risk_categories:
                return "Vamos manter nossa conversa focada em desenvolvimento profissional e carreiras sustentáveis."
            
            elif "illegal_activities" in risk_categories:
                return "Não posso ajudar com atividades ilegais. Que tal explorarmos oportunidades legais e positivas no setor verde?"
            
            elif "financial_scams" in risk_categories:
                return "Cuidado com esquemas que prometem dinheiro fácil. Vou te ajudar com caminhos reais para construir uma carreira sustentável."
            
            elif "personal_info" in risk_categories:
                return "Por segurança, evite compartilhar informações pessoais. Posso te ajudar sem esses dados!"
            
            else:
                return "Vamos manter nossa conversa focada em seu desenvolvimento profissional na área verde!"
        
        else:
            if "violence" in risk_categories:
                return "This conversation contains violence-related content. Let's focus on positive green career opportunities!"
            
            elif "inappropriate_content" in risk_categories:
                return "Let's keep our conversation focused on professional development and sustainable careers."
            
            elif "illegal_activities" in risk_categories:
                return "I can't help with illegal activities. How about we explore legal and positive opportunities in the green sector?"
            
            elif "financial_scams" in risk_categories:
                return "Be careful with schemes that promise easy money. I'll help you with real paths to build a sustainable career."
            
            elif "personal_info" in risk_categories:
                return "For safety reasons, avoid sharing personal information. I can help you without that data!"
            
            else:
                return "Let's keep our conversation focused on your professional development in the green area!"
    
    def validate_response_safety(self, response_text: str, persona: Persona) -> Dict[str, Any]:
        """Validate safety of generated response before sending to user"""
        
        self.logger.info(f"🔍 Validating response safety for persona {persona.id}")
        
        # Quick check for obviously unsafe content in response
        quick_check = self._quick_safety_check(response_text)
        
        # Additional checks for response-specific issues
        response_risks = []
        
        # Check for inappropriate promises or guarantees
        if re.search(r'\b(garanto|prometo|certeza|100%|sem risco)\b', response_text.lower()):
            response_risks.append("unrealistic_promises")
        
        # Check for financial advice without disclaimers
        if re.search(r'\b(investir|investimento|ações|bitcoin)\b', response_text.lower()):
            if "disclaimer" not in response_text.lower() and "risco" not in response_text.lower():
                response_risks.append("financial_advice_without_disclaimer")
        
        # Calculate overall safety
        is_safe = quick_check["is_safe"] and len(response_risks) == 0
        safety_score = max(0.1, quick_check["total_score"] / 5 - len(response_risks) * 0.2)
        
        return {
            "is_response_safe": is_safe,
            "response_safety_score": safety_score,
            "response_risks": quick_check["risk_categories"] + response_risks,
            "recommendations": self._get_response_safety_recommendations(response_risks),
            "validated_at": "response_validation"
        }
    
    def _get_response_safety_recommendations(self, risks: List[str]) -> List[str]:
        """Get recommendations for improving response safety"""
        
        recommendations = []
        
        if "unrealistic_promises" in risks:
            recommendations.append("Evitar garantias absolutas - usar linguagem como 'pode ajudar' ou 'potencialmente'")
        
        if "financial_advice_without_disclaimer" in risks:
            recommendations.append("Adicionar disclaimer sobre riscos financeiros e necessidade de consultoria especializada")
        
        if not recommendations:
            recommendations.append("Resposta considerada segura para o público jovem")
        
        return recommendations
    
    def get_system_prompt(self, language: LanguageCode) -> str:
        """Get safety agent system prompt"""
        if language == LanguageCode.PT_BR:
            return """
Você é um moderador de segurança especializado em proteger jovens brasileiros de 16-24 anos
em conversas sobre desenvolvimento de carreira e sustentabilidade.

Responsabilidades:
- Identificar conteúdo inadequado ou perigoso
- Proteger jovens de informações prejudiciais
- Garantir que as conversas sejam educativas e construtivas
- Detectar tentativas de manipulação ou exploração
- Validar adequação do conteúdo para a faixa etária

Critérios de Segurança:
- Conteúdo violento ou agressivo = INSEGURO
- Material sexual ou inapropriado = INSEGURO  
- Atividades ilegais ou perigosas = INSEGURO
- Esquemas financeiros duvidosos = INSEGURO
- Solicitação de informações pessoais = MODERADO
- Conteúdo educativo sobre carreiras = SEGURO
- Orientação profissional construtiva = SEGURO

Abordagem:
- Seja conservador na análise de segurança
- Priorize sempre a proteção dos jovens
- Considere o contexto brasileiro e cultural
- Foque no desenvolvimento positivo
- Em caso de dúvida, seja cauteloso
"""
        else:
            return """
You are a safety moderator specialized in protecting Brazilian youth aged 16-24
in conversations about career development and sustainability.

Responsibilities:
- Identify inappropriate or dangerous content
- Protect youth from harmful information
- Ensure conversations are educational and constructive
- Detect manipulation or exploitation attempts
- Validate content appropriateness for age group

Safety Criteria:
- Violent or aggressive content = UNSAFE
- Sexual or inappropriate material = UNSAFE
- Illegal or dangerous activities = UNSAFE
- Questionable financial schemes = UNSAFE
- Personal information requests = MODERATE
- Educational career content = SAFE
- Constructive professional guidance = SAFE

Approach:
- Be conservative in safety analysis
- Always prioritize youth protection
- Consider Brazilian cultural context
- Focus on positive development
- When in doubt, be cautious
"""