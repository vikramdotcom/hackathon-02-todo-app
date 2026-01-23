# Quickstart: AI-Powered Todo Chatbot

**Feature**: 1-ai-chatbot
**Date**: 2026-01-22
**Audience**: Developers implementing this feature

---

## Overview

This quickstart guide provides step-by-step instructions for implementing the AI-Powered Todo Chatbot feature. Follow these steps in order to build a working conversational interface for todo management.

---

## Prerequisites

### Required
- Phase II Todo application running and accessible
- Phase II API endpoints operational (see Phase II API documentation)
- Python 3.11+ installed
- Node.js 18+ and npm installed
- OpenAI API key with GPT-3.5-turbo or GPT-4 access

### Recommended
- Familiarity with FastAPI and React
- Understanding of JWT authentication
- Basic knowledge of LLM function calling

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend (Next.js)                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Chat Page    │  │ Chat         │  │ Todo Card    │      │
│  │ /chat        │─▶│ Interface    │─▶│ Component    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└────────────────────────────┬────────────────────────────────┘
                             │ POST /api/v1/chat/message
                             │ (streaming response)
┌────────────────────────────▼────────────────────────────────┐
│                    Chat Backend (FastAPI)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Chat API     │─▶│ Conversation │─▶│ LLM Service  │      │
│  │ Endpoint     │  │ Manager      │  │ (OpenAI)     │      │
│  └──────────────┘  └──────────────┘  └──────┬───────┘      │
│                                              │               │
│  ┌──────────────┐  ┌──────────────┐        │               │
│  │ Function     │◀─│ Phase II API │◀───────┘               │
│  │ Executor     │  │ Client       │                         │
│  └──────────────┘  └──────────────┘                         │
└────────────────────────────┬────────────────────────────────┘
                             │ HTTP requests with JWT
┌────────────────────────────▼────────────────────────────────┐
│                   Phase II Backend (existing)                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Auth API     │  │ Todo API     │  │ User API     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

---

## Implementation Steps

### Step 1: Backend Setup

#### 1.1 Install Dependencies

Create `requirements-chat.txt` in the backend directory:

```txt
openai==1.12.0
httpx==0.26.0
dateparser==1.2.0
python-dotenv==1.0.0
```

Install:
```bash
cd phase-3-ai-chatbot/backend
pip install -r requirements-chat.txt
```

#### 1.2 Configure Environment

Add to `.env`:
```env
# OpenAI Configuration
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_MAX_TOKENS=1000

# Phase II API Configuration
PHASE2_API_BASE_URL=http://localhost:8000/api/v1

# Chat Configuration
CHAT_SESSION_TIMEOUT_MINUTES=30
CHAT_MAX_MESSAGES_PER_SESSION=20
```

#### 1.3 Create Directory Structure

```bash
cd phase-3-ai-chatbot/backend
mkdir -p app/chat/{services,models,api}
touch app/chat/__init__.py
touch app/chat/services/{__init__.py,conversation_manager.py,llm_service.py,function_executor.py,phase2_client.py}
touch app/chat/models/{__init__.py,chat_models.py}
touch app/chat/api/{__init__.py,chat_routes.py}
```

---

### Step 2: Implement Core Services

#### 2.1 Phase II API Client

**File**: `app/chat/services/phase2_client.py`

**Purpose**: HTTP client for calling Phase II APIs

**Key Methods**:
- `get_todos(jwt_token, filters)` → List todos
- `create_todo(jwt_token, todo_data)` → Create todo
- `update_todo(jwt_token, todo_id, updates)` → Update todo
- `delete_todo(jwt_token, todo_id)` → Delete todo
- `complete_todo(jwt_token, todo_id)` → Mark complete

**Implementation Notes**:
- Use `httpx.AsyncClient` for async requests
- Pass JWT token in Authorization header
- Handle HTTP errors and convert to user-friendly messages
- Implement retry logic for transient failures

---

#### 2.2 LLM Service

**File**: `app/chat/services/llm_service.py`

**Purpose**: Wrapper for OpenAI API with function calling

**Key Methods**:
- `generate_response(messages, functions)` → Stream response
- `_build_system_prompt(user_context)` → Create system prompt
- `_define_functions()` → Define available functions

