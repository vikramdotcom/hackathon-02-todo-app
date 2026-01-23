# Implementation Plan: AI-Powered Todo Chatbot

**Branch**: `1-ai-chatbot` | **Date**: 2026-01-22 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/1-ai-chatbot/spec.md`

---

## Summary

Transform the Phase II Todo application into an AI-powered conversational assistant that allows users to manage tasks through natural language interactions. Users can create, update, query, and organize todos by chatting with the system, eliminating the need to navigate traditional UI forms.

**Technical Approach**: Build a stateless chat API using FastAPI that integrates OpenAI's GPT-3.5-turbo/GPT-4 with function calling to orchestrate todo operations. The system maintains session-based conversation context in memory (MVP) or Redis (production), streams responses to a custom React chat interface, and executes all todo operations through existing Phase II REST APIs without modifying Phase II code or database schemas.

---

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript/React 18+ (frontend)

**Primary Dependencies**:
- Backend: FastAPI (existing), OpenAI SDK (openai), httpx, dateparser, python-jose (existing), SQLModel (existing)
- Frontend: Next.js 14+ (existing), React 18+ (existing), Fetch API with streaming

**Storage**:
- Session data: In-memory dict (MVP) or Redis (production)
- Todo data: Phase II database (no changes, API-only access)

**Testing**: pytest (backend), Jest/React Testing Library (frontend)

**Target Platform**:
- Backend: Linux/Windows server (same as Phase II)
- Frontend: Web browsers (Chrome, Firefox, Safari, Edge)

**Project Type**: Web application (backend + frontend)

**Performance Goals**:
- First token response: <1 second (p95)
- Complete response: <3 seconds (p95)
- Support 100 concurrent users
- Handle 1000+ messages per minute

**Constraints**:
- Cannot modify Phase II code, database, or APIs
- Must use existing Phase II authentication (JWT)
- Session-based context only (no persistent conversation history in MVP)
- OpenAI API rate limits and token costs
- 30-minute session timeout

**Scale/Scope**:
- MVP: Single backend instance, in-memory sessions
- Production: Multi-instance with Redis, 1000+ concurrent users
- Average 5-20 messages per conversation
- Support 10-turn conversation context

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Initial Check (Before Phase 0)

✅ **Spec-Driven Development**: Feature has complete specification (spec.md) with clear intent, inputs/outputs, constraints, and acceptance criteria

✅ **Data Model Compliance**: No modifications to Phase II Todo schema; all todo operations use existing APIs

✅ **Phase Isolation**: Chat feature is architecturally independent; Phase II remains unchanged and functional

✅ **Feature Completeness**: Specification includes clear intent (conversational todo management), defined inputs/outputs (chat API), explicit constraints (no Phase II modifications), and acceptance criteria (95% accuracy, 2s response time)

✅ **Code Generation**: Implementation will be generated from specifications following TDD approach

### Post-Design Check (After Phase 1)

✅ **Spec-Driven Development**: All design artifacts (research.md, data-model.md, contracts/, quickstart.md) derived from specification

✅ **Data Model Compliance**: Chat entities (ConversationSession, ChatMessage) are separate from Phase II; todo data accessed only via APIs

✅ **Phase Isolation**: Chat backend can be deployed independently; no Phase II dependencies beyond API contracts

✅ **Testing Discipline**: Test strategy defined in quickstart.md (unit tests for services, integration tests for API flow)

✅ **Error Handling**: Error taxonomy defined in API contracts (400, 401, 404, 429); user-friendly error messages specified

✅ **Code Quality**: Architecture follows simplicity principle (custom implementation vs. heavy frameworks); no hardcoded secrets (OpenAI key in .env)

**Result**: ✅ All constitution gates passed

---

## Project Structure

### Documentation (this feature)

```text
specs/1-ai-chatbot/
├── spec.md              # Feature specification (existing)
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output - technology decisions
├── data-model.md        # Phase 1 output - chat entities
├── quickstart.md        # Phase 1 output - implementation guide
├── contracts/           # Phase 1 output - API contracts
│   └── chat-api.yaml    # OpenAPI spec for chat endpoints
├── checklists/          # Existing validation checklists
│   └── requirements.md
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT YET CREATED)
```

### Source Code (repository root)

```text
phase-3-ai-chatbot/
├── backend/
│   ├── app/
│   │   ├── chat/                    # NEW: Chat feature module
│   │   │   ├── __init__.py
│   │   │   ├── models/
│   │   │   │   ├── __init__.py
│   │   │   │   └── chat_models.py   # ConversationSession, ChatMessage, etc.
│   │   │   ├── services/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── conversation_manager.py  # Session management
│   │   │   │   ├── llm_service.py           # OpenAI API wrapper
│   │   │   │   ├── function_executor.py     # Execute LLM function calls
│   │   │   │   └── phase2_client.py         # HTTP client for Phase II APIs
│   │   │   └── api/
│   │   │       ├── __init__.py
│   │   │       └── chat_routes.py   # Chat API endpoints
│   │   ├── main.py                  # MODIFY: Register chat routes
│   │   └── [existing Phase II code] # NO CHANGES
│   ├── tests/
│   │   ├── chat/                    # NEW: Chat tests
│   │   │   ├── __init__.py
│   │   │   ├── test_conversation_manager.py
│   │   │   ├── test_llm_service.py
│   │   │   ├── test_function_executor.py
│   │   │   └── test_chat_api.py
│   │   └── [existing Phase II tests] # NO CHANGES
│   ├── requirements-chat.txt        # NEW: Chat dependencies
│   └── [existing Phase II files]    # NO CHANGES
│
└── frontend/
    ├── src/
    │   ├── app/
    │   │   ├── chat/                # NEW: Chat page
    │   │   │   └── page.tsx
    │   │   └── [existing pages]     # NO CHANGES
    │   ├── components/
    │   │   ├── chat/                # NEW: Chat components
    │   │   │   ├── ChatInterface.tsx
    │   │   │   ├── MessageList.tsx
    │   │   │   ├── MessageBubble.tsx
    │   │   │   ├── InputBox.tsx
    │   │   │   └── TodoCard.tsx
    │   │   └── [existing components] # NO CHANGES
    │   ├── lib/
    │   │   ├── chat-api.ts          # NEW: Chat API client
    │   │   └── [existing lib]       # NO CHANGES
    │   └── types/
    │       ├── chat.ts              # NEW: Chat TypeScript types
    │       └── [existing types]     # NO CHANGES
    └── [existing frontend files]    # NO CHANGES
