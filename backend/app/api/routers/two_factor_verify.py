"""Two-Factor Authentication verification endpoint for login."""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.security import decode_token, create_access_token, create_refresh_token
from app.core.two_factor import two_factor_service
from app.models.users import User, Session
from app.models.two_factor import TwoFactorAuth, TwoFactorBackupCode
from uuid import UUID
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["authentication"])


class TwoFactorLoginRequest(BaseModel):
    """Request to complete login with 2FA."""
    temp_token: str
    token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


@router.post("/login/2fa", response_model=TokenResponse)
async def verify_2fa_login(
    request_data: TwoFactorLoginRequest,
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Complete login with 2FA verification.
    User provides the temporary token from initial login and their 2FA code.
    """
    # Decode temporary token
    payload = decode_token(request_data.temp_token)
    if not payload or payload.get("type") != "2fa_pending":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired temporary token",
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid temporary token",
        )
    
    # Get user
    user = await db.get(User, UUID(user_id))
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )
    
    # Get 2FA settings
    result = await db.execute(
        select(TwoFactorAuth).where(TwoFactorAuth.user_id == user.id)
    )
    two_fa = result.scalar_one_or_none()
    
    if not two_fa or not two_fa.is_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA is not enabled for this user.",
        )
    
    # Try to verify as TOTP token
    token_valid = False
    if two_factor_service.verify_token(two_fa.secret, request_data.token):
        token_valid = True
        two_fa.last_used = datetime.utcnow()
    else:
        # Try to verify as backup code
        result = await db.execute(
            select(TwoFactorBackupCode).where(
                TwoFactorBackupCode.user_id == user.id,
                TwoFactorBackupCode.is_used == False
            )
        )
        backup_codes = result.scalars().all()
        
        for backup_code in backup_codes:
            if two_factor_service.verify_backup_code(request_data.token, backup_code.code_hash):
                # Mark backup code as used
                backup_code.is_used = True
                backup_code.used_at = datetime.utcnow()
                two_fa.last_used = datetime.utcnow()
                token_valid = True
                break
    
    if not token_valid:
        logger.warning(f"Failed 2FA verification for user: {user.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid 2FA token or backup code.",
        )
    
    # Create tokens with JTI for revocation
    from app.core.config import settings
    access_token, jti = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    # Create session
    try:
        # Get IP and user agent
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent", "")[:512]
        
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
        
        logger.info(f"User logged in with 2FA: {user.email} (ID: {user.id})")
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
        )
    except Exception as e:
        logger.error(f"Session creation error after 2FA: {e}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create session. Please try again.",
        )