**Function Definitions**:
```python
functions = [
    {
        "name": "create_todo",
        "description": "Create a new todo item",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "description": {"type": "string"},
                "priority": {"type": "string", "enum": ["low", "medium", "high"]},
                "due_date": {"type": "string"},
                "tags": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["title"]
        }
    },
    {
        "name": "get_todos",
        "description": "Query and filter todos",
        "parameters": {
            "type": "object",
            "properties": {
                "completed": {"type": "boolean"},
                "priority": {"type": "string"},
                "tags": {"type": "array"},
                "search": {"type": "string"}
            }
        }
    },
    # ... more functions for update, delete, complete
]
```

**System Prompt Template**:
```
You are a helpful todo management assistant. You help users manage their tasks through natural conversation.

User Context:
- User ID: {user_id}
- Username: {username}

Available Operations:
- Create, read, update, delete todos
- Mark todos complete/incomplete
- Query and filter todos

Guidelines:
- Be concise and friendly
- Confirm destructive operations before executing
- When showing todos, format them clearly
- If unsure about user intent, ask for clarification
- Use the provided functions to perform operations
```

---

#### 2.3 Function Executor

**File**: `app/chat/services/function_executor.py`

**Purpose**: Execute LLM function calls by calling Phase II APIs

**Key Methods**:
- `execute_function(function_name, arguments, jwt_token)` → Result
- `_parse_date(date_string)` → datetime
- `_validate_arguments(function_name, arguments)` → bool

**Implementation Notes**:
- Map function names to Phase II API calls
- Parse natural language dates using `dateparser`
- Validate arguments before API calls
- Handle API errors gracefully
- Return structured results for LLM

---

#### 2.4 Conversation Manager

**File**: `app/chat/services/conversation_manager.py`

**Purpose**: Manage conversation sessions and context

**Key Methods**:
- `create_session(user_id)` → session_id
- `get_session(session_id)` → ConversationSession
- `add_message(session_id, role, content)` → None
- `update_context(session_id, context_updates)` → None
- `cleanup_expired_sessions()` → None

**Storage**:
```python
# In-memory storage (MVP)
sessions: Dict[str, ConversationSession] = {}

# Background cleanup task
async def cleanup_task():
    while True:
        await asyncio.sleep(300)  # 5 minutes
        cleanup_expired_sessions()
```

---

### Step 3: Implement API Endpoint

#### 3.1 Chat Routes

**File**: `app/chat/api/chat_routes.py`

**Endpoint**: `POST /api/v1/chat/message`

**Flow**:
1. Extract JWT token from Authorization header
2. Get or create conversation session
3. Add user message to session
4. Build message history for LLM
5. Call LLM service with streaming
6. For each token/function call:
   - If token: stream to client
   - If function call: execute function, add result to messages
7. Add assistant response to session
8. Return session_id in header

**Streaming Response**:
```python
async def stream_response():
    async for chunk in llm_service.generate_response(messages, functions):
        if chunk.type == "token":
            yield f"data: {json.dumps({'type': 'token', 'content': chunk.content})}\n\n"
        elif chunk.type == "function_call":
            result = await function_executor.execute(chunk.name, chunk.args, jwt_token)
            # Add result to messages and continue
        elif chunk.type == "done":
            yield f"data: {json.dumps({'type': 'done', 'message_id': message_id})}\n\n"
```

---

### Step 4: Frontend Implementation

#### 4.1 Create Chat Page

**File**: `frontend/src/app/chat/page.tsx`

```tsx
export default function ChatPage() {
  return (
    <div className="container mx-auto p-4">
      <h1>Todo Chat Assistant</h1>
      <ChatInterface />
    </div>
  );
}
```

#### 4.2 Chat Interface Component

**File**: `frontend/src/components/ChatInterface.tsx`

**State**:
```tsx
const [messages, setMessages] = useState<Message[]>([]);
const [input, setInput] = useState("");
const [sessionId, setSessionId] = useState<string | null>(null);
const [isLoading, setIsLoading] = useState(false);
```

