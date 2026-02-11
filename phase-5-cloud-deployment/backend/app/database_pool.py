"""
Database Connection Pooling

Provides connection pool management for PostgreSQL with health checks.
"""

import logging
from typing import Optional, AsyncGenerator
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker
)
from sqlalchemy.pool import NullPool, QueuePool
from sqlalchemy import text

logger = logging.getLogger(__name__)


class DatabasePool:
    """Manage database connection pool."""

    def __init__(
        self,
        database_url: str,
        pool_size: int = 10,
        max_overflow: int = 20,
        pool_timeout: int = 30,
        pool_recycle: int = 3600,
        echo: bool = False
    ):
        """
        Initialize database pool.

        Args:
            database_url: Database connection URL
            pool_size: Number of connections to maintain
            max_overflow: Maximum overflow connections
            pool_timeout: Timeout for getting connection from pool
            pool_recycle: Recycle connections after this many seconds
            echo: Echo SQL statements
        """
        self.database_url = database_url
        self.pool_size = pool_size
        self.max_overflow = max_overflow
        self.pool_timeout = pool_timeout
        self.pool_recycle = pool_recycle
        self.echo = echo

        self._engine: Optional[AsyncEngine] = None
        self._session_factory: Optional[async_sessionmaker] = None

    def create_engine(self) -> AsyncEngine:
        """
        Create database engine with connection pool.

        Returns:
            AsyncEngine instance
        """
        if self._engine is not None:
            return self._engine

        self._engine = create_async_engine(
            self.database_url,
            poolclass=QueuePool,
            pool_size=self.pool_size,
            max_overflow=self.max_overflow,
            pool_timeout=self.pool_timeout,
            pool_recycle=self.pool_recycle,
            pool_pre_ping=True,  # Verify connections before using
            echo=self.echo,
            future=True
        )

        logger.info(
            "Database engine created",
            extra={
                "pool_size": self.pool_size,
                "max_overflow": self.max_overflow
            }
        )

        return self._engine

    def create_session_factory(self) -> async_sessionmaker:
        """
        Create session factory.

        Returns:
            Session factory
        """
        if self._session_factory is not None:
            return self._session_factory

        if self._engine is None:
            self.create_engine()

        self._session_factory = async_sessionmaker(
            self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False
        )

        logger.info("Session factory created")

        return self._session_factory

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Get database session from pool.

        Yields:
            AsyncSession instance
        """
        if self._session_factory is None:
            self.create_session_factory()

        session = self._session_factory()

        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Session error: {e}", exc_info=True)
            raise
        finally:
            await session.close()

    async def check_connection(self) -> bool:
        """
        Check database connection health.

        Returns:
            True if connection is healthy
        """
        try:
            async with self.get_session() as session:
                result = await session.execute(text("SELECT 1"))
                return result.scalar() == 1

        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False

    async def get_pool_status(self) -> dict:
        """
        Get connection pool status.

        Returns:
            Pool status information
        """
        if self._engine is None:
            return {"status": "not_initialized"}

        pool = self._engine.pool

        return {
            "status": "active",
            "size": pool.size(),
            "checked_in": pool.checkedin(),
            "checked_out": pool.checkedout(),
            "overflow": pool.overflow(),
            "total_connections": pool.size() + pool.overflow()
        }

    async def dispose(self):
        """Dispose of the connection pool."""
        if self._engine is not None:
            await self._engine.dispose()
            logger.info("Database engine disposed")
            self._engine = None
            self._session_factory = None


class DatabasePoolManager:
    """Manage multiple database pools."""

    def __init__(self):
        """Initialize pool manager."""
        self.pools: dict[str, DatabasePool] = {}

    def register_pool(self, name: str, pool: DatabasePool):
        """
        Register a database pool.

        Args:
            name: Pool name
            pool: DatabasePool instance
        """
        self.pools[name] = pool
        logger.info(f"Registered database pool: {name}")

    def get_pool(self, name: str = "default") -> Optional[DatabasePool]:
        """
        Get database pool by name.

        Args:
            name: Pool name

        Returns:
            DatabasePool instance or None
        """
        return self.pools.get(name)

    async def check_all_pools(self) -> dict[str, bool]:
        """
        Check health of all pools.

        Returns:
            Dictionary of pool names to health status
        """
        results = {}

        for name, pool in self.pools.items():
            results[name] = await pool.check_connection()

        return results

    async def dispose_all(self):
        """Dispose of all pools."""
        for name, pool in self.pools.items():
            await pool.dispose()
            logger.info(f"Disposed pool: {name}")

        self.pools.clear()


# Global pool manager instance
pool_manager = DatabasePoolManager()


# Dependency for FastAPI
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency for database sessions.

    Yields:
        AsyncSession instance
    """
    pool = pool_manager.get_pool("default")

    if pool is None:
        raise RuntimeError("Database pool not initialized")

    async with pool.get_session() as session:
        yield session
