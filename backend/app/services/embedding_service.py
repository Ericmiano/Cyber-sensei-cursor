"""Embedding service for generating vector embeddings."""
from typing import List, Optional
from app.core.config import settings
from app.core.logging_config import logger


class EmbeddingService:
    """Service for generating text embeddings with support for free (Ollama) and paid (OpenAI) providers."""
    
    def __init__(self):
        self.model = settings.EMBEDDING_MODEL
        self.dimensions = settings.EMBEDDING_DIMENSIONS
        self.provider = settings.EMBEDDING_PROVIDER if hasattr(settings, 'EMBEDDING_PROVIDER') else "ollama"
        self._openai_client = None
        self._ollama_client = None
    
    def _get_openai_client(self):
        """Get or create OpenAI client for embeddings."""
        if self._openai_client is None:
            try:
                from openai import OpenAI
                if not settings.OPENAI_API_KEY:
                    raise ValueError("OPENAI_API_KEY not set for embeddings")
                self._openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
            except ImportError:
                raise ImportError("openai package not installed")
        return self._openai_client
    
    def _get_ollama_client(self):
        """Get or create Ollama client for free local embeddings."""
        if self._ollama_client is None:
            try:
                import httpx
                self._ollama_client = httpx.AsyncClient(base_url=settings.OLLAMA_BASE_URL, timeout=300.0)
            except ImportError:
                raise ImportError("httpx package not installed")
        return self._ollama_client
    
    async def _generate_ollama_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using Ollama (free, local)."""
        client = self._get_ollama_client()
        # Use nomic-embed-text as default free embedding model
        model = "nomic-embed-text" if self.model == "text-embedding-3-small" else self.model
        
        all_embeddings = []
        for text in texts:
            try:
                response = await client.post(
                    "/api/embeddings",
                    json={"model": model, "prompt": text}
                )
                response.raise_for_status()
                data = response.json()
                embedding = data.get("embedding", [])
                all_embeddings.append(embedding)
            except Exception as e:
                logger.error(f"Ollama embedding failed for text: {e}")
                # Fallback: return zero vector
                all_embeddings.append([0.0] * self.dimensions)
        
        return all_embeddings
    
    async def _generate_openai_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using OpenAI (paid API)."""
        client = self._get_openai_client()
        import asyncio
        loop = asyncio.get_event_loop()
        
        # Batch process (OpenAI supports up to 2048 texts per request)
        batch_size = 100
        all_embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            response = await loop.run_in_executor(
                None,
                lambda: client.embeddings.create(
                    model=self.model,
                    input=batch,
                )
            )
            batch_embeddings = [item.embedding for item in response.data]
            all_embeddings.extend(batch_embeddings)
        
        return all_embeddings
    
    async def generate_embeddings(self, texts: List[str], provider: Optional[str] = None) -> List[List[float]]:
        """
        Generate embeddings for a list of texts.
        
        Args:
            texts: List of text strings to embed
            provider: Optional provider override ("ollama" or "openai")
            
        Returns:
            List of embedding vectors (each is a list of floats)
        """
        provider = provider or self.provider
        
        try:
            if provider == "ollama" or (provider == "auto" and not settings.OPENAI_API_KEY):
                # Use free Ollama embeddings by default
                logger.info(f"Using Ollama (free) for embeddings with model: nomic-embed-text")
                return await self._generate_ollama_embeddings(texts)
            elif provider == "openai" or (provider == "auto" and settings.OPENAI_API_KEY):
                # Use OpenAI embeddings if API key is available
                logger.info(f"Using OpenAI (paid) for embeddings with model: {self.model}")
                return await self._generate_openai_embeddings(texts)
            else:
                raise ValueError(f"Unknown embedding provider: {provider}")
        
        except Exception as e:
            logger.error(f"Embedding generation failed with {provider}: {e}")
            # Fallback to Ollama if OpenAI fails
            if provider == "openai":
                logger.info("Falling back to Ollama (free) embeddings")
                return await self._generate_ollama_embeddings(texts)
            raise


# Singleton instance
embedding_service = EmbeddingService()