**Send Message Function**:
```tsx
async function sendMessage() {
  const userMessage = { role: "user", content: input };
  setMessages([...messages, userMessage]);
  setInput("");
  setIsLoading(true);

  const response = await fetch("/api/v1/chat/message", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${getToken()}`
    },
    body: JSON.stringify({
      session_id: sessionId,
      message: input
    })
  });

  // Get session_id from header
  const newSessionId = response.headers.get("X-Session-Id");
  if (newSessionId) setSessionId(newSessionId);

  // Read streaming response
  const reader = response.body.getReader();
  let assistantMessage = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    const text = new TextDecoder().decode(value);
    const lines = text.split("\n");

    for (const line of lines) {
      if (line.startsWith("data: ")) {
        const data = JSON.parse(line.slice(6));
        if (data.type === "token") {
          assistantMessage += data.content;
          // Update UI incrementally
        }
      }
    }
  }

  setMessages([...messages, userMessage, { role: "assistant", content: assistantMessage }]);
  setIsLoading(false);
}
```

---

### Step 5: Testing

#### 5.1 Unit Tests

**Test Conversation Manager**:
```python
def test_create_session():
    manager = ConversationManager()
    session_id = manager.create_session(user_id=1)
    assert session_id is not None
    session = manager.get_session(session_id)
    assert session.user_id == 1
```

**Test Function Executor**:
```python
async def test_execute_create_todo():
    executor = FunctionExecutor(phase2_client)
    result = await executor.execute_function(
        "create_todo",
        {"title": "Test task", "priority": "high"},
        jwt_token
    )
    assert result["success"] == True
```

#### 5.2 Integration Tests

**Test Full Chat Flow**:
```python
async def test_chat_message_flow():
    response = await client.post(
        "/api/v1/chat/message",
        json={"message": "Create a task to buy groceries"},
        headers={"Authorization": f"Bearer {jwt_token}"}
    )
    assert response.status_code == 200
    session_id = response.headers["X-Session-Id"]
    assert session_id is not None
```

#### 5.3 Manual Testing Scenarios

1. **Create Todo**: "Add a task to buy groceries tomorrow"
2. **Query Todos**: "Show me all high priority tasks"
3. **Update Todo**: "Mark the first one as complete"
4. **Delete Todo**: "Delete all completed tasks" (should ask for confirmation)
5. **Multi-Turn**: "Show my tasks" → "Mark the second one complete"

---

## Development Workflow

### 1. Start Phase II Backend
```bash
cd phase-3-ai-chatbot/backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
uvicorn app.main:app --reload
```

### 2. Start Frontend
```bash
cd phase-3-ai-chatbot/frontend
npm run dev
```

### 3. Test Chat Interface
- Navigate to `http://localhost:3000/chat`
- Login with test user
- Send test messages

---

## Troubleshooting

### Issue: "Session not found"
- **Cause**: Session expired or invalid session_id
- **Solution**: Clear localStorage and start new conversation

### Issue: "OpenAI rate limit exceeded"
- **Cause**: Too many requests to OpenAI API
- **Solution**: Implement request queuing or use GPT-3.5-turbo

### Issue: "Phase II API not responding"
- **Cause**: Phase II backend not running or wrong URL
- **Solution**: Check PHASE2_API_BASE_URL in .env

### Issue: Streaming not working
- **Cause**: Browser or proxy blocking SSE
- **Solution**: Check browser console, verify Content-Type header

---

## Performance Optimization

### Backend
- Use connection pooling for Phase II API calls
- Cache frequently accessed todos in conversation context
- Implement request queuing for OpenAI API

### Frontend
- Debounce user input
- Implement optimistic UI updates
- Use React.memo for message components

---

## Security Considerations

1. **JWT Validation**: Always validate JWT before processing messages
2. **Rate Limiting**: Implement per-user rate limits (60 messages/hour)
3. **Input Sanitization**: Validate and sanitize user input
4. **Prompt Injection**: Never expose system prompts to users
5. **Session Security**: Use secure session IDs (UUIDs)

---

## Next Steps

After completing this quickstart:
1. Review `/specs/1-ai-chatbot/tasks.md` for detailed implementation tasks
2. Run `/sp.tasks` to generate task breakdown
3. Begin implementation following TDD approach
4. Test each component thoroughly before integration

---

## Resources

- [OpenAI Function Calling Documentation](https://platform.openai.com/docs/guides/function-calling)
- [FastAPI Streaming Responses](https://fastapi.tiangolo.com/advanced/custom-response/#streamingresponse)
- [Phase II API Documentation](../../backend/README.md)
- [Feature Specification](./spec.md)
- [Data Model](./data-model.md)
- [API Contracts](./contracts/chat-api.yaml)
