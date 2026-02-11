"""
Data Encryption and Security Utilities

Handle encryption, hashing, and security operations.
"""

import logging
import hashlib
import hmac
import secrets
from typing import Optional
import base64
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class PasswordHasher:
    """Secure password hashing."""

    def __init__(self, iterations: int = 100000):
        """Initialize password hasher."""
        self.iterations = iterations
        self.algorithm = "sha256"

    def hash_password(self, password: str, salt: Optional[bytes] = None) -> str:
        """Hash password with salt."""
        if salt is None:
            salt = secrets.token_bytes(32)

        # Use PBKDF2
        key = hashlib.pbkdf2_hmac(
            self.algorithm,
            password.encode('utf-8'),
            salt,
            self.iterations
        )

        # Combine salt and hash
        combined = salt + key
        return base64.b64encode(combined).decode('utf-8')

    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash."""
        try:
            # Decode combined salt+hash
            combined = base64.b64decode(hashed.encode('utf-8'))
            salt = combined[:32]
            stored_key = combined[32:]

            # Hash provided password with same salt
            key = hashlib.pbkdf2_hmac(
                self.algorithm,
                password.encode('utf-8'),
                salt,
                self.iterations
            )

            # Constant-time comparison
            return hmac.compare_digest(key, stored_key)

        except Exception as e:
            logger.error(f"Password verification error: {e}")
            return False


class TokenGenerator:
    """Generate secure tokens."""

    @staticmethod
    def generate_token(length: int = 32) -> str:
        """Generate random token."""
        return secrets.token_urlsafe(length)

    @staticmethod
    def generate_hex_token(length: int = 32) -> str:
        """Generate hex token."""
        return secrets.token_hex(length)

    @staticmethod
    def generate_numeric_code(length: int = 6) -> str:
        """Generate numeric code."""
        return ''.join(secrets.choice('0123456789') for _ in range(length))


class DataEncryptor:
    """Encrypt and decrypt data."""

    def __init__(self, key: Optional[bytes] = None):
        """Initialize encryptor."""
        self.key = key or secrets.token_bytes(32)

    def encrypt(self, data: str) -> str:
        """Encrypt data."""
        # In production, use proper encryption library like cryptography
        # This is a simplified example
        encoded = base64.b64encode(data.encode('utf-8'))
        return encoded.decode('utf-8')

    def decrypt(self, encrypted: str) -> str:
        """Decrypt data."""
        # In production, use proper encryption library
        decoded = base64.b64decode(encrypted.encode('utf-8'))
        return decoded.decode('utf-8')


class SignatureVerifier:
    """Verify HMAC signatures."""

    def __init__(self, secret: str):
        """Initialize signature verifier."""
        self.secret = secret.encode('utf-8')

    def sign(self, data: str) -> str:
        """Create signature for data."""
        signature = hmac.new(
            self.secret,
            data.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature

    def verify(self, data: str, signature: str) -> bool:
        """Verify signature."""
        expected = self.sign(data)
        return hmac.compare_digest(expected, signature)


class SecureTokenManager:
    """Manage secure tokens with expiry."""

    def __init__(self):
        """Initialize token manager."""
        self.tokens: dict[str, tuple[int, datetime]] = {}

    def create_token(self, user_id: int, expires_minutes: int = 60) -> str:
        """Create token for user."""
        token = TokenGenerator.generate_token()
        expires_at = datetime.utcnow() + timedelta(minutes=expires_minutes)
        self.tokens[token] = (user_id, expires_at)

        logger.info(f"Created token for user {user_id}")
        return token

    def verify_token(self, token: str) -> Optional[int]:
        """Verify token and return user ID."""
        if token not in self.tokens:
            return None

        user_id, expires_at = self.tokens[token]

        if datetime.utcnow() > expires_at:
            del self.tokens[token]
            return None

        return user_id

    def revoke_token(self, token: str):
        """Revoke token."""
        if token in self.tokens:
            del self.tokens[token]
            logger.info("Token revoked")

    def cleanup_expired(self):
        """Cleanup expired tokens."""
        now = datetime.utcnow()
        expired = [
            token for token, (_, expires_at) in self.tokens.items()
            if now > expires_at
        ]

        for token in expired:
            del self.tokens[token]

        if expired:
            logger.info(f"Cleaned up {len(expired)} expired tokens")


class APIKeyManager:
    """Manage API keys."""

    def __init__(self):
        """Initialize API key manager."""
        self.keys: dict[str, dict] = {}

    def create_api_key(
        self,
        user_id: int,
        name: str,
        scopes: list[str]
    ) -> str:
        """Create API key."""
        api_key = f"sk_{TokenGenerator.generate_token(32)}"

        self.keys[api_key] = {
            "user_id": user_id,
            "name": name,
            "scopes": scopes,
            "created_at": datetime.utcnow(),
            "last_used": None,
            "usage_count": 0
        }

        logger.info(
            f"Created API key for user {user_id}",
            extra={"user_id": user_id, "name": name}
        )

        return api_key

    def verify_api_key(self, api_key: str) -> Optional[dict]:
        """Verify API key."""
        if api_key not in self.keys:
            return None

        key_data = self.keys[api_key]
        key_data["last_used"] = datetime.utcnow()
        key_data["usage_count"] += 1

        return key_data

    def revoke_api_key(self, api_key: str):
        """Revoke API key."""
        if api_key in self.keys:
            del self.keys[api_key]
            logger.info("API key revoked")

    def list_user_keys(self, user_id: int) -> list[dict]:
        """List API keys for user."""
        return [
            {
                "name": data["name"],
                "scopes": data["scopes"],
                "created_at": data["created_at"].isoformat(),
                "last_used": data["last_used"].isoformat() if data["last_used"] else None,
                "usage_count": data["usage_count"]
            }
            for key, data in self.keys.items()
            if data["user_id"] == user_id
        ]


class DataSanitizer:
    """Sanitize sensitive data."""

    @staticmethod
    def mask_email(email: str) -> str:
        """Mask email address."""
        if '@' not in email:
            return email

        local, domain = email.split('@', 1)
        if len(local) <= 2:
            masked_local = '*' * len(local)
        else:
            masked_local = local[0] + '*' * (len(local) - 2) + local[-1]

        return f"{masked_local}@{domain}"

    @staticmethod
    def mask_phone(phone: str) -> str:
        """Mask phone number."""
        if len(phone) <= 4:
            return '*' * len(phone)
        return '*' * (len(phone) - 4) + phone[-4:]

    @staticmethod
    def mask_credit_card(card: str) -> str:
        """Mask credit card number."""
        digits = ''.join(c for c in card if c.isdigit())
        if len(digits) <= 4:
            return '*' * len(digits)
        return '*' * (len(digits) - 4) + digits[-4:]

    @staticmethod
    def redact_sensitive_fields(data: dict, fields: list[str]) -> dict:
        """Redact sensitive fields from dictionary."""
        result = data.copy()
        for field in fields:
            if field in result:
                result[field] = "[REDACTED]"
        return result


class SecurityHeaders:
    """Security headers for HTTP responses."""

    @staticmethod
    def get_security_headers() -> dict[str, str]:
        """Get recommended security headers."""
        return {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()"
        }


# Global instances
password_hasher = PasswordHasher()
token_generator = TokenGenerator()
token_manager = SecureTokenManager()
api_key_manager = APIKeyManager()
data_sanitizer = DataSanitizer()


# Helper functions
def hash_password(password: str) -> str:
    """Hash password."""
    return password_hasher.hash_password(password)


def verify_password(password: str, hashed: str) -> bool:
    """Verify password."""
    return password_hasher.verify_password(password, hashed)


def generate_token(length: int = 32) -> str:
    """Generate secure token."""
    return token_generator.generate_token(length)


def create_signature(data: str, secret: str) -> str:
    """Create HMAC signature."""
    verifier = SignatureVerifier(secret)
    return verifier.sign(data)


def verify_signature(data: str, signature: str, secret: str) -> bool:
    """Verify HMAC signature."""
    verifier = SignatureVerifier(secret)
    return verifier.verify(data, signature)
