"""
Enhanced Security Features for Cyber Sensei
Implements additional security layers beyond basic authentication
"""
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import hashlib
import secrets
import re
from collections import defaultdict
import time

# Account lockout tracking
failed_login_attempts: Dict[str, List[float]] = defaultdict(list)
locked_accounts: Dict[str, float] = {}

# CSRF token storage (in production, use Redis)
csrf_tokens: Dict[str, float] = {}

# Security constants
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION = 900  # 15 minutes in seconds
CSRF_TOKEN_EXPIRY = 3600  # 1 hour
PASSWORD_MIN_LENGTH = 8
PASSWORD_REQUIRE_UPPERCASE = True
PASSWORD_REQUIRE_LOWERCASE = True
PASSWORD_REQUIRE_DIGIT = True
PASSWORD_REQUIRE_SPECIAL = True


class SecurityEnhancements:
    """Enhanced security features"""
    
    @staticmethod
    def validate_password_strength(password: str) -> tuple[bool, str]:
        """
        Validate password meets security requirements
        
        Returns:
            tuple: (is_valid, error_message)
        """
        if len(password) < PASSWORD_MIN_LENGTH:
            return False, f"Password must be at least {PASSWORD_MIN_LENGTH} characters"
        
        if PASSWORD_REQUIRE_UPPERCASE and not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"
        
        if PASSWORD_REQUIRE_LOWERCASE and not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"
        
        if PASSWORD_REQUIRE_DIGIT and not re.search(r'\d', password):
            return False, "Password must contain at least one digit"
        
        if PASSWORD_REQUIRE_SPECIAL and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "Password must contain at least one special character"
        
        # Check against common passwords
        common_passwords = [
            'password', '12345678', 'qwerty', 'abc123', 'password123',
            'admin', 'letmein', 'welcome', 'monkey', '1234567890'
        ]
        if password.lower() in common_passwords:
            return False, "Password is too common. Please choose a stronger password"
        
        return True, ""
    
    @staticmethod
    def check_account_lockout(email: str) -> bool:
        """
        Check if account is locked due to failed login attempts
        
        Returns:
            bool: True if account is locked
        """
        # Check if account is currently locked
        if email in locked_accounts:
            lock_time = locked_accounts[email]
            if time.time() - lock_time < LOCKOUT_DURATION:
                return True
            else:
                # Lockout expired, remove from locked accounts
                del locked_accounts[email]
                failed_login_attempts[email] = []
                return False
        
        return False
    
    @staticmethod
    def record_failed_login(email: str) -> Optional[int]:
        """
        Record a failed login attempt
        
        Returns:
            Optional[int]: Remaining attempts before lockout, None if locked
        """
        current_time = time.time()
        
        # Clean old attempts (older than lockout duration)
        failed_login_attempts[email] = [
            attempt_time for attempt_time in failed_login_attempts[email]
            if current_time - attempt_time < LOCKOUT_DURATION
        ]
        
        # Add new failed attempt
        failed_login_attempts[email].append(current_time)
        
        # Check if should lock account
        if len(failed_login_attempts[email]) >= MAX_LOGIN_ATTEMPTS:
            locked_accounts[email] = current_time
            return None
        
        return MAX_LOGIN_ATTEMPTS - len(failed_login_attempts[email])
    
    @staticmethod
    def clear_failed_attempts(email: str):
        """Clear failed login attempts after successful login"""
        if email in failed_login_attempts:
            failed_login_attempts[email] = []
        if email in locked_accounts:
            del locked_accounts[email]
    
    @staticmethod
    def generate_csrf_token() -> str:
        """Generate a CSRF token"""
        token = secrets.token_urlsafe(32)
        csrf_tokens[token] = time.time()
        return token
    
    @staticmethod
    def validate_csrf_token(token: str) -> bool:
        """Validate a CSRF token"""
        if token not in csrf_tokens:
            return False
        
        # Check if token is expired
        if time.time() - csrf_tokens[token] > CSRF_TOKEN_EXPIRY:
            del csrf_tokens[token]
            return False
        
        return True
    
    @staticmethod
    def sanitize_input(text: str, max_length: int = 1000) -> str:
        """
        Sanitize user input to prevent injection attacks
        
        Args:
            text: Input text to sanitize
            max_length: Maximum allowed length
            
        Returns:
            str: Sanitized text
        """
        # Truncate to max length
        text = text[:max_length]
        
        # Remove null bytes
        text = text.replace('\x00', '')
        
        # Remove control characters except newlines and tabs
        text = ''.join(char for char in text if char.isprintable() or char in '\n\t')
        
        return text.strip()
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def hash_sensitive_data(data: str) -> str:
        """Hash sensitive data for logging/storage"""
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    @staticmethod
    def detect_sql_injection(text: str) -> bool:
        """
        Detect potential SQL injection attempts
        
        Returns:
            bool: True if suspicious patterns detected
        """
        sql_patterns = [
            r"(\bUNION\b.*\bSELECT\b)",
            r"(\bSELECT\b.*\bFROM\b)",
            r"(\bINSERT\b.*\bINTO\b)",
            r"(\bUPDATE\b.*\bSET\b)",
            r"(\bDELETE\b.*\bFROM\b)",
            r"(\bDROP\b.*\bTABLE\b)",
            r"(--|\#|\/\*|\*\/)",
            r"(\bOR\b.*=.*)",
            r"(\bAND\b.*=.*)",
            r"('.*OR.*'.*=.*')",
        ]
        
        text_upper = text.upper()
        for pattern in sql_patterns:
            if re.search(pattern, text_upper, re.IGNORECASE):
                return True
        
        return False
    
    @staticmethod
    def detect_xss(text: str) -> bool:
        """
        Detect potential XSS attempts
        
        Returns:
            bool: True if suspicious patterns detected
        """
        xss_patterns = [
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"on\w+\s*=",
            r"<iframe",
            r"<object",
            r"<embed",
            r"eval\(",
            r"expression\(",
        ]
        
        for pattern in xss_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        return False
    
    @staticmethod
    def validate_ip_address(ip: str) -> bool:
        """Validate IP address format"""
        pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        if not re.match(pattern, ip):
            return False
        
        # Check each octet is 0-255
        octets = ip.split('.')
        return all(0 <= int(octet) <= 255 for octet in octets)
    
    @staticmethod
    async def check_request_anomalies(request: Request) -> Optional[str]:
        """
        Check for suspicious request patterns
        
        Returns:
            Optional[str]: Warning message if anomaly detected
        """
        warnings = []
        
        # Check for suspicious user agents
        user_agent = request.headers.get("user-agent", "").lower()
        suspicious_agents = ['sqlmap', 'nikto', 'nmap', 'masscan', 'nessus']
        if any(agent in user_agent for agent in suspicious_agents):
            warnings.append("Suspicious user agent detected")
        
        # Check for unusual request sizes
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > 10_000_000:  # 10MB
            warnings.append("Unusually large request")
        
        # Check for path traversal attempts
        path = str(request.url.path)
        if '..' in path or '~' in path:
            warnings.append("Path traversal attempt detected")
        
        return "; ".join(warnings) if warnings else None


