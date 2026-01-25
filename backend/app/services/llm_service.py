"""LLM service for routing between different providers."""
from typing import Optional, Dict, Any
from app.core.config import settings
from app.core.logging_config import logger


class LLMService:
    """Service for routing LLM requests to different providers."""
    
    def __init__(self):
        self.provider = settings.DEFAULT_LLM_PROVIDER
        self._clients = {}
    
    def _get_openai_client(self):
        """Get or create OpenAI client."""
        if "openai" not in self._clients:
            try:
                from openai import OpenAI
                if not settings.OPENAI_API_KEY:
                    raise ValueError("OPENAI_API_KEY not set")
                self._clients["openai"] = OpenAI(api_key=settings.OPENAI_API_KEY)
            except ImportError:
                raise ImportError("openai package not installed")
        return self._clients["openai"]
    
    def _get_anthropic_client(self):
        """Get or create Anthropic client."""
        if "anthropic" not in self._clients:
            try:
                from anthropic import Anthropic
                if not settings.ANTHROPIC_API_KEY:
                    raise ValueError("ANTHROPIC_API_KEY not set")
                self._clients["anthropic"] = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
            except ImportError:
                raise ImportError("anthropic package not installed")
        return self._clients["anthropic"]
    
    def _get_ollama_client(self):
        """Get or create Ollama client."""
        if "ollama" not in self._clients:
            try:
                from langchain_community.llms import Ollama
                self._clients["ollama"] = Ollama(base_url=settings.OLLAMA_BASE_URL)
            except ImportError:
                raise ImportError("langchain-community package not installed")
        return self._clients["ollama"]
    
    async def generate_text(
        self,
        prompt: str,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Generate text using the specified LLM provider.
        
        Args:
            prompt: Input prompt
            provider: LLM provider (openai, anthropic, ollama)
            model: Model name (optional, uses default)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
        """
        provider = provider or self.provider
        
        try:
            if provider == "openai":
                client = self._get_openai_client()
                model = model or "gpt-4-turbo-preview"
                response = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                return response.choices[0].message.content
            
            elif provider == "anthropic":
                client = self._get_anthropic_client()
                model = model or "claude-3-opus-20240229"
                response = client.messages.create(
                    model=model,
                    max_tokens=max_tokens or 1024,
                    temperature=temperature,
                    messages=[{"role": "user", "content": prompt}],
                )
                return response.content[0].text
            
            elif provider == "ollama":
                llm = self._get_ollama_client()
                model = model or "llama2"
                # Ollama is synchronous, run in thread
                import asyncio
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    None,
                    lambda: llm.invoke(prompt)
                )
                return result
            
            else:
                raise ValueError(f"Unknown provider: {provider}")
        
        except Exception as e:
            logger.error(f"LLM generation failed with {provider}: {e}")
            # Fallback to another provider if available
            if provider != "ollama":
                logger.info("Falling back to Ollama")
                return await self.generate_text(prompt, provider="ollama", model=model)
            raise


# Singleton instance
llm_service = LLMService()
