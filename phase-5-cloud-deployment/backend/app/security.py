"""
Security Utilities for Phase V Backend

Provides security-related utilities for authentication and authorization.
"""

import secrets
import hashlib
from typing import Optional
from datetime import datetime, timedelta
import jwt
import logging

logger = logging.getLogger(__name__)


class SecurityUtils:
    """Security utilities for authentication and authorization."""

    # JWT configuration (should be loaded from environment)
    SECRET_KEY = "your-secret-key-change-in-production"
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30

    @staticmethod
    def generate_token(length: int = 32) -> str:
        """
        Generate a secure random token.

        Args:
            length: Length of the token

        Returns:
            Secure random token
        """
        return secrets.token_urlsafe(length)

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password using SHA-256.

        Note: In production, use bcrypt or argon2 instead.

        Args:
            password: Plain text password

        Returns:
            Hashed password
        """
        return hashlib.sha256(password.encode()).hexdigest()

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash.

        Args:
            plain_password: Plain text password
            hashed_password: Hashed password

        Returns:
            True if password matches, False otherwise
        """
        return SecurityUtils.hash_password(plain_password) == hashed_password

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """
        Create a JWT access token.

        Args:
            data: Data to encode in the token
            expires_delta: Optional expiration time delta

        Returns:
            JWT token string
        """
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=SecurityUtils.ACCESS_TOKEN_EXPIRE_MINUTES
            )

        to_encode.update({"exp": expire})

        encoded_jwt = jwt.encode(
            to_encode,
            SecurityUtils.SECRET_KEY,
            algorithm=SecurityUtils.ALGORITHM
        )

        return encoded_jwt

    @staticmethod
    def decode_access_token(token: str) -> Optional[dict]:
        """
        Decode and verify a JWT access token.

        Args:
            token: JWT token string

        Returns:
            Decoded token data or None if invalid
        """
        try:
            payload = jwt.decode(
                token,
                SecurityUtils.SECRET_KEY,
                algorithms=[SecurityUtils.ALGORITHM]
            )
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except jwt.JWTError as e:
            logger.error(f"JWT decode error: {e}")
            return None

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitize a filename to prevent directory traversal attacks.

        Args:
            filename: Original filename

        Returns:
            Sanitized filename
        """
        # Remove path separators
        filename = filename.replace("/", "").replace("\\", "")

        # Remove null bytes
        filename = filename.replace("\x00", "")

        # Remove leading dots
        filename = filename.lstrip(".")

        # Limit length
        if len(filename) > 255:
            filename = filename[:255]

        return filename

    @staticmethod
    def is_safe_redirect_url(url: str, allowed_hosts: list[str]) -> bool:
        """
        Check if a redirect URL is safe.

        Args:
            url: URL to check
            allowed_hosts: List of allowed host names

        Returns:
            True if URL is safe, False otherwise
        """
        from urllib.parse import urlparse

        try:
            parsed = urlparse(url)

            # Check if it's a relative URL (no scheme or netloc)
            if not parsed.scheme and not parsed.netloc:
                return True

            # Check if host is in allowed list
            if parsed.netloc in allowed_hosts:
                return True

            return False
        except Exception as e:
            logger.error(f"Error parsing redirect URL: {e}")
            return False

    @staticmethod
    def generate_api_key() -> str:
        """
        Generate a secure API key.

        Returns:
            API key string
        """
        return f"sk_{secrets.token_urlsafe(32)}"

    @staticmethod
    def mask_sensitive_data(data: str, visible_chars: int = 4) -> str:
        """
        Mask sensitive data for logging.

        Args:
            data: Sensitive data to mask
            visible_chars: Number of characters to keep visible

        Returns:
            Masked string
        """
        if len(data) <= visible_chars:
            return "*" * len(data)

        return data[:visible_chars] + "*" * (len(data) - visible_chars)


class IPWhitelist:
    """IP address whitelist for access control."""

    def __init__(self, allowed_ips: list[str]):
        """
        Initialize IP whitelist.

        Args:
            allowed_ips: List of allowed IP addresses
        """
        self.allowed_ips = set(allowed_ips)

    def is_allowed(self, ip: str) -> bool:
        """
        Check if IP address is allowed.

        Args:
            ip: IP address to check

        Returns:
            True if allowed, False otherwise
        """
        return ip in self.allowed_ips

    def add_ip(self, ip: str) -> None:
        """
        Add IP address to whitelist.

        Args:
            ip: IP address to add
        """
        self.allowed_ips.add(ip)
        logger.info(f"Added IP to whitelist: {ip}")

    def remove_ip(self, ip: str) -> None:
        """
        Remove IP address from whitelist.

        Args:
            ip: IP address to remove
        """
        self.allowed_ips.discard(ip)
        logger.info(f"Removed IP from whitelist: {ip}")
