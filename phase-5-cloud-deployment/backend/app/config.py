"""
Configuration Management Utilities

Provides utilities for managing application configuration.
"""

import os
from typing import Optional, Any
from pydantic import BaseSettings, Field, validator
import logging

logger = logging.getLogger(__name__)


class DatabaseSettings(BaseSettings):
    """Database configuration settings."""

    url: str = Field(
        default="postgresql://user:password@localhost:5432/todo_db",
        env="DATABASE_URL"
    )
    pool_size: int = Field(default=5, env="DB_POOL_SIZE")
    max_overflow: int = Field(default=10, env="DB_MAX_OVERFLOW")
    echo: bool = Field(default=False, env="SQL_ECHO")

    class Config:
        env_file = ".env"
        case_sensitive = False


class RedisSettings(BaseSettings):
    """Redis configuration settings."""

    host: str = Field(default="localhost", env="REDIS_HOST")
    port: int = Field(default=6379, env="REDIS_PORT")
    password: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    db: int = Field(default=0, env="REDIS_DB")
    ssl: bool = Field(default=False, env="REDIS_SSL")

    class Config:
        env_file = ".env"
        case_sensitive = False


class KafkaSettings(BaseSettings):
    """Kafka/Redpanda configuration settings."""

    bootstrap_servers: str = Field(
        default="localhost:9092",
        env="KAFKA_BOOTSTRAP_SERVERS"
    )
    sasl_username: Optional[str] = Field(default=None, env="KAFKA_SASL_USERNAME")
    sasl_password: Optional[str] = Field(default=None, env="KAFKA_SASL_PASSWORD")
    sasl_mechanism: str = Field(default="SCRAM-SHA-256", env="KAFKA_SASL_MECHANISM")
    security_protocol: str = Field(default="SASL_SSL", env="KAFKA_SECURITY_PROTOCOL")

    # Topics
    topic_task_events: str = Field(default="task-events", env="KAFKA_TOPIC_TASK_EVENTS")
    topic_reminders: str = Field(default="reminders", env="KAFKA_TOPIC_REMINDERS")
    topic_task_updates: str = Field(default="task-updates", env="KAFKA_TOPIC_TASK_UPDATES")

    # Consumer group
    consumer_group: str = Field(default="todo-backend-group", env="KAFKA_CONSUMER_GROUP")

    class Config:
        env_file = ".env"
        case_sensitive = False


class DaprSettings(BaseSettings):
    """Dapr configuration settings."""

    http_port: int = Field(default=3500, env="DAPR_HTTP_PORT")
    grpc_port: int = Field(default=50001, env="DAPR_GRPC_PORT")
    app_id: str = Field(default="todo-backend", env="DAPR_APP_ID")
    app_port: int = Field(default=8000, env="DAPR_APP_PORT")

    class Config:
        env_file = ".env"
        case_sensitive = False


class SecuritySettings(BaseSettings):
    """Security configuration settings."""

    secret_key: str = Field(
        default="your-secret-key-change-in-production",
        env="JWT_SECRET_KEY"
    )
    algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(
        default=30,
        env="JWT_ACCESS_TOKEN_EXPIRE_MINUTES"
    )
    refresh_token_expire_days: int = Field(
        default=7,
        env="JWT_REFRESH_TOKEN_EXPIRE_DAYS"
    )

    class Config:
        env_file = ".env"
        case_sensitive = False


class CORSSettings(BaseSettings):
    """CORS configuration settings."""

    origins: str = Field(
        default="http://localhost:3000,http://localhost:8080",
        env="CORS_ORIGINS"
    )
    allow_credentials: bool = Field(default=True, env="CORS_ALLOW_CREDENTIALS")
    allow_methods: str = Field(default="*", env="CORS_ALLOW_METHODS")
    allow_headers: str = Field(default="*", env="CORS_ALLOW_HEADERS")

    @validator("origins")
    def parse_origins(cls, v):
        """Parse comma-separated origins into list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    class Config:
        env_file = ".env"
        case_sensitive = False


class AppSettings(BaseSettings):
    """Application configuration settings."""

    name: str = Field(default="todo-chatbot-backend", env="APP_NAME")
    version: str = Field(default="2.0.0", env="APP_VERSION")
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=True, env="DEBUG")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")

    # Server settings
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    reload: bool = Field(default=True, env="RELOAD")

    # Feature flags
    enable_recurring_tasks: bool = Field(default=True, env="ENABLE_RECURRING_TASKS")
    enable_reminders: bool = Field(default=True, env="ENABLE_REMINDERS")
    enable_audit_trail: bool = Field(default=True, env="ENABLE_AUDIT_TRAIL")
    enable_websocket: bool = Field(default=True, env="ENABLE_WEBSOCKET")

    # Monitoring
    enable_metrics: bool = Field(default=True, env="ENABLE_METRICS")
    metrics_port: int = Field(default=9090, env="METRICS_PORT")

    class Config:
        env_file = ".env"
        case_sensitive = False


class Settings:
    """Main settings class that aggregates all configuration."""

    def __init__(self):
        """Initialize all settings."""
        self.app = AppSettings()
        self.database = DatabaseSettings()
        self.redis = RedisSettings()
        self.kafka = KafkaSettings()
        self.dapr = DaprSettings()
        self.security = SecuritySettings()
        self.cors = CORSSettings()

    def log_config(self):
        """Log current configuration (excluding sensitive data)."""
        logger.info("Application Configuration:")
        logger.info(f"  Environment: {self.app.environment}")
        logger.info(f"  Debug: {self.app.debug}")
        logger.info(f"  Host: {self.app.host}:{self.app.port}")
        logger.info(f"  Database: {self._mask_url(self.database.url)}")
        logger.info(f"  Kafka: {self.kafka.bootstrap_servers}")
        logger.info(f"  Dapr: {self.dapr.app_id} (HTTP:{self.dapr.http_port})")

    @staticmethod
    def _mask_url(url: str) -> str:
        """Mask sensitive parts of URL."""
        import re
        # Mask password in database URL
        return re.sub(r'://([^:]+):([^@]+)@', r'://\1:****@', url)


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """
    Get application settings.

    Returns:
        Settings instance
    """
    return settings


def reload_settings():
    """Reload settings from environment."""
    global settings
    settings = Settings()
    logger.info("Settings reloaded")
