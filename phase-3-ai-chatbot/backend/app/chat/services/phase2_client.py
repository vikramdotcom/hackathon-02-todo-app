"""Phase II API client for calling existing todo APIs.

This module provides an HTTP client for interacting with Phase II
backend APIs without modifying Phase II code.
"""

import logging
from typing import Any, Dict, List, Optional
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


class Phase2Client:
    """HTTP client for Phase II REST APIs."""

    def __init__(self, base_url: str, timeout: int = 30):
        """Initialize the Phase II API client.
        
        Args:
            base_url: Base URL for Phase II API (e.g., http://localhost:8000/api/v1)
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    def _get_headers(self, jwt_token: str) -> Dict[str, str]:
        """Build request headers with JWT authentication."""
        return {
            "Authorization": f"Bearer {jwt_token}",
            "Content-Type": "application/json"
        }

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def get_todos(
        self,
        jwt_token: str,
        completed: Optional[bool] = None,
        priority: Optional[str] = None,
        tags: Optional[List[str]] = None,
        search: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get todos with optional filters."""
        try:
            params = {}
            if completed is not None:
                params["completed"] = str(completed).lower()
            if priority:
                params["priority"] = priority
            if tags:
                params["tags"] = ",".join(tags)
            if search:
                params["search"] = search

            response = await self.client.get(
                f"{self.base_url}/todos",
                headers=self._get_headers(jwt_token),
                params=params
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error getting todos: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Error getting todos: {str(e)}")
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def create_todo(
        self,
        jwt_token: str,
        title: str,
        description: Optional[str] = None,
        priority: Optional[str] = None,
        due_date: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Create a new todo."""
        try:
            payload = {"title": title}
            if description:
                payload["description"] = description
            if priority:
                payload["priority"] = priority
            if due_date:
                payload["due_date"] = due_date
            if tags:
                payload["tags"] = tags

            response = await self.client.post(
                f"{self.base_url}/todos",
                headers=self._get_headers(jwt_token),
                json=payload
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error creating todo: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Error creating todo: {str(e)}")
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def update_todo(
        self,
        jwt_token: str,
        todo_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
        priority: Optional[str] = None,
        due_date: Optional[str] = None,
        tags: Optional[List[str]] = None,
        completed: Optional[bool] = None
    ) -> Dict[str, Any]:
        """Update an existing todo."""
        try:
            payload = {}
            if title is not None:
                payload["title"] = title
            if description is not None:
                payload["description"] = description
            if priority is not None:
                payload["priority"] = priority
            if due_date is not None:
                payload["due_date"] = due_date
            if tags is not None:
                payload["tags"] = tags
            if completed is not None:
                payload["completed"] = completed

            response = await self.client.put(
                f"{self.base_url}/todos/{todo_id}",
                headers=self._get_headers(jwt_token),
                json=payload
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error updating todo {todo_id}: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Error updating todo {todo_id}: {str(e)}")
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def delete_todo(self, jwt_token: str, todo_id: int) -> Dict[str, Any]:
        """Delete a todo."""
        try:
            response = await self.client.delete(
                f"{self.base_url}/todos/{todo_id}",
                headers=self._get_headers(jwt_token)
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error deleting todo {todo_id}: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Error deleting todo {todo_id}: {str(e)}")
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def complete_todo(self, jwt_token: str, todo_id: int) -> Dict[str, Any]:
        """Mark a todo as complete."""
        try:
            response = await self.client.patch(
                f"{self.base_url}/todos/{todo_id}/complete",
                headers=self._get_headers(jwt_token)
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error completing todo {todo_id}: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Error completing todo {todo_id}: {str(e)}")
            raise

    async def get_user_info(self, jwt_token: str) -> Dict[str, Any]:
        """Get current user information."""
        try:
            response = await self.client.get(
                f"{self.base_url}/users/me",
                headers=self._get_headers(jwt_token)
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error getting user info: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Error getting user info: {str(e)}")
            raise
