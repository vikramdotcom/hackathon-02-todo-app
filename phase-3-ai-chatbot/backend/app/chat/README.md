# AI-Powered Todo Chatbot - Backend

**Phase III Feature**: Conversational todo management through natural language

## Architecture Overview

The chat backend is built as a modular extension to the Phase II Todo application, providing AI-powered conversational interfaces without modifying existing Phase II code.

### Components

```
app/chat/
├── models/
│   └── chat_models.py          # Data models for sessions, messages, context
├── services/
│   ├── conversation_manager.py # Session storage and management
│   ├── llm_service.py          # OpenAI API integration
│   ├── function_executor.py    # Execute LLM function calls
│   └── phase2_client.py        # HTTP client for Phase II APIs
└── api/
    └── chat_routes.py          # FastAPI endpoints for chat
```

### Key Features

✅ **Natural Language Task Creation**
- Parse dates: "tomorrow", "next Monday", "in 3 days"
- Extract priorities: low, medium, high
- Support tags and descriptions

✅ **Multi-Turn Conversations**
- Context management with sliding window (20 messages)
- Reference resolution: "the first one", "that task"
- Session persistence with 30-minute timeout

✅ **Task Queries and Filtering**
- Filter by status, priority, tags, due dates
- Natural language queries: "show me high priority tasks"
- Display results as interactive todo cards

✅ **Task Updates and Completion**
- Update any todo field through conversation
- Mark single or multiple tasks complete
- Reference resolution for updates

✅ **Safe Deletion with Confirmation**
- Always request confirmation for deletions
- 2-minute confirmation timeout
- Bulk deletion support

✅ **Streaming Responses**
- Real-time token-by-token responses
- Server-Sent Events (SSE) format
- Function call execution during streaming

## Configuration

### Environment Variables

```env
# OpenAI Configuration
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_MAX_TOKENS=1000
OPENAI_TEMPERATURE=0.7

# Phase II API Configuration
PHASE2_API_BASE_URL=http://localhost:8000/api/v1

# Chat Configuration
CHAT_SESSION_TIMEOUT_MINUTES=30
CHAT_MAX_MESSAGES_PER_SESSION=20
CHAT_MAX_CONTEXT_TURNS=10
```

### Dependencies

Install chat-specific dependencies:

```bash
pip install -r requirements-chat.txt
```

Required packages:
- `openai==1.12.0` - OpenAI API client
- `httpx==0.26.0` - Async HTTP client
- `dateparser==1.2.0` - Natural language date parsing
- `python-dotenv==1.0.0` - Environment management

## API Endpoints

### POST /api/v1/chat/message

Send a chat message and receive streaming response.

**Request:**
```json
{
  "session_id": "optional-uuid",
  "message": "Add a task to buy groceries tomorrow"
}
```

**Response:** Server-Sent Events stream

```
data: {"type": "session_id", "session_id": "uuid"}
data: {"type": "token", "content": "I've"}
data: {"type": "token", "content": " added"}
data: {"type": "todo", "todo": {...}}
data: {"type": "done"}
```

**Authentication:** Requires JWT token in Authorization header

### GET /api/v1/chat/health

Health check endpoint for chat service.

**Response:**
```json
{
  "status": "healthy",
  "service": "chat",
  "llm_configured": true,
  "phase2_api_url": "http://localhost:8000/api/v1",
  "session_stats": {
    "total_sessions": 5,
    "total_messages": 42
  }
}
```

## Data Models

### ConversationSession
- `session_id`: UUID identifier
- `user_id`: User from Phase II
- `messages`: List of ChatMessage objects
- `context`: ConversationContext with references
- `created_at`, `last_activity_at`: Timestamps

### ChatMessage
- `message_id`: UUID identifier
- `role`: "user" or "assistant"
- `content`: Message text
- `timestamp`: ISO datetime
- `metadata`: Optional MessageMetadata

### ConversationContext
- `referenced_todos`: Dict of TodoReference objects
- `last_query_results`: List of todo IDs
- `pending_confirmation`: PendingConfirmation for deletions

## Session Management

**Storage:** In-memory dictionary (MVP)
- Sessions expire after 30 minutes of inactivity
- Background cleanup task runs every 5 minutes
- Session IDs stored in client localStorage

**Production:** Use Redis for multi-instance deployments

## Function Calling

The LLM service defines functions that map to Phase II API operations:

1. **create_todo** - Create new todo
2. **get_todos** - Query and filter todos
3. **update_todo** - Update todo fields
4. **complete_todo** - Mark todos complete
5. **delete_todo** - Delete todos (with confirmation)

Function calls are executed by `FunctionExecutor`, which:
- Validates arguments
- Parses natural language dates
- Calls Phase II APIs with JWT token
- Formats results for LLM

## Error Handling

- Input validation: max 10,000 characters, sanitized
- OpenAI API errors: rate limits, API failures
- Phase II API errors: 401, 404, 500 responses
- User-friendly error messages in responses

## Logging

All services include comprehensive logging:
- Session creation and cleanup
- Function call execution
- API errors and retries
- Token usage (for monitoring)

## Testing

### Manual Testing Scenarios

1. **Task Creation**
   ```
   User: "Add a task to buy groceries tomorrow"
   Expected: Todo created with due date = tomorrow
   ```

2. **Task Query**
   ```
   User: "Show me all high priority tasks"
   Expected: List of high priority todos displayed
   ```

3. **Multi-Turn Context**
   ```
   User: "Show my tasks"
   User: "Mark the first one as complete"
   Expected: First task from previous query marked complete
   ```

4. **Deletion with Confirmation**
   ```
   User: "Delete all completed tasks"
   Expected: System asks for confirmation
   User: "Yes"
   Expected: Tasks deleted
   ```

### Integration Testing

Run with Phase II backend:

```bash
# Terminal 1: Start Phase II backend
cd phase-3-ai-chatbot/backend
uvicorn app.main:app --port 8000

# Terminal 2: Start chat-enabled backend
uvicorn app.main:app --port 8001 --reload
```

## Performance

- First token: <1 second (p95)
- Complete response: <3 seconds (p95)
- Concurrent users: 100+
- Session cleanup: Every 5 minutes

## Security

- JWT authentication required for all endpoints
- User isolation: users only access their own todos
- Input sanitization: remove control characters
- Confirmation required for destructive operations
- Session IDs are secure UUIDs

## Troubleshooting

### "OpenAI API key not provided"
- Check `.env` file has valid `OPENAI_API_KEY`
- Restart backend after updating `.env`

### "Session not found or expired"
- Sessions expire after 30 minutes
- Clear localStorage and start new conversation

### "Phase II API not responding"
- Verify Phase II backend is running
- Check `PHASE2_API_BASE_URL` in `.env`

### Streaming not working
- Check browser supports Server-Sent Events
- Verify CORS configuration allows streaming

## Future Enhancements

- Redis session storage for production
- Persistent conversation history
- Bulk update operations
- Smart task suggestions
- Rate limiting per user
- Conversation analytics

## References

- [Feature Specification](../../../specs/1-ai-chatbot/spec.md)
- [Implementation Plan](../../../specs/1-ai-chatbot/plan.md)
- [API Contracts](../../../specs/1-ai-chatbot/contracts/chat-api.yaml)
- [OpenAI Function Calling](https://platform.openai.com/docs/guides/function-calling)
