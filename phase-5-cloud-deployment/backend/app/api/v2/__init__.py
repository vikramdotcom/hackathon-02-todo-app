"""
FastAPI v2 API Router

This module provides the main router for API v2 endpoints.
API v2 includes advanced features: recurring tasks, due dates, reminders,
priorities, tags, search, filtering, and audit trail.
"""

from fastapi import APIRouter
from .todos import router as todos_router
from .recurrence import router as recurrence_router

# Create main v2 router
router = APIRouter(prefix="/api/v2", tags=["v2"])

# Include sub-routers
router.include_router(todos_router)
router.include_router(recurrence_router)

@router.get("/health")
async def health_check():
    """Health check endpoint for API v2."""
    return {
        "status": "healthy",
        "version": "2.0",
        "features": [
            "recurring_tasks",
            "due_dates",
            "reminders",
            "priorities",
            "tags",
            "search",
            "filtering",
            "audit_trail"
        ]
    }
