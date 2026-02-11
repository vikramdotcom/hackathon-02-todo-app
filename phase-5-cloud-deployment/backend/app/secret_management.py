"""
Secret Management System

Securely manage application secrets and credentials.
"""

import logging
import base64
import json
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import hashlib
import os

logger = logging.getLogger(__name__)


class Secret:
    """Secret entity."""

    def __init__(
        self,
        name: str,
        value: str,
        secret_type: str = "generic",
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Initialize secret."""
        self.name = name
        self.value = value
        self.secret_type = secret_type
        self.metadata = metadata or {}
        self.created_at = datetime.utcnow()
        self.updated_at = self.created_at
        self.version = 1
        self.expires_at: Optional[datetime] = None

    def rotate(self, new_value: str):
        """Rotate secret value."""
        self.value = new_value
        self.updated_at = datetime.utcnow()
        self.version += 1

        logger.info(
            f"Secret rotated: {self.name}",
            extra={"secret": self.name, "version": self.version}
        )

    def is_expired(self) -> bool:
        """Check if secret is expired."""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at

    def to_dict(self, include_value: bool = False) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = {
            "name": self.name,
            "type": self.secret_type,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "version": self.version,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None
        }

        if include_value:
            data["value"] = self.value

        return data


class SecretEncryption:
    """Encrypt and decrypt secrets."""

    def __init__(self, encryption_key: Optional[bytes] = None):
        """Initialize secret encryption."""
        self.encryption_key = encryption_key or self._generate_key()

    def _generate_key(self) -> bytes:
        """Generate encryption key."""
        return os.urandom(32)

    def encrypt(self, plaintext: str) -> str:
        """Encrypt plaintext."""
        # In production, use proper encryption library (cryptography, etc.)
        # This is a simplified example
        encoded = base64.b64encode(plaintext.encode('utf-8'))
        return encoded.decode('utf-8')

    def decrypt(self, ciphertext: str) -> str:
        """Decrypt ciphertext."""
        # In production, use proper encryption library
        decoded = base64.b64decode(ciphertext.encode('utf-8'))
        return decoded.decode('utf-8')


class SecretStore:
    """Store and manage secrets."""

    def __init__(self, encryption: SecretEncryption):
        """Initialize secret store."""
        self.encryption = encryption
        self.secrets: Dict[str, Secret] = {}
        self.secret_history: Dict[str, List[Dict[str, Any]]] = {}

    def create_secret(
        self,
        name: str,
        value: str,
        secret_type: str = "generic",
        metadata: Optional[Dict[str, Any]] = None,
        ttl_days: Optional[int] = None
    ) -> Secret:
        """Create secret."""
        if name in self.secrets:
            raise ValueError(f"Secret already exists: {name}")

        # Encrypt value
        encrypted_value = self.encryption.encrypt(value)

        secret = Secret(name, encrypted_value, secret_type, metadata)

        if ttl_days:
            secret.expires_at = datetime.utcnow() + timedelta(days=ttl_days)

        self.secrets[name] = secret
        self.secret_history[name] = []

        logger.info(
            f"Secret created: {name}",
            extra={"secret": name, "type": secret_type}
        )

        return secret

    def get_secret(self, name: str) -> Optional[str]:
        """Get secret value."""
        if name not in self.secrets:
            return None

        secret = self.secrets[name]

        if secret.is_expired():
            logger.warning(f"Secret expired: {name}")
            return None

        # Decrypt value
        decrypted = self.encryption.decrypt(secret.value)

        logger.debug(f"Secret accessed: {name}")

        return decrypted

    def update_secret(self, name: str, new_value: str):
        """Update secret value."""
        if name not in self.secrets:
            raise ValueError(f"Secret not found: {name}")

        secret = self.secrets[name]

        # Store old version in history
        self.secret_history[name].append({
            "version": secret.version,
            "value": secret.value,
            "updated_at": secret.updated_at.isoformat()
        })

        # Encrypt new value
        encrypted_value = self.encryption.encrypt(new_value)

        # Rotate secret
        secret.rotate(encrypted_value)

        logger.info(f"Secret updated: {name}")

    def delete_secret(self, name: str):
        """Delete secret."""
        if name in self.secrets:
            del self.secrets[name]
            logger.info(f"Secret deleted: {name}")

    def list_secrets(self) -> List[Dict[str, Any]]:
        """List all secrets (without values)."""
        return [s.to_dict(include_value=False) for s in self.secrets.values()]

    def get_secret_metadata(self, name: str) -> Optional[Dict[str, Any]]:
        """Get secret metadata."""
        if name not in self.secrets:
            return None

        return self.secrets[name].to_dict(include_value=False)


class SecretRotationPolicy:
    """Manage secret rotation policies."""

    def __init__(self, secret_store: SecretStore):
        """Initialize secret rotation policy."""
        self.secret_store = secret_store
        self.policies: Dict[str, Dict[str, Any]] = {}

    def set_rotation_policy(
        self,
        secret_name: str,
        rotation_days: int,
        auto_rotate: bool = False
    ):
        """Set rotation policy for secret."""
        self.policies[secret_name] = {
            "rotation_days": rotation_days,
            "auto_rotate": auto_rotate,
            "last_rotation": datetime.utcnow()
        }

        logger.info(
            f"Set rotation policy: {secret_name} ({rotation_days} days)"
        )

    def check_rotation_needed(self, secret_name: str) -> bool:
        """Check if secret needs rotation."""
        if secret_name not in self.policies:
            return False

        policy = self.policies[secret_name]
        days_since_rotation = (
            datetime.utcnow() - policy["last_rotation"]
        ).days

        return days_since_rotation >= policy["rotation_days"]

    def get_secrets_needing_rotation(self) -> List[str]:
        """Get secrets that need rotation."""
        return [
            name for name in self.policies
            if self.check_rotation_needed(name)
        ]


class SecretAccessControl:
    """Control access to secrets."""

    def __init__(self):
        """Initialize secret access control."""
        self.permissions: Dict[str, Dict[str, List[str]]] = {}

    def grant_access(self, user_id: str, secret_name: str, permission: str):
        """Grant access to secret."""
        if user_id not in self.permissions:
            self.permissions[user_id] = {}

        if secret_name not in self.permissions[user_id]:
            self.permissions[user_id][secret_name] = []

        if permission not in self.permissions[user_id][secret_name]:
            self.permissions[user_id][secret_name].append(permission)

        logger.info(
            f"Granted {permission} access to {secret_name} for user {user_id}"
        )

    def revoke_access(self, user_id: str, secret_name: str, permission: str):
        """Revoke access to secret."""
        if (user_id in self.permissions and
            secret_name in self.permissions[user_id]):
            if permission in self.permissions[user_id][secret_name]:
                self.permissions[user_id][secret_name].remove(permission)

        logger.info(
            f"Revoked {permission} access to {secret_name} for user {user_id}"
        )

    def has_permission(
        self,
        user_id: str,
        secret_name: str,
        permission: str
    ) -> bool:
        """Check if user has permission."""
        if user_id not in self.permissions:
            return False

        if secret_name not in self.permissions[user_id]:
            return False

        return permission in self.permissions[user_id][secret_name]


class SecretAuditLog:
    """Audit log for secret access."""

    def __init__(self):
        """Initialize secret audit log."""
        self.logs: List[Dict[str, Any]] = []

    def log_access(
        self,
        user_id: str,
        secret_name: str,
        action: str,
        success: bool
    ):
        """Log secret access."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "secret_name": secret_name,
            "action": action,
            "success": success
        }

        self.logs.append(log_entry)

        if not success:
            logger.warning(
                f"Secret access denied: {user_id} -> {secret_name} ({action})"
            )

    def get_logs(
        self,
        secret_name: Optional[str] = None,
        user_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get audit logs."""
        filtered_logs = self.logs

        if secret_name:
            filtered_logs = [
                log for log in filtered_logs
                if log["secret_name"] == secret_name
            ]

        if user_id:
            filtered_logs = [
                log for log in filtered_logs
                if log["user_id"] == user_id
            ]

        return filtered_logs[-limit:]


class SecretManager:
    """Comprehensive secret management."""

    def __init__(self):
        """Initialize secret manager."""
        self.encryption = SecretEncryption()
        self.store = SecretStore(self.encryption)
        self.rotation_policy = SecretRotationPolicy(self.store)
        self.access_control = SecretAccessControl()
        self.audit_log = SecretAuditLog()

    def create_secret(
        self,
        name: str,
        value: str,
        secret_type: str = "generic",
        ttl_days: Optional[int] = None
    ) -> Secret:
        """Create secret."""
        return self.store.create_secret(name, value, secret_type, ttl_days=ttl_days)

    def get_secret(self, name: str, user_id: str) -> Optional[str]:
        """Get secret with access control."""
        # Check permission
        if not self.access_control.has_permission(user_id, name, "read"):
            self.audit_log.log_access(user_id, name, "read", False)
            logger.warning(f"Access denied: {user_id} -> {name}")
            return None

        # Get secret
        value = self.store.get_secret(name)

        # Log access
        self.audit_log.log_access(user_id, name, "read", value is not None)

        return value

    def update_secret(self, name: str, new_value: str, user_id: str):
        """Update secret with access control."""
        # Check permission
        if not self.access_control.has_permission(user_id, name, "write"):
            self.audit_log.log_access(user_id, name, "write", False)
            raise PermissionError(f"Access denied: {user_id} -> {name}")

        # Update secret
        self.store.update_secret(name, new_value)

        # Log access
        self.audit_log.log_access(user_id, name, "write", True)

    def delete_secret(self, name: str, user_id: str):
        """Delete secret with access control."""
        # Check permission
        if not self.access_control.has_permission(user_id, name, "delete"):
            self.audit_log.log_access(user_id, name, "delete", False)
            raise PermissionError(f"Access denied: {user_id} -> {name}")

        # Delete secret
        self.store.delete_secret(name)

        # Log access
        self.audit_log.log_access(user_id, name, "delete", True)


class EnvironmentSecrets:
    """Manage environment-specific secrets."""

    def __init__(self):
        """Initialize environment secrets."""
        self.environments: Dict[str, SecretStore] = {}

    def get_environment_store(self, environment: str) -> SecretStore:
        """Get secret store for environment."""
        if environment not in self.environments:
            encryption = SecretEncryption()
            self.environments[environment] = SecretStore(encryption)

        return self.environments[environment]

    def create_secret(
        self,
        environment: str,
        name: str,
        value: str
    ):
        """Create secret in environment."""
        store = self.get_environment_store(environment)
        store.create_secret(name, value)

    def get_secret(self, environment: str, name: str) -> Optional[str]:
        """Get secret from environment."""
        store = self.get_environment_store(environment)
        return store.get_secret(name)


class SecretInjector:
    """Inject secrets into application configuration."""

    def __init__(self, secret_manager: SecretManager):
        """Initialize secret injector."""
        self.secret_manager = secret_manager

    def inject_secrets(
        self,
        config: Dict[str, Any],
        user_id: str
    ) -> Dict[str, Any]:
        """Inject secrets into configuration."""
        result = {}

        for key, value in config.items():
            if isinstance(value, str) and value.startswith("secret://"):
                # Extract secret name
                secret_name = value[9:]  # Remove "secret://" prefix

                # Get secret value
                secret_value = self.secret_manager.get_secret(secret_name, user_id)

                if secret_value:
                    result[key] = secret_value
                else:
                    logger.warning(f"Secret not found: {secret_name}")
                    result[key] = None
            elif isinstance(value, dict):
                result[key] = self.inject_secrets(value, user_id)
            else:
                result[key] = value

        return result


# Global instances
secret_manager = SecretManager()
environment_secrets = EnvironmentSecrets()
secret_injector = SecretInjector(secret_manager)


# Helper functions
def create_secret(name: str, value: str, ttl_days: Optional[int] = None) -> Secret:
    """Create secret."""
    return secret_manager.create_secret(name, value, ttl_days=ttl_days)


def get_secret(name: str, user_id: str) -> Optional[str]:
    """Get secret."""
    return secret_manager.get_secret(name, user_id)


def update_secret(name: str, new_value: str, user_id: str):
    """Update secret."""
    secret_manager.update_secret(name, new_value, user_id)


def grant_secret_access(user_id: str, secret_name: str, permission: str):
    """Grant access to secret."""
    secret_manager.access_control.grant_access(user_id, secret_name, permission)


def inject_secrets(config: Dict[str, Any], user_id: str) -> Dict[str, Any]:
    """Inject secrets into configuration."""
    return secret_injector.inject_secrets(config, user_id)
