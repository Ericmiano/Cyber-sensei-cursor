"""Authentication endpoints."""
import re
from datetime import timedelta, datetime
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, EmailStr, field_validator, ConfigDict
from app.core.database import get_db
from app.api.dependencies import get_current_user
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
from uuid import uuid4, UUID
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
    user: dict


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
    
    # Create user
    try:
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
        
        # Commit the transaction
        await db.commit()
        
        await db.refresh(user)
        logger.info(f"User registered: {user.email} (ID: {user.id})")
        
        # Create tokens for auto-login after registration
        access_token, jti = create_access_token(data={"sub": str(user.id)})
        refresh_token = create_refresh_token(data={"sub": str(user.id)})
        
        # Create session
        session = Session(
            user_id=user.id,
            refresh_token=refresh_token,
            access_token_jti=jti,
            expires_at=datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        )
        db.add(session)
        await db.commit()
        
        return {
            "message": "User created successfully",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": {
                "id": str(user.id),
                "email": user.email,
                "username": user.username,
                "name": user.username,
                "avatar": "",
                "createdAt": user.created_at.isoformat() if user.created_at else ""
            }
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


class TwoFactorRequired(BaseModel):
    requires_2fa: bool = True
    user_id: str
    message: str = "2FA verification required"


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
    
    # Check if 2FA is enabled for this user
    from app.models.two_factor import TwoFactorAuth
    stmt_2fa = select(TwoFactorAuth).where(
        TwoFactorAuth.user_id == user.id,
        TwoFactorAuth.is_enabled == True
    )
    result_2fa = await db.execute(stmt_2fa)
    two_fa = result_2fa.scalar_one_or_none()
    
    # If 2FA is enabled, return a special response indicating 2FA is required
    if two_fa:
        # Create a temporary token for 2FA verification (valid for 5 minutes)
        temp_token, _ = create_access_token(
            data={"sub": str(user.id), "type": "2fa_pending"},
            expires_delta=timedelta(minutes=5)
        )
        return JSONResponse(
            status_code=status.HTTP_202_ACCEPTED,
            content={
                "requires_2fa": True,
                "temp_token": temp_token,
                "message": "2FA verification required"
            }
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
            user={
                "id": str(user.id),
                "email": user.email,
                "username": user.username,
                "name": user.username,
                "avatar": "",
                "createdAt": user.created_at.isoformat() if user.created_at else ""
            }
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



@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_token: str,
    request: Request = None,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Refresh access token using refresh token."""
    # Decode refresh token
    from app.core.security import decode_token
    
    payload = decode_token(refresh_token, token_type="refresh")
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )
    
    # Verify refresh token exists in database
    stmt = select(Session).where(
        Session.refresh_token == refresh_token,
        Session.expires_at > datetime.utcnow(),
    )
    result = await db.execute(stmt)
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expired or revoked",
        )
    
    # Get user
    user = await db.get(User, UUID(user_id))
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )
    
    # Create new access token
    access_token, jti = create_access_token(data={"sub": str(user.id)})
    
    # Update session
    session.access_token_jti = jti
    session.last_used_at = datetime.utcnow()
    await db.commit()
    
    logger.info(f"Token refreshed for user {user.email}")
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user={
            "id": str(user.id),
            "email": user.email,
            "username": user.username,
            "name": user.username,
            "avatar": "",
            "createdAt": user.created_at.isoformat() if user.created_at else ""
        }
    )


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Logout user by revoking all sessions."""
    # Delete all user sessions
    stmt = select(Session).where(Session.user_id == current_user.id)
    result = await db.execute(stmt)
    sessions = result.scalars().all()
    
    for session in sessions:
        await db.delete(session)
    
    await db.commit()
    
    logger.info(f"User logged out: {current_user.email}")
    
    return {"message": "Logged out successfully"}


@router.get("/me")
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
):
    """Get current user information."""
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "username": current_user.username,
        "name": current_user.username,
        "avatar": "",
        "createdAt": current_user.created_at.isoformat() if current_user.created_at else ""
    }


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordReset(BaseModel):
    token: str
    new_password: str
    
    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        return validate_password_strength(v)


@router.post("/password-reset-request")
async def request_password_reset(
    data: PasswordResetRequest,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(rate_limit_dependency(requests_per_minute=3)),
):
    """Request password reset (sends email with token)."""
    # Find user
    stmt = select(User).where(User.email == data.email.lower())
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    # Always return success to prevent email enumeration
    if not user:
        logger.warning(f"Password reset requested for non-existent email: {data.email}")
        return {"message": "If the email exists, a reset link has been sent"}
    
    # Generate reset token (valid for 1 hour)
    from app.core.security import create_access_token
    reset_token, _ = create_access_token(
        data={"sub": str(user.id), "type": "password_reset"},
        expires_delta=timedelta(hours=1),
    )
    
    # TODO: Send email with reset token
    # For now, just log it (in production, use email service)
    logger.info(f"Password reset token for {user.email}: {reset_token}")
    
    # In production, you would:
    # await email_service.send_password_reset(user.email, reset_token)
    
    return {"message": "If the email exists, a reset link has been sent"}


@router.post("/password-reset")
async def reset_password(
    data: PasswordReset,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(rate_limit_dependency(requests_per_minute=3)),
):
    """Reset password using token."""
    from app.core.security import decode_token
    
    # Decode token
    payload = decode_token(data.token)
    if not payload or payload.get("type") != "password_reset":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid reset token",
        )
    
    # Get user
    user = await db.get(User, UUID(user_id))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not found",
        )
    
    # Update password
    user.hashed_password = get_password_hash(data.new_password)
    user.updated_at = datetime.utcnow()
    
    # Revoke all sessions
    stmt = select(Session).where(Session.user_id == user.id)
    result = await db.execute(stmt)
    sessions = result.scalars().all()
    for session in sessions:
        await db.delete(session)
    
    await db.commit()
    
    logger.info(f"Password reset for user {user.email}")
    
    return {"message": "Password reset successfully"}



