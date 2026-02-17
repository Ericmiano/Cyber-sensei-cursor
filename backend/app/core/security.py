"""Security utilities for authentication and authorization."""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt
from app.core.config import settings

# Bcrypt constants
BCRYPT_ROUNDS = 12
BCRYPT_MAX_BYTES = 72  # Bcrypt has a 72-byte limit


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash.
    
    Note: Bcrypt has a 72-byte limit, so we truncate the password before verification.
    """
    try:
        # Truncate to match the truncation done in get_password_hash
        plain_password_truncated = plain_password.encode('utf-8')[:BCRYPT_MAX_BYTES]
        # hashed_password should be bytes
        if isinstance(hashed_password, str):
            hashed_password = hashed_password.encode('utf-8')
        return bcrypt.checkpw(plain_password_truncated, hashed_password)
    except Exception:
        return False


def get_password_hash(password: str) -> str:
    """Hash a password.
    
    Note: Bcrypt has a 72-byte limit, so we truncate longer passwords.
    This is done transparently to the user.
    """
    # Bcrypt has a 72-byte limit. Truncate if necessary.
    password_bytes = password.encode('utf-8')[:BCRYPT_MAX_BYTES]
    # Generate salt and hash
    salt = bcrypt.gensalt(rounds=BCRYPT_ROUNDS)
    hashed = bcrypt.hashpw(password_bytes, salt)
    # Return as string
    return hashed.decode('utf-8')


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None, jti: Optional[str] = None) -> tuple[str, str]:
    """Create a JWT access token."""
    import uuid
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Add JWT ID (jti) for revocation
    if not jti:
        jti = str(uuid.uuid4())
    
    to_encode.update({
        "exp": expire,
        "type": "access",
        "jti": jti,  # JWT ID for revocation
    })
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt, jti


def create_refresh_token(data: dict) -> str:
    """Create a JWT refresh token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_token(token: str, token_type: Optional[str] = None) -> Optional[dict]:
    """
    Decode and verify a JWT token.
    
    Args:
        token: JWT token string
        token_type: Expected token type ("access" or "refresh")
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        # Verify token type if specified
        if token_type and payload.get("type") != token_type:
            return None
        
        return payload
    except JWTError:
        return None
