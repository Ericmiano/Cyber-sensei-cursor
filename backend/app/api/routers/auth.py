"""Authentication endpoints."""
import re
from datetime import timedelta, datetime
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, EmailStr, field_validator, ConfigDict
from app.core.database import get_db
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
)
from app.core.validators import validate_password_strength, validate_email
from app.core.rate_limiter import rate_limit_dependency
from app.core.config import settings
from app.models.users import User, Session, UserProfile
from uuid import uuid4
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["authentication"])


class UserRegister(BaseModel):
    email: EmailStr
    username: str
    password: str
    
    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Validate and normalize email."""
        return validate_email(v)
    
    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength."""
        return validate_password_strength(v)
    
    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Validate username format and length."""
        if len(v) < 3:
            raise ValueError("Username must be at least 3 characters")
        if len(v) > 50:
            raise ValueError("Username must be less than 50 characters")
        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError("Username can only contain letters, numbers, underscores, and hyphens")
        # Sanitize username
        return v.strip().lower()
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "username": "johndoe",
                "password": "SecurePass123!",
            }
        }
    )


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    request: Request,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(rate_limit_dependency(requests_per_minute=settings.RATE_LIMIT_AUTH_PER_MINUTE)),
):
    """Register a new user with proper transaction management."""
    # Check if user exists (optimistic check before transaction)
    stmt = select(User).where(User.email == user_data.email)
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    stmt = select(User).where(User.username == user_data.username)
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken",
        )
    
    # Create user with transaction
    try:
        async with db.begin():
            user = User(
                email=user_data.email.lower().strip(),
                username=user_data.username,
                hashed_password=get_password_hash(user_data.password),
                is_active=True,
            )
            db.add(user)
            await db.flush()  # Get user.id without committing
            
            # Create user profile in same transaction
            profile = UserProfile(user_id=user.id)
            db.add(profile)
            # Transaction will commit automatically on exit
        
        await db.refresh(user)
        logger.info(f"User registered: {user.email} (ID: {user.id})")
        
        return {
            "message": "User created successfully",
            "user_id": str(user.id),
            "email": user.email,
        }
    except Exception as e:
        logger.error(f"Registration error: {e}", exc_info=True)
        await db.rollback()
        
        # Check for unique constraint violations
        error_str = str(e).lower()
        if "unique" in error_str or "duplicate" in error_str:
            if "email" in error_str:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered",
                )
            elif "username" in error_str:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken",
                )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email or username already exists",
            )
        
        # Don't expose internal errors in production
        if settings.ENVIRONMENT == "production":
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user. Please try again later.",
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user: {str(e)}",
        )


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(rate_limit_dependency(requests_per_minute=settings.RATE_LIMIT_AUTH_PER_MINUTE)),
):
    """Login and get access token with proper security."""
    # Find user by email (OAuth2PasswordRequestForm uses 'username' field for email)
    email = form_data.username.lower().strip()
    stmt = select(User).where(User.email == email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    # Always perform password check to prevent timing attacks
    password_valid = False
    if user:
        password_valid = verify_password(form_data.password, user.hashed_password)
    
    if not user or not password_valid:
        logger.warning(f"Failed login attempt for email: {email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        logger.warning(f"Login attempt for inactive user: {user.email}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )
    
    # Create tokens with JTI for revocation
    access_token, jti = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    # Create session with transaction
    try:
        # Get IP and user agent
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent", "")[:512]  # Limit length
        
        async with db.begin():
            session = Session(
                user_id=user.id,
                refresh_token=refresh_token,
                access_token_jti=jti,
                expires_at=datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
                ip_address=ip_address,
                user_agent=user_agent,
            )
            db.add(session)
            # Transaction commits automatically
        
        logger.info(f"User logged in: {user.email} (ID: {user.id})")
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
        )
    except Exception as e:
        logger.error(f"Session creation error: {e}", exc_info=True)
        await db.rollback()
        
        if settings.ENVIRONMENT == "production":
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create session. Please try again.",
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create session: {str(e)}",
        )
