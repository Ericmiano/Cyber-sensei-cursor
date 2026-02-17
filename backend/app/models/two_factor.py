"""Two-Factor Authentication models."""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class TwoFactorAuth(Base):
    """Two-factor authentication settings for users."""
    
    __tablename__ = "two_factor_auth"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    secret = Column(String(32), nullable=False)  # TOTP secret
    is_enabled = Column(Boolean, default=False, nullable=False)
    backup_codes = Column(String(500))  # JSON array of backup codes
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_used = Column(DateTime)
    
    # Relationship
    user = relationship("User", back_populates="two_factor")


class TwoFactorBackupCode(Base):
    """Backup codes for 2FA recovery."""
    
    __tablename__ = "two_factor_backup_codes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    code_hash = Column(String(64), nullable=False)  # Hashed backup code
    is_used = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    used_at = Column(DateTime)
    
    # Relationship
    user = relationship("User", back_populates="backup_codes")
