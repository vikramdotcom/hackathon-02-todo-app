from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.core.startup import initialize_database
from app.api.routes import auth, todos, users
from app.chat.api import chat_routes
from app.chat.services.conversation_manager import init_conversation_manager, get_conversation_manager
import logging
import os

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    Initializes database on startup with automatic error recovery.
    """
    # Startup: Initialize database with health checks
    logger.info("Starting application...")
    try:
        initialize_database()
        logger.info("Database initialized")

        # Initialize conversation manager for chat feature
        session_timeout = int(os.getenv("CHAT_SESSION_TIMEOUT_MINUTES", "30"))
        conv_manager = init_conversation_manager(session_timeout)
        logger.info(f"Conversation manager initialized (timeout: {session_timeout}min)")

        # Start background cleanup task
        await conv_manager.start_cleanup_task(interval_seconds=300)
        logger.info("Session cleanup task started")

        logger.info("Application startup complete")
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise

    yield

    # Shutdown
    logger.info("Shutting down application...")
    try:
        # Stop cleanup task
        conv_manager = get_conversation_manager()
        await conv_manager.stop_cleanup_task()
        logger.info("Session cleanup task stopped")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix=f"{settings.API_V1_PREFIX}/auth", tags=["auth"])
app.include_router(todos.router, prefix=f"{settings.API_V1_PREFIX}/todos", tags=["todos"])
app.include_router(users.router, prefix=f"{settings.API_V1_PREFIX}/users", tags=["users"])
app.include_router(chat_routes.router, prefix=f"{settings.API_V1_PREFIX}/chat", tags=["chat"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Todo App Phase II API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
