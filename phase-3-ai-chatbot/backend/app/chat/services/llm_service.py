"""LLM service for OpenAI API integration.

This module provides the LLMService class for interfacing with OpenAI's GPT models,
including function calling for todo operations and streaming response handling.
"""

import logging
import os
from typing import Any, AsyncGenerator, Dict, List, Optional

import openai
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessageParam

logger = logging.getLogger(__name__)


class LLMService:
    """Service for OpenAI LLM integration with function calling.

    This class provides methods for:
    - Generating streaming responses from OpenAI
    - Defining function schemas for todo operations
    - Building system prompts with context
    - Handling function calls from the LLM
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-3.5-turbo",
        max_tokens: int = 1000,
        temperature: float = 0.7
    ):
        """Initialize the LLM service.

        Args:
            api_key: OpenAI API key (default: from OPENAI_API_KEY env var)
            model: Model name (default: gpt-3.5-turbo)
            max_tokens: Maximum tokens in response (default: 1000)
            temperature: Sampling temperature (default: 0.7)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")

        # Allow initialization without API key for testing/development
        # but log a warning
        if not self.api_key or self.api_key == "your-openai-api-key-here":
            logger.warning("OpenAI API key not configured - chat functionality will not work")
            self.api_key = None
            self.client = None
        else:
            self.client = AsyncOpenAI(api_key=self.api_key)
            logger.info(f"LLMService initialized with model: {model}")

        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature

    def _build_system_prompt(
        self,
        user_id: int,
        username: Optional[str] = None,
        recent_todos: Optional[List[Dict]] = None
    ) -> str:
        """Build system prompt with user context.

        Args:
            user_id: User ID from Phase II
            username: Username (optional)
            recent_todos: Recently referenced todos (optional)

        Returns:
            System prompt string
        """
        prompt = f"""You are a professional and courteous todo management assistant. Your primary purpose is to help users efficiently manage their tasks and stay organized.

User Context:
- User ID: {user_id}
{f"- Username: {username}" if username else ""}

Professional Guidelines:
1. Focus exclusively on todo-related requests (create, read, update, delete tasks)
2. Politely decline requests outside your area of expertise
3. Maintain a helpful, respectful, and professional demeanor at all times
4. Be clear about your capabilities and limitations
5. Provide efficient and accurate assistance for all todo management needs

Available Operations:
- Create todos with title, description, priority (low/medium/high), tags, and due dates
- Query and filter todos by status, priority, tags, due dates, or keywords
- Update todo details (title, description, priority, tags, due date, status)
- Mark todos as complete or incomplete
- Delete todos (always ask for confirmation first)

How to Politely Decline Non-Todo Requests:
- "I appreciate your question, but I specialize exclusively in todo management. How may I assist you with your tasks today?"
- "Thank you for reaching out. I'm designed specifically to help with task management. Is there a todo I can help you create or manage?"
- "I'd be happy to help, but my expertise is limited to managing your todos and tasks. Would you like to add a new task or review your existing ones?"
- "While I'd like to assist, I'm specifically designed for todo management. May I help you organize your tasks instead?"
- "I appreciate your interest, but I focus solely on helping you manage your tasks efficiently. How can I assist with your todo list?"

Todo Management Best Practices:
- Be helpful, clear, and efficient when handling todo operations
- Always confirm destructive operations (delete, bulk updates) before executing
- Format todos clearly with all relevant details for easy understanding
- Use the provided functions to perform all todo operations accurately
- Parse natural language dates intelligently (e.g., "tomorrow", "next Monday", "in 3 days")
- Understand contextual references like "the first one", "that task" from previous messages

Confirmation Workflow:
- For delete operations, ALWAYS ask for confirmation first by calling delete_todo with confirmed=false
- When user confirms with "yes", "confirm", "delete them", "go ahead", call delete_todo with confirmed=true
- If user says "no", "cancel", "nevermind", acknowledge respectfully and do not proceed with deletion
- For bulk operations (deleting multiple todos), clearly state how many items will be affected
- Be patient and understanding throughout the confirmation process

Valid Todo Request Examples:
- "Add a task to buy groceries tomorrow" → Create todo
- "Show me my tasks" → Query todos
- "Mark the first task as complete" → Update todo status
- "Delete all completed tasks" → Delete todos (with confirmation)
- "What do I need to do today?" → Query todos by due date

Requests Outside Scope (Politely Decline):
- General conversation or greetings → Politely redirect to todo management
- Questions about weather, news, or general knowledge → Politely explain your specialization
- Technical help or coding assistance → Kindly decline and refocus on tasks
- Any question not directly about managing todos → Courteously redirect to your core function

Remember: Be professional, courteous, and helpful. Your goal is to provide excellent todo management assistance while maintaining appropriate boundaries with grace and respect.
"""

        if recent_todos:
            prompt += "\nRecently Referenced Todos:\n"
            for todo in recent_todos[:5]:  # Show max 5 recent todos
                prompt += f"- [{todo.get('id')}] {todo.get('title')} (Priority: {todo.get('priority')}, Completed: {todo.get('completed')})\n"

        return prompt

    def _define_functions(self) -> List[Dict[str, Any]]:
        """Define function schemas for OpenAI function calling.

        Returns:
            List of function definition dictionaries
        """
        return [
            {
                "name": "create_todo",
                "description": "Create a new todo item with the specified details",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "The title or main description of the todo"
                        },
                        "description": {
                            "type": "string",
                            "description": "Additional details or notes about the todo"
                        },
                        "priority": {
                            "type": "string",
                            "enum": ["low", "medium", "high"],
                            "description": "Priority level of the todo"
                        },
                        "due_date": {
                            "type": "string",
                            "description": "Due date in natural language (e.g., 'tomorrow', 'next Monday', '2026-01-25')"
                        },
                        "tags": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Tags or categories for the todo"
                        }
                    },
                    "required": ["title"]
                }
            },
            {
                "name": "get_todos",
                "description": "Query and filter todos based on various criteria",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "completed": {
                            "type": "boolean",
                            "description": "Filter by completion status (true for completed, false for incomplete)"
                        },
                        "priority": {
                            "type": "string",
                            "enum": ["low", "medium", "high"],
                            "description": "Filter by priority level"
                        },
                        "tags": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Filter by tags (returns todos with any of these tags)"
                        },
                        "search": {
                            "type": "string",
                            "description": "Search text to find in todo titles or descriptions"
                        },
                        "due_date_filter": {
                            "type": "string",
                            "description": "Filter by due date range (e.g., 'today', 'this week', 'overdue')"
                        }
                    }
                }
            },
            {
                "name": "update_todo",
                "description": "Update details of an existing todo",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "todo_id": {
                            "type": "integer",
                            "description": "ID of the todo to update, or reference like 'first', 'second', 'last'"
                        },
                        "title": {
                            "type": "string",
                            "description": "New title for the todo"
                        },
                        "description": {
                            "type": "string",
                            "description": "New description for the todo"
                        },
                        "priority": {
                            "type": "string",
                            "enum": ["low", "medium", "high"],
                            "description": "New priority level"
                        },
                        "due_date": {
                            "type": "string",
                            "description": "New due date in natural language"
                        },
                        "tags": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "New tags for the todo"
                        }
                    },
                    "required": ["todo_id"]
                }
            },
            {
                "name": "complete_todo",
                "description": "Mark one or more todos as complete",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "todo_ids": {
                            "type": "array",
                            "items": {"type": "integer"},
                            "description": "IDs of todos to mark as complete, or references like 'first', 'all'"
                        }
                    },
                    "required": ["todo_ids"]
                }
            },
            {
                "name": "delete_todo",
                "description": "Delete one or more todos (ALWAYS ask for user confirmation first)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "todo_ids": {
                            "type": "array",
                            "items": {"type": "integer"},
                            "description": "IDs of todos to delete"
                        },
                        "confirmed": {
                            "type": "boolean",
                            "description": "Whether user has confirmed the deletion"
                        }
                    },
                    "required": ["todo_ids"]
                }
            }
        ]

    async def generate_response(
        self,
        messages: List[ChatCompletionMessageParam],
        user_id: int,
        username: Optional[str] = None,
        recent_todos: Optional[List[Dict]] = None,
        stream: bool = True
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Generate streaming response from OpenAI with function calling.

        Args:
            messages: Conversation history in OpenAI format
            user_id: User ID for system prompt
            username: Username for system prompt (optional)
            recent_todos: Recently referenced todos for context (optional)
            stream: Whether to stream the response (default: True)

        Yields:
            Dictionary with response chunks or function calls
        """
        # Build system prompt with context
        system_prompt = self._build_system_prompt(user_id, username, recent_todos)

        # Prepend system message
        full_messages = [
            {"role": "system", "content": system_prompt},
            *messages
        ]

        # Define available functions
        functions = self._define_functions()

        try:
            logger.info(f"Generating response for user {user_id} (stream={stream})")

            if stream:
                # Streaming response
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=full_messages,
                    functions=functions,
                    function_call="auto",
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    stream=True
                )

                function_name = None
                function_args = ""

                async for chunk in response:
                    delta = chunk.choices[0].delta

                    # Check for function call
                    if delta.function_call:
                        if delta.function_call.name:
                            function_name = delta.function_call.name
                        if delta.function_call.arguments:
                            function_args += delta.function_call.arguments

                    # Check for content (text response)
                    elif delta.content:
                        yield {
                            "type": "token",
                            "content": delta.content
                        }

                    # Check if response is complete
                    if chunk.choices[0].finish_reason == "function_call":
                        yield {
                            "type": "function_call",
                            "function_name": function_name,
                            "arguments": function_args
                        }
                    elif chunk.choices[0].finish_reason == "stop":
                        yield {
                            "type": "done"
                        }

            else:
                # Non-streaming response
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=full_messages,
                    functions=functions,
                    function_call="auto",
                    max_tokens=self.max_tokens,
                    temperature=self.temperature
                )

                message = response.choices[0].message

                if message.function_call:
                    yield {
                        "type": "function_call",
                        "function_name": message.function_call.name,
                        "arguments": message.function_call.arguments
                    }
                elif message.content:
                    yield {
                        "type": "content",
                        "content": message.content
                    }

                yield {"type": "done"}

        except openai.APIConnectionError as e:
            logger.error(f"OpenAI API connection error: {e}")
            yield {
                "type": "error",
                "error": "I'm having trouble connecting to my AI service. Please check your internet connection and try again in a moment."
            }
        except openai.RateLimitError as e:
            logger.error(f"OpenAI rate limit exceeded: {e}")
            yield {
                "type": "error",
                "error": "I'm receiving too many requests right now. Please wait a moment and try again."
            }
        except openai.APIError as e:
            logger.error(f"OpenAI API error: {e}")
            yield {
                "type": "error",
                "error": "My AI service is temporarily unavailable. Please try again in a few moments."
            }
        except Exception as e:
            logger.error(f"Error generating response: {e}", exc_info=True)
            yield {
                "type": "error",
                "error": "An unexpected error occurred. Please try again."
            }

    async def generate_simple_response(
        self,
        prompt: str,
        user_id: int
    ) -> str:
        """Generate a simple non-streaming response without function calling.

        Args:
            prompt: User prompt
            user_id: User ID for system prompt

        Returns:
            Response text
        """
        system_prompt = self._build_system_prompt(user_id)

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )

            return response.choices[0].message.content or ""

        except Exception as e:
            logger.error(f"Error generating simple response: {e}", exc_info=True)
            return f"I'm sorry, I encountered an error: {str(e)}"
