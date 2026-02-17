"""Two-Factor Authentication API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import List
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.two_factor import two_factor_service
from app.models.users import User
from app.models.two_factor import TwoFactorAuth, TwoFactorBackupCode

router = APIRouter(prefix="/2fa", tags=["Two-Factor Authentication"])


class TwoFactorSetupResponse(BaseModel):
    """Response for 2FA setup."""
    secret: str
    qr_code: str
    backup_codes: List[str]


class TwoFactorEnableRequest(BaseModel):
    """Request to enable 2FA."""
    token: str


class TwoFactorVerifyRequest(BaseModel):
    """Request to verify 2FA token."""
    token: str


class TwoFactorStatusResponse(BaseModel):
    """Response for 2FA status."""
    is_enabled: bool
    last_used: str | None


@router.post("/setup", response_model=TwoFactorSetupResponse)
async def setup_two_factor(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Initialize 2FA setup for the current user.
    Returns secret, QR code, and backup codes.
    """
    # Check if 2FA already exists
    result = await db.execute(
        select(TwoFactorAuth).where(TwoFactorAuth.user_id == current_user.id)
    )
    existing_2fa = result.scalar_one_or_none()
    
    if existing_2fa and existing_2fa.is_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA is already enabled. Disable it first to set up again."
        )
    
    # Generate new secret
    secret = two_factor_service.generate_secret()
    
    # Generate QR code
    qr_code = two_factor_service.generate_qr_code(secret, current_user.email)
    
    # Generate backup codes
    backup_codes = two_factor_service.generate_backup_codes()
    
    # Store 2FA settings (not enabled yet)
    if existing_2fa:
        existing_2fa.secret = secret
        existing_2fa.is_enabled = False
    else:
        two_fa = TwoFactorAuth(
            user_id=current_user.id,
            secret=secret,
            is_enabled=False
        )
        db.add(two_fa)
    
    # Delete old backup codes
    await db.execute(
        select(TwoFactorBackupCode).where(TwoFactorBackupCode.user_id == current_user.id)
    )
    
    # Store backup codes (hashed)
    for code in backup_codes:
        code_hash = two_factor_service.hash_backup_code(code)
        backup_code = TwoFactorBackupCode(
            user_id=current_user.id,
            code_hash=code_hash
        )
        db.add(backup_code)
    
    await db.commit()
    
    return TwoFactorSetupResponse(
        secret=secret,
        qr_code=qr_code,
        backup_codes=backup_codes
    )


@router.post("/enable")
async def enable_two_factor(
    request: TwoFactorEnableRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Enable 2FA after verifying the token.
    User must provide a valid token from their authenticator app.
    """
    # Get 2FA settings
    result = await db.execute(
        select(TwoFactorAuth).where(TwoFactorAuth.user_id == current_user.id)
    )
    two_fa = result.scalar_one_or_none()
    
    if not two_fa:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA not set up. Call /setup first."
        )
    
    if two_fa.is_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA is already enabled."
        )
    
    # Verify token
    if not two_factor_service.verify_token(two_fa.secret, request.token):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token. Please try again."
        )
    
    # Enable 2FA
    two_fa.is_enabled = True
    two_fa.last_used = datetime.utcnow()
    await db.commit()
    
    return {"message": "2FA enabled successfully"}


@router.post("/disable")
async def disable_two_factor(
    request: TwoFactorVerifyRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Disable 2FA after verifying the token.
    """
    # Get 2FA settings
    result = await db.execute(
        select(TwoFactorAuth).where(TwoFactorAuth.user_id == current_user.id)
    )
    two_fa = result.scalar_one_or_none()
    
    if not two_fa or not two_fa.is_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA is not enabled."
        )
    
    # Verify token
    if not two_factor_service.verify_token(two_fa.secret, request.token):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token. Please try again."
        )
    
    # Disable 2FA
    two_fa.is_enabled = False
    await db.commit()
    
    return {"message": "2FA disabled successfully"}


@router.post("/verify")
async def verify_two_factor(
    request: TwoFactorVerifyRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Verify a 2FA token (used during login).
    """
    # Get 2FA settings
    result = await db.execute(
        select(TwoFactorAuth).where(TwoFactorAuth.user_id == current_user.id)
    )
    two_fa = result.scalar_one_or_none()
    
    if not two_fa or not two_fa.is_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA is not enabled for this user."
        )
    
    # Try to verify as TOTP token
    if two_factor_service.verify_token(two_fa.secret, request.token):
        two_fa.last_used = datetime.utcnow()
        await db.commit()
        return {"verified": True, "message": "Token verified successfully"}
    
    # Try to verify as backup code
    result = await db.execute(
        select(TwoFactorBackupCode).where(
            TwoFactorBackupCode.user_id == current_user.id,
            TwoFactorBackupCode.is_used == False
        )
    )
    backup_codes = result.scalars().all()
    
    for backup_code in backup_codes:
        if two_factor_service.verify_backup_code(request.token, backup_code.code_hash):
            # Mark backup code as used
            backup_code.is_used = True
            backup_code.used_at = datetime.utcnow()
            two_fa.last_used = datetime.utcnow()
            await db.commit()
            return {"verified": True, "message": "Backup code verified successfully"}
    
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Invalid token or backup code."
    )


@router.get("/status", response_model=TwoFactorStatusResponse)
async def get_two_factor_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get 2FA status for the current user.
    """
    result = await db.execute(
        select(TwoFactorAuth).where(TwoFactorAuth.user_id == current_user.id)
    )
    two_fa = result.scalar_one_or_none()
    
    if not two_fa:
        return TwoFactorStatusResponse(is_enabled=False, last_used=None)
    
    return TwoFactorStatusResponse(
        is_enabled=two_fa.is_enabled,
        last_used=two_fa.last_used.isoformat() if two_fa.last_used else None
    )


@router.get("/backup-codes")
async def get_backup_codes_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get backup codes status (how many unused).
    """
    result = await db.execute(
        select(TwoFactorBackupCode).where(
            TwoFactorBackupCode.user_id == current_user.id,
            TwoFactorBackupCode.is_used == False
        )
    )
    unused_codes = result.scalars().all()
    
    return {
        "unused_count": len(unused_codes),
        "total_count": 10
    }
