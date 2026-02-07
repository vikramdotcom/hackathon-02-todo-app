"""Function executor for LLM function calls.

This module provides the FunctionExecutor class for executing LLM function calls
by calling Phase II APIs, parsing natural language dates, and formatting results.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import dateparser

from app.chat.services.phase2_client import Phase2Client

logger = logging.getLogger(__name__)


class FunctionExecutor:
    """Executes LLM function calls by calling Phase II APIs.

    This class provides methods for:
    - Executing function calls from the LLM
    - Parsing natural language dates
    - Validating function arguments
    - Formatting results for the LLM
    """

    def __init__(self, phase2_client: Phase2Client):
        """Initialize the function executor.

        Args:
            phase2_client: Phase II API client instance
        """
        self.phase2_client = phase2_client
        logger.info("FunctionExecutor initialized")

    def _parse_date(self, date_string: str) -> Optional[str]:
        """Parse natural language date to ISO format.

        Args:
            date_string: Natural language date (e.g., "tomorrow", "next Monday")

        Returns:
            ISO formatted date string, or None if parsing fails
        """
        try:
            parsed_date = dateparser.parse(
                date_string,
                settings={
                    'PREFER_DATES_FROM': 'future',
                    'RETURN_AS_TIMEZONE_AWARE': False
                }
            )

            if parsed_date:
                return parsed_date.isoformat()

            logger.warning(f"Failed to parse date: {date_string}")
            return None

        except Exception as e:
            logger.error(f"Error parsing date '{date_string}': {e}")
            return None

    def _parse_date_range(self, filter_string: str) -> tuple[Optional[str], Optional[str]]:
        """Parse date range filter to start and end dates.

        Args:
            filter_string: Date range filter (e.g., "today", "this week", "overdue")

        Returns:
            Tuple of (start_date, end_date) in ISO format, or (None, None) if parsing fails
        """
        now = datetime.now()
        start_date = None
        end_date = None

        try:
            if filter_string.lower() == "today":
                start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
                end_date = now.replace(hour=23, minute=59, second=59, microsecond=999999)

            elif filter_string.lower() == "tomorrow":
                tomorrow = now + timedelta(days=1)
                start_date = tomorrow.replace(hour=0, minute=0, second=0, microsecond=0)
                end_date = tomorrow.replace(hour=23, minute=59, second=59, microsecond=999999)

            elif filter_string.lower() in ["this week", "week"]:
                # Start of week (Monday)
                start_date = now - timedelta(days=now.weekday())
                start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
                # End of week (Sunday)
                end_date = start_date + timedelta(days=6)
                end_date = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)

            elif filter_string.lower() == "overdue":
                # Overdue means due date is in the past
                end_date = now

            if start_date:
                start_date = start_date.isoformat()
            if end_date:
                end_date = end_date.isoformat()

            return start_date, end_date

        except Exception as e:
            logger.error(f"Error parsing date range '{filter_string}': {e}")
            return None, None

    def _resolve_todo_reference(self, reference: str, context: Optional[Dict] = None) -> Optional[int]:
        """Resolve todo reference to todo ID.
        
        Args:
            reference: Reference like 'first', 'second', 'last', 'that one'
            context: Conversation context with last_query_results
            
        Returns:
            Todo ID if resolved, None otherwise
        """
        if not context or not context.get('last_query_results'):
            return None
            
        last_results = context.get('last_query_results', [])
        if not last_results:
            return None
            
        ref_lower = reference.lower().strip()
        
        # Handle positional references
        if ref_lower in ['first', 'first one', 'the first', 'the first one']:
            return last_results[0] if len(last_results) > 0 else None
        elif ref_lower in ['second', 'second one', 'the second', 'the second one']:
            return last_results[1] if len(last_results) > 1 else None
        elif ref_lower in ['third', 'third one', 'the third', 'the third one']:
            return last_results[2] if len(last_results) > 2 else None
        elif ref_lower in ['last', 'last one', 'the last', 'the last one']:
            return last_results[-1] if len(last_results) > 0 else None
        elif ref_lower in ['that', 'that one', 'this', 'this one', 'it']:
            # Default to first result for ambiguous references
            return last_results[0] if len(last_results) > 0 else None
            
        return None


    async def execute_function(
        self,
        function_name: str,
        arguments: str,
        jwt_token: str,
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Execute a function call from the LLM.

        Args:
            function_name: Name of the function to execute
            arguments: JSON string of function arguments
            jwt_token: JWT token for Phase II API authentication
            context: Conversation context for resolving references (optional)

        Returns:
            Dictionary with execution result
        """
        try:
            # Parse arguments
            args = json.loads(arguments) if isinstance(arguments, str) else arguments

            logger.info(f"Executing function: {function_name} with args: {args}")

            # Route to appropriate handler
            if function_name == "create_todo":
                return await self._execute_create_todo(args, jwt_token)
            elif function_name == "get_todos":
                return await self._execute_get_todos(args, jwt_token)
            elif function_name == "update_todo":
                return await self._execute_update_todo(args, jwt_token, context)
            elif function_name == "complete_todo":
                return await self._execute_complete_todo(args, jwt_token, context)
            elif function_name == "delete_todo":
                return await self._execute_delete_todo(args, jwt_token, context)
            else:
                return {
                    "success": False,
                    "error": f"Unknown function: {function_name}"
                }

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse function arguments: {e}")
            return {
                "success": False,
                "error": f"Invalid function arguments: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Error executing function {function_name}: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"Function execution failed: {str(e)}"
            }

    async def _execute_create_todo(
        self,
        args: Dict[str, Any],
        jwt_token: str
    ) -> Dict[str, Any]:
        """Execute create_todo function.

        Args:
            args: Function arguments
            jwt_token: JWT token for authentication

        Returns:
            Execution result with created todo
        """
        try:
            title = args.get("title")
            if not title:
                return {"success": False, "error": "Title is required"}

            description = args.get("description", "")
            priority = args.get("priority", "medium")
            tags = args.get("tags", [])

            # Parse due date if provided
            due_date = None
            if args.get("due_date"):
                due_date = self._parse_date(args["due_date"])
                if not due_date:
                    return {
                        "success": False,
                        "error": f"Could not parse due date: {args['due_date']}"
                    }

            # Create todo via Phase II API
            todo = await self.phase2_client.create_todo(
                jwt_token=jwt_token,
                title=title,
                description=description,
                priority=priority,
                tags=tags,
                due_date=due_date
            )

            return {
                "success": True,
                "todo": todo,
                "message": f"Created todo: {title}"
            }

        except Exception as e:
            logger.error(f"Error creating todo: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"Failed to create todo: {str(e)}"
            }

    async def _execute_get_todos(
        self,
        args: Dict[str, Any],
        jwt_token: str
    ) -> Dict[str, Any]:
        """Execute get_todos function.

        Args:
            args: Function arguments
            jwt_token: JWT token for authentication

        Returns:
            Execution result with todos list
        """
        try:
            # Extract filter parameters
            completed = args.get("completed")
            priority = args.get("priority")
            tags = args.get("tags")
            search = args.get("search")

            # Parse date range filter if provided
            # Note: Phase II API doesn't have date range filtering built-in,
            # so we'll need to filter client-side or enhance the query
            due_date_filter = args.get("due_date_filter")

            # Get todos via Phase II API
            result = await self.phase2_client.get_todos(
                jwt_token=jwt_token,
                completed=completed,
                priority=priority,
                tags=tags,
                search=search,
                limit=100
            )

            todos = result.get("todos", [])

            # Apply date range filter if specified
            if due_date_filter and todos:
                start_date, end_date = self._parse_date_range(due_date_filter)
                if start_date or end_date:
                    filtered_todos = []
                    for todo in todos:
                        if todo.get("due_date"):
                            todo_date = todo["due_date"]
                            if start_date and todo_date < start_date:
                                continue
                            if end_date and todo_date > end_date:
                                continue
                            filtered_todos.append(todo)
                    todos = filtered_todos

            return {
                "success": True,
                "todos": todos,
                "count": len(todos),
                "message": f"Found {len(todos)} todo(s)"
            }

        except Exception as e:
            logger.error(f"Error getting todos: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"Failed to get todos: {str(e)}"
            }

    async def _execute_update_todo(
        self,
        args: Dict[str, Any],
        jwt_token: str,
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Execute update_todo function.

        Args:
            args: Function arguments
            jwt_token: JWT token for authentication
            context: Conversation context for resolving references

        Returns:
            Execution result with updated todo
        """
        try:
            todo_id = args.get("todo_id")
            if not todo_id:
                return {"success": False, "error": "Todo ID is required"}

            # Resolve todo reference if needed (e.g., "first", "second")
            if isinstance(todo_id, str) and not todo_id.isdigit():
                resolved_id = self._resolve_todo_reference(todo_id, context)
                if resolved_id:
                    todo_id = resolved_id
                else:
                    return {"success": False, "error": f"Could not resolve reference: {todo_id}"}
            else:
                todo_id = int(todo_id)

            # Parse due date if provided
            due_date = None
            if args.get("due_date"):
                due_date = self._parse_date(args["due_date"])

            # Update todo via Phase II API
            todo = await self.phase2_client.update_todo(
                jwt_token=jwt_token,
                todo_id=todo_id,
                title=args.get("title"),
                description=args.get("description"),
                priority=args.get("priority"),
                tags=args.get("tags"),
                due_date=due_date
            )

            return {
                "success": True,
                "todo": todo,
                "message": f"Updated todo: {todo.get('title')}"
            }

        except Exception as e:
            logger.error(f"Error updating todo: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"Failed to update todo: {str(e)}"
            }

    async def _execute_complete_todo(
        self,
        args: Dict[str, Any],
        jwt_token: str,
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Execute complete_todo function.

        Args:
            args: Function arguments
            jwt_token: JWT token for authentication
            context: Conversation context for resolving references

        Returns:
            Execution result with completed todos
        """
        try:
            todo_ids = args.get("todo_ids", [])
            if not todo_ids:
                return {"success": False, "error": "Todo IDs are required"}

            # Resolve references if needed
            resolved_ids = []
            for tid in todo_ids:
                if isinstance(tid, str) and not str(tid).isdigit():
                    resolved_id = self._resolve_todo_reference(tid, context)
                    if resolved_id:
                        resolved_ids.append(resolved_id)
                else:
                    resolved_ids.append(int(tid))
            
            todo_ids = resolved_ids
            if not todo_ids:
                return {"success": False, "error": "Could not resolve todo references"}

            # Complete each todo
            completed_todos = []
            for todo_id in todo_ids:
                try:
                    todo = await self.phase2_client.complete_todo(
                        jwt_token=jwt_token,
                        todo_id=todo_id
                    )
                    completed_todos.append(todo)
                except Exception as e:
                    logger.error(f"Error completing todo {todo_id}: {e}")

            if not completed_todos:
                return {
                    "success": False,
                    "error": "Failed to complete any todos"
                }

            return {
                "success": True,
                "todos": completed_todos,
                "count": len(completed_todos),
                "message": f"Marked {len(completed_todos)} todo(s) as complete"
            }

        except Exception as e:
            logger.error(f"Error completing todos: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"Failed to complete todos: {str(e)}"
            }

    async def _execute_delete_todo(
        self,
        args: Dict[str, Any],
        jwt_token: str,
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Execute delete_todo function.

        Args:
            args: Function arguments
            jwt_token: JWT token for authentication
            context: Conversation context for resolving references

        Returns:
            Execution result with deletion confirmation
        """
        try:
            todo_ids = args.get("todo_ids", [])
            if not todo_ids:
                return {"success": False, "error": "Todo IDs are required"}

            confirmed = args.get("confirmed", False)

            # Check if confirmation is needed
            if not confirmed:
                return {
                    "success": False,
                    "needs_confirmation": True,
                    "todo_ids": todo_ids,
                    "message": f"Are you sure you want to delete {len(todo_ids)} todo(s)? Please confirm."
                }

            # Delete each todo
            deleted_count = 0
            for todo_id in todo_ids:
                try:
                    await self.phase2_client.delete_todo(
                        jwt_token=jwt_token,
                        todo_id=todo_id
                    )
                    deleted_count += 1
                except Exception as e:
                    logger.error(f"Error deleting todo {todo_id}: {e}")

            if deleted_count == 0:
                return {
                    "success": False,
                    "error": "Failed to delete any todos"
                }

            return {
                "success": True,
                "count": deleted_count,
                "message": f"Deleted {deleted_count} todo(s)"
            }

        except Exception as e:
            logger.error(f"Error deleting todos: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"Failed to delete todos: {str(e)}"
            }