```

**Structure Decision**: Web application structure. All new chat functionality is isolated in dedicated `chat/` directories within both backend and frontend. Phase II code remains untouched. Chat backend integrates with existing FastAPI app by registering new routes. Frontend adds new chat page and components without modifying existing pages.

---

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations. All constitution principles are satisfied.

---

## Architecture Overview

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend (Next.js)                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Chat Page    │  │ Chat         │  │ Todo Card    │      │
│  │ /chat        │─▶│ Interface    │─▶│ Component    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└────────────────────────────┬────────────────────────────────┘
                             │ POST /api/v1/chat/message
                             │ (streaming SSE response)
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

### Key Components

#### 1. Chat API Endpoint (`chat_routes.py`)
- **Responsibility**: Handle HTTP requests, manage streaming responses
- **Inputs**: User message, session_id (optional), JWT token
- **Outputs**: Server-Sent Events stream with tokens, todos, completion
- **Dependencies**: ConversationManager, LLMService

#### 2. Conversation Manager (`conversation_manager.py`)
- **Responsibility**: Manage conversation sessions and context
- **Storage**: In-memory dict (MVP) or Redis (production)
- **Operations**: Create session, add message, update context, cleanup expired
- **Data**: ConversationSession with messages and context

#### 3. LLM Service (`llm_service.py`)
- **Responsibility**: Interface with OpenAI API, handle function calling
- **Inputs**: Message history, available functions, user context
- **Outputs**: Streaming tokens or function calls
- **Configuration**: Model (GPT-3.5-turbo/GPT-4), max tokens, temperature

#### 4. Function Executor (`function_executor.py`)
- **Responsibility**: Execute LLM function calls by calling Phase II APIs
- **Functions**: create_todo, get_todos, update_todo, delete_todo, complete_todo
- **Processing**: Parse dates, validate arguments, handle errors
- **Output**: Structured results for LLM

#### 5. Phase II API Client (`phase2_client.py`)
- **Responsibility**: HTTP client for Phase II REST APIs
- **Methods**: Async HTTP calls with retry logic
- **Authentication**: Pass JWT token in Authorization header
- **Error Handling**: Convert HTTP errors to user-friendly messages

---

## Key Design Decisions

### Decision 1: OpenAI Function Calling vs. Custom NLU

**Options Considered**:
1. OpenAI function calling
2. Separate NLU service (Rasa, Dialogflow)
3. Rule-based intent classification

**Decision**: OpenAI function calling

**Rationale**:
- Leverages LLM's natural language understanding
- No separate service to maintain
- No training data required
- Handles ambiguity better than rule-based systems
- Simpler architecture

**Trade-offs**:
- Higher token costs per request
- Dependent on OpenAI API availability
- Slightly higher latency than local NLU

**Documented in**: [research.md](./research.md#7-intent-classification--entity-extraction)

---

### Decision 2: Session-Based vs. Persistent Conversation History

**Options Considered**:
1. Session-based (in-memory)
2. Persistent (database storage)

**Decision**: Session-based for MVP

**Rationale**:
- Aligns with constraint: no Phase II database modifications
- Simpler implementation
- Reduces privacy concerns
- Can be enhanced later with separate conversation database

**Trade-offs**:
- Lost on logout/refresh
- Can't review past conversations
- No conversation analytics

**Migration Path**: Phase 3.1 can add persistence with new tables

**Documented in**: [research.md](./research.md#5-conversation-history-storage)

---

### Decision 3: HTTP Streaming vs. WebSockets

**Options Considered**:
1. HTTP streaming (SSE)
2. WebSockets
3. HTTP polling

**Decision**: HTTP streaming with Fetch API

**Rationale**:
- Simpler than WebSockets for this use case
- Works well with OpenAI's streaming API
- No persistent connection management
- Aligns with REST API patterns

**Trade-offs**:
- Unidirectional streaming (server to client)
- Need separate POST for user messages

**Documented in**: [research.md](./research.md#4-real-time-communication-protocol)

---

### Decision 4: Custom React Components vs. Chat UI Library

**Options Considered**:
1. Custom React components
2. ChatUI libraries (react-chat-elements)
3. Vercel AI SDK UI components

**Decision**: Custom React components

**Rationale**:
- Full control over styling
- Matches existing Phase II UI
- No additional heavy dependencies
- Straightforward requirements

**Trade-offs**:
- Need to build from scratch
- More initial development time

**Documented in**: [research.md](./research.md#3-chat-ui-framework)

---

## API Contracts

### Chat Endpoints

**POST /api/v1/chat/message**
- Send user message, receive streaming response
- Authentication: Required (JWT)
- Request: `{session_id?, message}`
- Response: Server-Sent Events stream
- Status codes: 200 (success), 400 (bad request), 401 (unauthorized), 404 (session not found), 429 (rate limit)

**GET /api/v1/chat/sessions/{session_id}**
- Retrieve conversation history
- Authentication: Required (JWT)
- Response: Full ConversationSession object

**DELETE /api/v1/chat/sessions/{session_id}**
- End conversation and clear history
- Authentication: Required (JWT)
- Response: Success message

**GET /api/v1/chat/sessions**
- List user's active sessions
- Authentication: Required (JWT)
- Response: Array of SessionSummary objects

**Full API specification**: [contracts/chat-api.yaml](./contracts/chat-api.yaml)

---

## Data Model

### Core Entities

1. **ConversationSession**: Tracks ongoing chat interaction
   - session_id (UUID), user_id, created_at, last_activity_at
   - messages (list, max 20), context (ConversationContext)

2. **ChatMessage**: Individual message in conversation
   - message_id (UUID), role (user/assistant), content, timestamp
   - metadata (MessageMetadata)

3. **ConversationContext**: Maintains state within conversation
   - referenced_todos (dict), last_query_results (list)
   - pending_confirmation (PendingConfirmation)

4. **PendingConfirmation**: Tracks destructive operations awaiting confirmation
   - operation (delete/bulk_delete/bulk_update)
   - target_todo_ids, expires_at

**Full data model**: [data-model.md](./data-model.md)

---

## Implementation Strategy

### Phase 0: Research ✅ COMPLETED
- Technology choices documented
- All NEEDS CLARIFICATION items resolved
- Architecture patterns defined

**Output**: [research.md](./research.md)

### Phase 1: Design ✅ COMPLETED
- Data model defined
- API contracts specified
- Quickstart guide created
- Agent context updated

**Outputs**:
- [data-model.md](./data-model.md)
- [contracts/chat-api.yaml](./contracts/chat-api.yaml)
- [quickstart.md](./quickstart.md)

### Phase 2: Task Breakdown (Next Step)
- Run `/sp.tasks` to generate detailed implementation tasks
- Tasks will follow TDD approach (test → implement → verify)
- Each task will be small, testable, and reference specific files

**Output**: tasks.md (to be generated)

### Phase 3: Implementation
- Follow tasks.md in order
- Write tests first (TDD)
- Implement each component
- Verify against acceptance criteria

---

## Testing Strategy

### Unit Tests
- **Conversation Manager**: Session creation, message addition, context updates, cleanup
- **LLM Service**: Function definition, prompt building, response parsing
- **Function Executor**: Function execution, date parsing, argument validation
- **Phase II Client**: API calls, error handling, retry logic

### Integration Tests
- **Chat API Flow**: End-to-end message flow with mocked OpenAI
- **Function Calling**: LLM function calls trigger correct Phase II API calls
- **Session Management**: Session creation, retrieval, expiration

### Manual Testing Scenarios
1. Create todo: "Add a task to buy groceries tomorrow"
2. Query todos: "Show me all high priority tasks"
3. Update todo: "Mark the first one as complete"
4. Delete todo: "Delete all completed tasks" (with confirmation)
5. Multi-turn: "Show my tasks" → "Mark the second one complete"

**Detailed testing guide**: [quickstart.md](./quickstart.md#step-5-testing)

---

## Security Considerations

1. **Authentication**: All chat endpoints require valid JWT from Phase II
2. **Authorization**: Users can only access their own todos and sessions
3. **Input Validation**: Sanitize and validate all user input
4. **Rate Limiting**: Implement per-user rate limits (60 messages/hour)
5. **Prompt Injection**: Never expose system prompts to users
6. **Session Security**: Use secure UUIDs for session IDs
7. **API Keys**: Store OpenAI API key in environment variables

---

## Performance Optimization

### Backend
- Connection pooling for Phase II API calls
- Cache frequently accessed todos in conversation context
- Request queuing for OpenAI API
- Async/await for all I/O operations

### Frontend
- Debounce user input
- Optimistic UI updates
- React.memo for message components
- Incremental rendering of streaming responses

---

## Operational Readiness

### Monitoring
- Track OpenAI API latency and token usage
- Monitor Phase II API response times
- Log conversation errors and failures
- Track session creation and expiration rates

### Error Handling
- Graceful degradation when OpenAI API is unavailable
- User-friendly error messages for all failure modes
- Retry logic for transient failures
- Timeout handling for long-running operations

### Deployment
- Environment variables for configuration
- Health check endpoint
- Graceful shutdown for in-flight requests
- Session persistence strategy for production (Redis)

---

## Risk Analysis

### Risk 1: OpenAI Rate Limits
- **Impact**: Users blocked during high traffic
- **Probability**: Medium
- **Mitigation**: Request queuing, exponential backoff, rate limit messages

### Risk 2: Token Costs
- **Impact**: High operational costs
- **Probability**: Medium
- **Mitigation**: Use GPT-3.5-turbo, sliding window context, efficient prompts

### Risk 3: Context Loss
- **Impact**: Users confused in long conversations
- **Probability**: Low
- **Mitigation**: Store referenced todos, provide conversation reset

### Risk 4: Phase II API Changes
- **Impact**: Integration breaks
- **Probability**: Low
- **Mitigation**: Version API contracts, integration tests, monitor responses

---

## Success Metrics

### Functional Metrics
- 95% task creation accuracy from natural language
- 90% intent classification accuracy
- 95% query result accuracy

### Performance Metrics
- <1 second first token (p95)
- <3 seconds complete response (p95)
- 100 concurrent users supported

### User Experience Metrics
- 40% faster task creation vs. traditional UI
- 80% conversation naturalness rating
- 90% error recovery success rate

---

## Next Steps

1. **Generate Tasks**: Run `/sp.tasks` to create detailed implementation tasks
2. **Review Plan**: Ensure all stakeholders approve architecture and approach
3. **Begin Implementation**: Follow tasks.md with TDD approach
4. **Continuous Testing**: Verify each component against acceptance criteria

---

## Architectural Decision Records

📋 **Architectural decision detected**: Technology stack selection (OpenAI function calling, session-based storage, HTTP streaming, custom React components)

These decisions have long-term consequences, multiple alternatives were considered, and they influence the entire system design.

**Recommendation**: Document reasoning and tradeoffs? Run `/sp.adr ai-chatbot-technology-stack`

---

## References

- [Feature Specification](./spec.md)
- [Research Document](./research.md)
- [Data Model](./data-model.md)
- [API Contracts](./contracts/chat-api.yaml)
- [Quickstart Guide](./quickstart.md)
- [Constitution](./.specify/memory/constitution.md)
- [Phase II API Documentation](../../backend/README.md)
