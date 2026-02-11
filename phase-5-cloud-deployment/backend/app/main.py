"""
Phase V Backend Main Application

FastAPI application with:
- API v2 endpoints (recurring tasks, due dates, priorities, tags)
- Dapr integration for event-driven architecture
- Health checks and monitoring
- CORS configuration
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import os

from app.api.v2 import router as v2_router
from app.database import init_db, check_db_connection

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.

    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting Phase V Todo Backend...")

    # Initialize database
    try:
        init_db()
        if check_db_connection():
            logger.info("Database connection established")
        else:
            logger.warning("Database connection check failed")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")

    logger.info("Application startup complete")

    yield

    # Shutdown
    logger.info("Shutting down Phase V Todo Backend...")


# Create FastAPI application
app = FastAPI(
    title="Todo Chatbot API",
    description="Phase V: Cloud-Native Event-Driven Todo System with Advanced Features",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configure CORS
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle uncaught exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_server_error",
            "message": "An unexpected error occurred",
            "details": str(exc) if os.getenv("DEBUG", "false").lower() == "true" else None
        }
    )


# Include API routers
app.include_router(v2_router)


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Todo Chatbot API",
        "version": "2.0.0",
        "phase": "V - Cloud-Native Event-Driven",
        "status": "operational",
        "docs": "/docs",
        "api_v2": "/api/v2"
    }


# Health check endpoint
@app.get("/health")
async def health_check():
    """
    Health check endpoint for Kubernetes probes.

    Returns:
        Health status with component checks
    """
    db_healthy = check_db_connection()

    return {
        "status": "healthy" if db_healthy else "degraded",
        "components": {
            "database": "healthy" if db_healthy else "unhealthy",
            "api": "healthy"
        },
        "version": "2.0.0"
    }


# Readiness probe
@app.get("/ready")
async def readiness_check():
    """
    Readiness check for Kubernetes.

    Returns 200 if ready to accept traffic, 503 otherwise.
    """
    if not check_db_connection():
        return JSONResponse(
            status_code=503,
            content={"status": "not_ready", "reason": "database_unavailable"}
        )

    return {"status": "ready"}


# Liveness probe
@app.get("/live")
async def liveness_check():
    """
    Liveness check for Kubernetes.

    Returns 200 if application is alive.
    """
    return {"status": "alive"}


# Dapr health check (for Dapr sidecar)
@app.get("/dapr/subscribe")
async def dapr_subscribe():
    """
    Dapr pub/sub subscription endpoint.

    Returns list of topics this service subscribes to.
    """
    return [
        {
            "pubsubname": "kafka-pubsub",
            "topic": "task-events",
            "route": "/api/v2/events/task"
        },
        {
            "pubsubname": "kafka-pubsub",
            "topic": "reminders",
            "route": "/api/v2/events/reminder"
        }
    ]


if __name__ == "__main__":
    import uvicorn

    # Run with uvicorn
    uvicorn.run(
        "app.main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
        reload=os.getenv("RELOAD", "false").lower() == "true",
        log_level=os.getenv("LOG_LEVEL", "info").lower()
    )
