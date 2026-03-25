"""FastAPI application entry point."""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
import time
import logging
from app.core.config import settings
from app.core.logging_config import setup_logging, logger
from app.api.routers import auth, curriculum, quiz, recommendations, labs, meta_learning, topics, documents, chat
from app.core.error_handlers import (
    AppException,
    DatabaseError,
    ValidationError as AppValidationError,
    NotFoundError,
    UnauthorizedError,
)

# Initialize logging
setup_logging()
logger.info("Starting Cyber Sensei API")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Intelligent adaptive learning platform with AI-generated personalized content",
    docs_url="/docs" if settings.DEBUG else None,  # Hide docs in production
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url="/openapi.json" if settings.DEBUG else None,
)

# Security: Add trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1"] if settings.ENVIRONMENT == "development" else ["yourdomain.com"],
)

# Performance: Add compression middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# CORS middleware with environment-based configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

# Security: Add security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Add security headers to all responses."""
    response = await call_next(request)
    
    # Security headers
    response.headers["X-Content-Type-Options"] = "nosniff"  # Prevent MIME sniffing
    response.headers["X-Frame-Options"] = "DENY"  # Prevent clickjacking
    response.headers["X-XSS-Protection"] = "1; mode=block"  # XSS protection
    
    if settings.ENVIRONMENT == "production":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"  # HTTPS only
    
    return response
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests with timing information."""
    start_time = time.time()
    
    # Log request
    logger.info(
        f"Request: {request.method} {request.url.path}",
        extra={
            "method": request.method,
            "path": request.url.path,
            "client": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent", "")[:100],
        }
    )
    
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Log response
        logger.info(
            f"Response: {request.method} {request.url.path} - {response.status_code} "
            f"({process_time:.3f}s)",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "process_time": process_time,
            }
        )
        
        # Add timing header
        response.headers["X-Process-Time"] = str(process_time)
        return response
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(
            f"Request error: {request.method} {request.url.path} - {str(e)} "
            f"({process_time:.3f}s)",
            exc_info=True,
            extra={
                "method": request.method,
                "path": request.url.path,
                "process_time": process_time,
            }
        )
        raise


# Global exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with proper serialization."""
    # Convert errors to JSON-serializable format
    errors = []
    for error in exc.errors():
        serializable_error = {
            "type": error.get("type"),
            "loc": list(error.get("loc", [])),
            "msg": error.get("msg"),
            "input": str(error.get("input", ""))[:500],  # Limit input length
        }
        # Handle ctx field if present
        if "ctx" in error:
            ctx = error["ctx"]
            serializable_error["ctx"] = {
                k: str(v) if not isinstance(v, (str, int, float, bool, type(None))) else v
                for k, v in ctx.items()
            }
        errors.append(serializable_error)
    
    logger.warning(
        f"Validation error: {request.method} {request.url.path}",
        extra={"errors": errors, "path": request.url.path}
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": errors},
    )

@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    """Handle application-specific exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.exception_handler(SQLAlchemyError)
async def database_exception_handler(request: Request, exc: SQLAlchemyError):
    """Handle database errors with proper logging."""
    logger.error(
        f"Database error: {request.method} {request.url.path} - {str(exc)}",
        exc_info=True,
        extra={
            "method": request.method,
            "path": request.url.path,
            "error_type": type(exc).__name__,
        }
    )
    
    if settings.ENVIRONMENT == "production":
        detail = "Database error occurred. Please try again later."
    else:
        detail = f"Database error: {str(exc)}"
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": detail},
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"} if not settings.DEBUG else {"detail": str(exc)},
    )

# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(curriculum.router, prefix="/api")
app.include_router(quiz.router, prefix="/api")
app.include_router(recommendations.router, prefix="/api")
app.include_router(labs.router, prefix="/api")
app.include_router(meta_learning.router, prefix="/api")
app.include_router(topics.router, prefix="/api")
app.include_router(documents.router, prefix="/api")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Cyber Sensei API",
        "version": settings.APP_VERSION,
    }


@app.get("/health")
async def health():
    """Basic health check endpoint."""
    return {"status": "healthy", "version": settings.APP_VERSION}

@app.get("/health/ready")
async def health_ready():
    """Readiness check - verifies dependencies."""
    from app.core.database import engine
    import redis
    from app.core.config import settings
    
    checks = {
        "database": False,
        "redis": False,
    }
    
    # Check database
    try:
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
        checks["database"] = True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
    
    # Check Redis
    try:
        r = redis.from_url(settings.REDIS_URL)
        r.ping()
        checks["redis"] = True
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
    
    all_healthy = all(checks.values())
    status_code = status.HTTP_200_OK if all_healthy else status.HTTP_503_SERVICE_UNAVAILABLE
    
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "ready" if all_healthy else "degraded",
            "checks": checks,
        }
    )

@app.get("/health/live")
async def health_live():
    """Liveness check - verifies application is running."""
    return {"status": "alive"}
