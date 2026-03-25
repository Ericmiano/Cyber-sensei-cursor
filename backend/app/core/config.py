"""Application configuration using Pydantic Settings."""
from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import Optional


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Application
    APP_NAME: str = "Cyber Sensei"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    @classmethod
    def parse_env_var(cls, field_name: str, raw_val: str) -> any:
        """Custom parser for environment variables."""
        if field_name == "DEBUG":
            # Handle DEBUG being set to non-boolean values (e.g., "WARN" from system env)
            if isinstance(raw_val, str):
                return raw_val.lower() in ("true", "1", "yes", "on")
        return raw_val
    
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/cyber_sensei"
    DATABASE_ECHO: bool = False
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 40
    DATABASE_POOL_RECYCLE: int = 3600
    DATABASE_POOL_PRE_PING: bool = True
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    
    # JWT
    SECRET_KEY: str  # Required, not Optional
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_AUTH_PER_MINUTE: int = 5
    
    # CORS - Multi-platform support
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "capacitor://localhost",
        "http://localhost",
        "https://localhost",
    ]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list[str] = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]
    CORS_ALLOW_HEADERS: list[str] = ["*"]
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"  # json or text
    
    # Environment
    ENVIRONMENT: str = "development"  # development, staging, production
    
    # AI/LLM
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    DEFAULT_LLM_PROVIDER: str = "ollama"  # ollama, openai, anthropic
    EMBEDDING_PROVIDER: str = "ollama"  # ollama (free), openai (paid), auto (auto-detect)
    EMBEDDING_MODEL: str = "nomic-embed-text"  # Free Ollama model (default) or "text-embedding-3-small" for OpenAI
    EMBEDDING_DIMENSIONS: int = 768  # nomic-embed-text uses 768, OpenAI uses 1536
    
    # Vector DB
    VECTOR_DB_TYPE: str = "chroma"  # chroma or qdrant
    CHROMA_PERSIST_DIR: str = "./chroma_db"
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_COLLECTION: str = "cyber_sensei"
    
    # Learning Algorithms
    BKT_INITIAL_MASTERY: float = 0.3
    BKT_LEARN_RATE: float = 0.1
    BKT_GUESS_RATE: float = 0.2
    BKT_SLIP_RATE: float = 0.1
    SM2_INITIAL_EASINESS: float = 2.5
    SM2_MIN_EASINESS: float = 1.3
    
    # Bloom's Taxonomy Weights (levels 1-6)
    BLOOM_WEIGHTS: list[float] = [0.1, 0.15, 0.2, 0.2, 0.2, 0.15]
    
    # Reliability Scoring
    DOMAIN_AUTHORITY_WEIGHT: float = 0.4
    AGE_BONUS_WEIGHT: float = 0.3
    PEER_REVIEW_WEIGHT: float = 0.3
    
    # Safety & Moderation
    ENABLE_CONTENT_MODERATION: bool = True
    AUTO_FLAG_THRESHOLD: float = 0.7
    
    # Lab Orchestrator (Docker removed - labs disabled for local execution)
    LAB_TIMEOUT_SECONDS: int = 3600
    MAX_CONCURRENT_LABS: int = 10
    LAB_ENABLED: bool = False  # Labs disabled without Docker
    
    @field_validator('DEBUG', mode='before')
    @classmethod
    def parse_debug(cls, v):
        """Parse DEBUG from environment, handling non-boolean values."""
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes", "on")
        return bool(v) if v is not None else False
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    def model_post_init(self, __context):
        """Validate settings after initialization."""
        # Validate SECRET_KEY
        if not self.SECRET_KEY or len(self.SECRET_KEY) < 32:
            if self.ENVIRONMENT == "production":
                raise ValueError(
                    "SECRET_KEY must be set and at least 32 characters in production environment"
                )
            else:
                import secrets
                import warnings
                generated_key = secrets.token_urlsafe(32)
                warnings.warn(
                    f"SECRET_KEY not set or too short. Using generated key for development: {generated_key}",
                    UserWarning
                )
                object.__setattr__(self, 'SECRET_KEY', generated_key)


settings = Settings()