class RateLimitMiddleware:
    """Rate limiting middleware to prevent abuse"""
    
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.requests: Dict[str, List[float]] = defaultdict(list)
    
    def check_rate_limit(self, identifier: str) -> bool:
        """
        Check if request should be rate limited
        
        Args:
            identifier: IP address or user ID
            
        Returns:
            bool: True if rate limit exceeded
        """
        current_time = time.time()
        minute_ago = current_time - 60
        
        # Clean old requests
        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier]
            if req_time > minute_ago
        ]
        
        # Check rate limit
        if len(self.requests[identifier]) >= self.requests_per_minute:
            return True
        
        # Add current request
        self.requests[identifier].append(current_time)
        return False


# Initialize security enhancements
security = SecurityEnhancements()
rate_limiter = RateLimitMiddleware()


# Dependency for CSRF protection
async def verify_csrf_token(request: Request):
    """Verify CSRF token in request"""
    token = request.headers.get("X-CSRF-Token")
    if not token or not security.validate_csrf_token(token):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or missing CSRF token"
        )
    return token


# Dependency for rate limiting
async def check_rate_limit(request: Request):
    """Check rate limit for request"""
    # Use IP address as identifier
    client_ip = request.client.host if request.client else "unknown"
    
    if rate_limiter.check_rate_limit(client_ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later."
        )
