"""
Configuration Management System

Centralized configuration management with environment support.
"""

import os
import logging
from typing import Any, Optional, Dict
from pathlib import Path
import json

logger = logging.getLogger(__name__)


class ConfigurationError(Exception):
    """Configuration error exception."""
    pass


class Config:
    """Configuration manager."""

    def __init__(self, env: str = "development"):
        """Initialize configuration."""
        self.env = env
        self._config: Dict[str, Any] = {}
        self._load_config()

    def _load_config(self):
        """Load configuration from environment and files."""
        # Load from environment variables
        self._load_from_env()

        # Load from config files
        self._load_from_file()

    def _load_from_env(self):
        """Load configuration from environment variables."""
        # Database
        self._config["database"] = {
            "url": os.getenv("DATABASE_URL", "postgresql://localhost/todo_app"),
            "pool_size": int(os.getenv("DB_POOL_SIZE", "10")),
            "max_overflow": int(os.getenv("DB_MAX_OVERFLOW", "20")),
            "echo": os.getenv("DB_ECHO", "false").lower() == "true"
        }

        # Redis
        self._config["redis"] = {
            "url": os.getenv("REDIS_URL", "redis://localhost:6379"),
            "max_connections": int(os.getenv("REDIS_MAX_CONNECTIONS", "50"))
        }

        # Kafka
        self._config["kafka"] = {
            "bootstrap_servers": os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"),
            "topic_prefix": os.getenv("KAFKA_TOPIC_PREFIX", "todo-app")
        }

        # API
        self._config["api"] = {
            "host": os.getenv("API_HOST", "0.0.0.0"),
            "port": int(os.getenv("API_PORT", "8000")),
            "debug": os.getenv("API_DEBUG", "false").lower() == "true",
            "cors_origins": os.getenv("CORS_ORIGINS", "*").split(",")
        }

        # Security
        self._config["security"] = {
            "secret_key": os.getenv("SECRET_KEY", "change-me-in-production"),
            "jwt_algorithm": os.getenv("JWT_ALGORITHM", "HS256"),
            "jwt_expiry_hours": int(os.getenv("JWT_EXPIRY_HOURS", "24")),
            "password_min_length": int(os.getenv("PASSWORD_MIN_LENGTH", "8"))
        }

        # Email
        self._config["email"] = {
            "smtp_host": os.getenv("SMTP_HOST", "localhost"),
            "smtp_port": int(os.getenv("SMTP_PORT", "587")),
            "smtp_user": os.getenv("SMTP_USER", ""),
            "smtp_password": os.getenv("SMTP_PASSWORD", ""),
            "from_email": os.getenv("FROM_EMAIL", "noreply@todoapp.com")
        }

        # Logging
        self._config["logging"] = {
            "level": os.getenv("LOG_LEVEL", "INFO"),
            "format": os.getenv("LOG_FORMAT", "json"),
            "file": os.getenv("LOG_FILE", "")
        }

        # Features
        self._config["features"] = {
            "enable_webhooks": os.getenv("ENABLE_WEBHOOKS", "true").lower() == "true",
            "enable_notifications": os.getenv("ENABLE_NOTIFICATIONS", "true").lower() == "true",
            "enable_background_jobs": os.getenv("ENABLE_BACKGROUND_JOBS", "true").lower() == "true"
        }

    def _load_from_file(self):
        """Load configuration from file."""
        config_file = Path(f"config/{self.env}.json")

        if config_file.exists():
            try:
                with open(config_file) as f:
                    file_config = json.load(f)
                    self._merge_config(file_config)
                    logger.info(f"Loaded configuration from {config_file}")
            except Exception as e:
                logger.warning(f"Failed to load config file: {e}")

    def _merge_config(self, new_config: Dict[str, Any]):
        """Merge new configuration."""
        for key, value in new_config.items():
            if key in self._config and isinstance(self._config[key], dict) and isinstance(value, dict):
                self._config[key].update(value)
            else:
                self._config[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        keys = key.split(".")
        value = self._config

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default

        return value

    def set(self, key: str, value: Any):
        """Set configuration value."""
        keys = key.split(".")
        config = self._config

        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        config[keys[-1]] = value

    def require(self, key: str) -> Any:
        """Get required configuration value."""
        value = self.get(key)
        if value is None:
            raise ConfigurationError(f"Required configuration missing: {key}")
        return value

    def validate(self):
        """Validate configuration."""
        required = [
            "database.url",
            "security.secret_key"
        ]

        for key in required:
            self.require(key)

        # Validate secret key in production
        if self.env == "production":
            secret_key = self.get("security.secret_key")
            if secret_key == "change-me-in-production":
                raise ConfigurationError("Secret key must be changed in production")

    def to_dict(self) -> Dict[str, Any]:
        """Export configuration as dictionary."""
        return self._config.copy()

    def __repr__(self) -> str:
        """String representation."""
        return f"Config(env={self.env})"


# Global configuration instance
config = Config(env=os.getenv("ENVIRONMENT", "development"))


# Helper functions
def get_config(key: str, default: Any = None) -> Any:
    """Get configuration value."""
    return config.get(key, default)


def require_config(key: str) -> Any:
    """Get required configuration value."""
    return config.require(key)


def is_production() -> bool:
    """Check if running in production."""
    return config.env == "production"


def is_development() -> bool:
    """Check if running in development."""
    return config.env == "development"


def is_testing() -> bool:
    """Check if running in testing."""
    return config.env == "testing"
