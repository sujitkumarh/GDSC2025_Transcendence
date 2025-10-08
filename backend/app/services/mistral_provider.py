"""
AWS Mistral AI provider service for Transcendence.
Handles text generation and embeddings with fallback mock mode.
"""
import json
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from loguru import logger
from cachetools import TTLCache
import hashlib

from app.core.config import settings


class MistralProvider:
    """AWS Mistral AI service provider with caching and mock support"""
    
    def __init__(self):
        self.mock_mode = settings.MOCK_MODE
        self.client = None
        self.cache = TTLCache(maxsize=settings.CACHE_MAX_SIZE, ttl=settings.CACHE_TTL)
        self._initialize_client()
        
    def _initialize_client(self):
        """Initialize AWS Bedrock client if not in mock mode"""
        if self.mock_mode:
            logger.info("🎭 Mistral provider running in MOCK mode")
            return
            
        try:
            credentials = settings.get_aws_credentials()
            if credentials.get("mock_mode"):
                logger.warning("🔐 AWS credentials not configured, using mock mode")
                self.mock_mode = True
                return
                
            self.client = boto3.client(
                'bedrock-runtime',
                region_name=credentials["region_name"],
                aws_access_key_id=credentials["aws_access_key_id"],
                aws_secret_access_key=credentials["aws_secret_access_key"],
                aws_session_token=credentials.get("aws_session_token")
            )
            logger.info("✅ AWS Mistral client initialized")
            
        except (ClientError, NoCredentialsError) as e:
            logger.error(f"❌ Failed to initialize AWS client: {e}")
            logger.warning("🎭 Falling back to mock mode")
            self.mock_mode = True
            
    def _generate_cache_key(self, prompt: str, system_prompt: str, **kwargs) -> str:
        """Generate cache key for prompt"""
        content = f"{prompt}:{system_prompt}:{json.dumps(kwargs, sort_keys=True)}"
        return hashlib.md5(content.encode()).hexdigest()
    
    async def generate_text(
        self, 
        prompt: str, 
        system_prompt: str = "", 
        temperature: float = None, 
        max_tokens: int = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate text using AWS Mistral AI or mock response
        
        Args:
            prompt: User prompt
            system_prompt: System instruction
            temperature: Response randomness (0-1)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional model parameters
            
        Returns:
            Dict containing generated text and metadata
        """
        # Use defaults from settings
        temperature = temperature or settings.DEFAULT_TEMPERATURE
        max_tokens = max_tokens or settings.MAX_TOKENS
        
        # Check cache first
        cache_key = self._generate_cache_key(prompt, system_prompt, temperature=temperature, max_tokens=max_tokens)
        if cache_key in self.cache:
            logger.debug("📦 Returning cached response")
            return self.cache[cache_key]
        
        if self.mock_mode:
            response = await self._generate_mock_response(prompt, system_prompt, temperature, max_tokens)
        else:
            response = await self._generate_real_response(prompt, system_prompt, temperature, max_tokens, **kwargs)
        
        # Cache the response
        self.cache[cache_key] = response
        return response
    
    async def _generate_real_response(
        self, 
        prompt: str, 
        system_prompt: str, 
        temperature: float, 
        max_tokens: int,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate response using real AWS Mistral API"""
        try:
            # Prepare the request body
            body = {
                "prompt": f"<s>[INST] {system_prompt}\n\n{prompt} [/INST]",
                "max_tokens": max_tokens,
                "temperature": temperature,
                "top_p": kwargs.get("top_p", 0.9),
                "top_k": kwargs.get("top_k", 50)
            }
            
            start_time = datetime.utcnow()
            
            # Make the API call
            response = self.client.invoke_model(
                modelId=settings.AWS_MISTRAL_MODEL,
                body=json.dumps(body),
                contentType="application/json",
                accept="application/json"
            )
            
            end_time = datetime.utcnow()
            duration_ms = int((end_time - start_time).total_seconds() * 1000)
            
            # Parse response
            response_body = json.loads(response['body'].read())
            generated_text = response_body.get('outputs', [{}])[0].get('text', '')
            
            logger.info(f"✅ Generated {len(generated_text)} characters in {duration_ms}ms")
            
            return {
                "text": generated_text,
                "prompt_tokens": len(prompt.split()),
                "completion_tokens": len(generated_text.split()),
                "total_tokens": len(prompt.split()) + len(generated_text.split()),
                "duration_ms": duration_ms,
                "model": settings.AWS_MISTRAL_MODEL,
                "temperature": temperature,
                "mock_mode": False,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ AWS Mistral API error: {e}")
            # Fallback to mock response
            logger.warning("🎭 Falling back to mock response")
            return await self._generate_mock_response(prompt, system_prompt, temperature, max_tokens)
    
    async def _generate_mock_response(
        self, 
        prompt: str, 
        system_prompt: str, 
        temperature: float, 
        max_tokens: int
    ) -> Dict[str, Any]:
        """Generate mock response for development/testing"""
        
        # Simulate API delay
        await asyncio.sleep(0.1 + (temperature * 0.3))
        
        # Generate contextual mock response based on prompt content
        mock_responses = {
            "career": "Com base no seu perfil, recomendo explorar oportunidades em energia solar, que está crescendo rapidamente no Brasil. Considere começar com um curso técnico em instalação de painéis solares e depois buscar certificações específicas. O setor oferece boas perspectivas de emprego, especialmente no Nordeste brasileiro.",
            "learning": "Existem várias opções de treinamento disponíveis para você. Recomendo começar com cursos online gratuitos sobre sustentabilidade e depois partir para certificações mais específicas. O SENAI oferece cursos técnicos em energia renovável que são muito valorizados pelo mercado.",
            "pathway": "Aqui está um plano de carreira personalizado para você: 1) Complete um curso básico de sustentabilidade (1-2 meses), 2) Faça um estágio ou trabalho voluntário na área (3-6 meses), 3) Busque uma certificação técnica específica (6-12 meses), 4) Aplique para vagas júnior em empresas do setor. Essa progressão está alinhada com seu perfil e orçamento.",
            "awareness": "O Brasil oferece muitas oportunidades em empregos verdes! Setores como energia renovável, gestão de resíduos e agricultura sustentável estão em expansão. Mesmo sem experiência prévia, existem programas de capacitação que podem te preparar para essas carreiras promissoras."
        }
        
        # Determine response type based on prompt keywords
        prompt_lower = prompt.lower()
        if any(word in prompt_lower for word in ["carreira", "emprego", "trabalho", "career", "job"]):
            response_text = mock_responses["career"]
        elif any(word in prompt_lower for word in ["curso", "treinamento", "aprender", "learning", "training"]):
            response_text = mock_responses["learning"]
        elif any(word in prompt_lower for word in ["caminho", "plano", "próximos passos", "pathway", "plan"]):
            response_text = mock_responses["pathway"]
        else:
            response_text = mock_responses["awareness"]
        
        # Add some variability based on temperature
        if temperature > 0.7:
            response_text += " Lembre-se de que cada jornada é única, e você pode adaptar essas sugestões às suas necessidades específicas."
        
        logger.info(f"🎭 Generated mock response ({len(response_text)} characters)")
        
        return {
            "text": response_text,
            "prompt_tokens": len(prompt.split()),
            "completion_tokens": len(response_text.split()),
            "total_tokens": len(prompt.split()) + len(response_text.split()),
            "duration_ms": 100,  # Mock duration
            "model": "mock-mistral-7b",
            "temperature": temperature,
            "mock_mode": True,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for texts (mock implementation for now)
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        if self.mock_mode:
            # Generate mock embeddings (random but consistent)
            embeddings = []
            for text in texts:
                # Use hash for consistent mock embeddings
                text_hash = hash(text)
                embedding = [(text_hash % 1000 + i) / 1000.0 for i in range(384)]  # 384-dim vector
                embeddings.append(embedding)
            
            logger.info(f"🎭 Generated {len(embeddings)} mock embeddings")
            return embeddings
        else:
            # TODO: Implement real embeddings when available in AWS Bedrock
            logger.warning("📝 Real embeddings not implemented yet, using mock")
            return await self.generate_embeddings(texts)  # Fallback to mock
    
    async def health_check(self) -> Dict[str, Any]:
        """Check the health of the Mistral service"""
        if self.mock_mode:
            return {
                "status": "healthy",
                "mode": "mock",
                "cache_size": len(self.cache),
                "cache_capacity": self.cache.maxsize
            }
        
        try:
            # Simple test call
            test_response = await self.generate_text(
                prompt="Test health check",
                system_prompt="Respond with 'OK' if you are working correctly.",
                max_tokens=10
            )
            
            return {
                "status": "healthy",
                "mode": "real",
                "model": settings.AWS_MISTRAL_MODEL,
                "cache_size": len(self.cache),
                "cache_capacity": self.cache.maxsize,
                "test_response_length": len(test_response.get("text", ""))
            }
            
        except Exception as e:
            logger.error(f"❌ Health check failed: {e}")
            return {
                "status": "unhealthy",
                "mode": "real",
                "error": str(e),
                "cache_size": len(self.cache)
            }


# Global provider instance
mistral_provider = MistralProvider()