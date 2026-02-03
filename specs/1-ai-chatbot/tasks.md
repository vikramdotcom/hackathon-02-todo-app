# Tasks: AI-Powered Todo Chatbot

**Feature**: 1-ai-chatbot
**Input**: Design documents from `/specs/1-ai-chatbot/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/chat-api.yaml, quickstart.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

**Tests**: Not explicitly requested in specification - tests are omitted per template guidelines.

---

## Format: `- [ ] [ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4, US5)
- All paths are relative to `phase-3-ai-chatbot/` directory

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure for chat feature

- [X] T001 Create backend chat module directory structure: `backend/app/chat/` with subdirectories `models/`, `services/`, `api/`
- [X] T002 Create `backend/app/chat/__init__.py` and subdirectory `__init__.py` files
- [X] T003 [P] Create `backend/requirements-chat.txt` with dependencies: openai==1.12.0, httpx==0.26.0, dateparser==1.2.0, python-dotenv==1.0.0
- [X] T004 [P] Add chat configuration to `backend/.env`: OPENAI_API_KEY, OPENAI_MODEL, OPENAI_MAX_TOKENS, OPENAI_TEMPERATURE, PHASE2_API_BASE_URL, CHAT_SESSION_TIMEOUT_MINUTES, CHAT_MAX_MESSAGES_PER_SESSION, CHAT_MAX_CONTEXT_TURNS
- [X] T005 [P] Update `backend/app/core/config.py` to include chat configuration settings (OpenAI, Phase II API URL, chat limits)
- [X] T006 [P] Create frontend chat directory structure: `frontend/src/app/chat/`, `frontend/src/components/chat/`, `frontend/src/lib/`, `frontend/src/types/`
- [X] T007 [P] Create `frontend/src/types/chat.ts` with TypeScript interfaces for Message, ConversationSession, ChatMessageRequest, ChatMessageResponse

**Checkpoint**: Directory structure and configuration ready

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T008 Create data models in `backend/app/chat/models/chat_models.py`: ConversationSession, ChatMessage, MessageMetadata, ConversationContext, TodoReference, PendingConfirmation classes
- [X] T009 Implement Phase II API client in `backend/app/chat/services/phase2_client.py` with async methods: get_todos(), create_todo(), update_todo(), delete_todo(), complete_todo() using httpx.AsyncClient
- [X] T010 Add error handling and retry logic to Phase II API client for transient failures
- [X] T011 Implement conversation manager in `backend/app/chat/services/conversation_manager.py` with in-memory session storage (Dict), methods: create_session(), get_session(), add_message(), update_context(), cleanup_expired_sessions()
- [X] T012 Add background cleanup task to conversation manager for expired sessions (runs every 5 minutes)
- [X] T013 Implement singleton pattern for conversation manager with init_conversation_manager() and get_conversation_manager() functions
- [X] T014 Register chat routes in `backend/app/main.py`: import chat_routes and include_router with prefix `/api/v1/chat`
- [X] T015 Update CORS configuration in `backend/app/main.py` to allow chat endpoints

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Basic Chat with Task Creation (Priority: P0) 🎯 MVP

**Goal**: Users can open chat interface and create todos through natural language

**Independent Test**: User sends "Add a task to buy groceries tomorrow" and todo is created in Phase II database with correct title and due date

### Implementation for User Story 1

- [X] T016 [P] [US1] Implement LLM service in `backend/app/chat/services/llm_service.py` with OpenAI AsyncClient initialization, _build_system_prompt() method, and _define_functions() method for create_todo function
- [X] T017 [P] [US1] Add streaming response generation to LLM service: generate_response() method that yields tokens from OpenAI streaming API
- [X] T018 [P] [US1] Implement function executor in `backend/app/chat/services/function_executor.py` with execute_function() method, _parse_date() using dateparser, and _validate_arguments() for create_todo
- [X] T019 [US1] Create chat API endpoint in `backend/app/chat/api/chat_routes.py`: POST /chat/message with request model ChatMessageRequest (session_id, message)
- [X] T020 [US1] Implement streaming response handler in chat_routes.py that processes LLM tokens and function calls, returns StreamingResponse with Server-Sent Events format
- [X] T021 [US1] Add JWT authentication dependency to chat endpoint using get_current_user from `backend/app/api/deps.py`
- [X] T022 [US1] Implement session management in chat endpoint: create or retrieve session, add user message, return session_id in X-Session-Id header
- [X] T023 [P] [US1] Create chat page in `frontend/src/app/chat/page.tsx` with basic layout and ChatInterface component
- [X] T024 [P] [US1] Implement ChatInterface component in `frontend/src/components/chat/ChatInterface.tsx` with state management (messages, sessionId, isLoading)
- [X] T025 [P] [US1] Create MessageList component in `frontend/src/components/chat/MessageList.tsx` to display conversation history
- [X] T026 [P] [US1] Create MessageBubble component in `frontend/src/components/chat/MessageBubble.tsx` with styling for user/assistant messages
- [X] T027 [P] [US1] Create InputBox component in `frontend/src/components/chat/InputBox.tsx` with text input and send button
- [X] T028 [US1] Implement chat API client in `frontend/src/lib/chat-api.ts` with sendMessage() function using Fetch API with streaming response handling
- [X] T029 [US1] Connect InputBox to chat API client: handle message submission, update messages state, store session_id in localStorage
- [X] T030 [US1] Implement streaming response parsing in ChatInterface: read ReadableStream, parse SSE data, update UI incrementally as tokens arrive
- [X] T031 [US1] Add loading indicator to ChatInterface while waiting for first token

**Checkpoint**: User Story 1 complete - users can chat and create todos through natural language

---

## Phase 4: User Story 2 - Task Queries and Multi-Turn Context (Priority: P0)

**Goal**: Users can query/filter todos and system maintains context across multiple messages

**Independent Test**: User sends "Show me all high priority tasks" then "Mark the first one as complete" - system correctly identifies which task to mark complete

### Implementation for User Story 2

- [X] T032 [P] [US2] Add get_todos function definition to LLM service with parameters: completed (boolean), priority (string), tags (array), search (string), due_date_range (object)
- [X] T033 [P] [US2] Implement get_todos execution in function executor: call Phase II API with filters, format results for LLM
- [X] T034 [US2] Update conversation context management: store last_query_results (list of todo IDs) and referenced_todos (dict of TodoReference objects)
- [X] T035 [US2] Implement context resolution in function executor: resolve references like "the first one", "that task", "those" using last_query_results
- [X] T036 [US2] Add sliding window context management to conversation manager: maintain last 10 message pairs (20 messages total), prune older messages
- [X] T037 [US2] Update system prompt builder to include recent todo context from conversation state
- [X] T038 [P] [US2] Create TodoCard component in `frontend/src/components/chat/TodoCard.tsx` to display todo details (title, due date, priority, status, tags)
- [X] T039 [US2] Update MessageBubble component to detect and render TodoCard components when assistant message contains todo data
- [X] T040 [US2] Add todo list formatting to LLM responses: display multiple todos as cards in chat interface
- [X] T041 [US2] Implement conversation reset option in ChatInterface: "Start new conversation" button that clears session_id and messages

**Checkpoint**: User Story 2 complete - users can query todos and system maintains multi-turn context

---

## Phase 5: User Story 3 - Task Updates and Completion (Priority: P0)

**Goal**: Users can update todo details and mark tasks complete through natural language

**Independent Test**: User sends "Update the priority of task 'buy groceries' to high" and todo is updated in Phase II database

### Implementation for User Story 3

- [X] T042 [P] [US3] Add update_todo function definition to LLM service with parameters: todo_id (integer), title (string), description (string), priority (string), due_date (string), tags (array)
- [X] T043 [P] [US3] Add complete_todo function definition to LLM service with parameters: todo_id (integer) or todo_ids (array)
- [X] T044 [P] [US3] Implement update_todo execution in function executor: validate arguments, call Phase II PUT /api/v1/todos/{id} endpoint
- [X] T045 [P] [US3] Implement complete_todo execution in function executor: handle single and bulk completion, call Phase II PATCH /api/v1/todos/{id}/complete endpoint
- [X] T046 [US3] Add partial update support to function executor: only send changed fields to Phase II API
- [X] T047 [US3] Implement todo reference resolution for updates: allow "update the first one" to resolve to specific todo_id from context
- [X] T048 [US3] Add confirmation messages to LLM responses for successful updates and completions
- [X] T049 [US3] Update TodoCard component to show visual indication when todo is marked complete (strikethrough, checkmark)

**Checkpoint**: User Story 3 complete - users can update and complete todos through chat

---

## Phase 6: User Story 4 - Task Deletion with Confirmation (Priority: P0)

**Goal**: Users can delete todos with required confirmation for destructive operations

**Independent Test**: User sends "Delete all completed tasks", system asks for confirmation, user confirms, tasks are deleted

### Implementation for User Story 4

- [X] T050 [P] [US4] Add delete_todo function definition to LLM service with parameters: todo_id (integer) or todo_ids (array), confirmed (boolean)
- [X] T051 [US4] Implement PendingConfirmation tracking in conversation context: store operation type, target_todo_ids, created_at, expires_at (2 minutes)
- [X] T052 [US4] Implement delete_todo execution in function executor: if not confirmed, create PendingConfirmation and ask for confirmation; if confirmed, check pending confirmation and execute deletion
- [X] T053 [US4] Add confirmation timeout handling: expire pending confirmations after 2 minutes, clear from context
- [X] T054 [US4] Implement confirmation detection in LLM service: recognize "yes", "confirm", "delete them" as confirmation responses
- [X] T055 [US4] Add bulk deletion support: handle "delete all completed tasks", "delete tasks tagged urgent" with confirmation
- [X] T056 [US4] Update system prompt to include confirmation workflow guidance for destructive operations
- [X] T057 [US4] Add confirmation UI in ChatInterface: highlight confirmation requests with distinct styling

**Checkpoint**: User Story 4 complete - users can safely delete todos with confirmation

---

## Phase 7: User Story 5 - Bulk Operations and Smart Suggestions (Priority: P1)

**Goal**: Users can perform bulk operations and receive smart suggestions about their tasks

**Independent Test**: User sends "What should I focus on today?" and receives prioritized recommendations based on due dates and priorities

### Implementation for User Story 5

- [ ] T058 [P] [US5] Add bulk_update_todo function definition to LLM service with parameters: todo_ids (array), updates (object), confirmed (boolean)
- [ ] T059 [P] [US5] Add get_suggestions function definition to LLM service with parameters: context (string) - analyzes overdue, high priority, due today tasks
- [ ] T060 [US5] Implement bulk_update_todo execution in function executor: require confirmation for bulk updates, execute updates in batch
- [ ] T061 [US5] Implement get_suggestions execution in function executor: query Phase II API for user's todos, analyze patterns, return prioritized recommendations
- [X] T062 [US5] Add smart date parsing to function executor: handle "tomorrow", "next Monday", "in 3 days", "Jan 25" using dateparser library
- [ ] T063 [US5] Implement suggestion formatting in LLM responses: present recommendations with reasoning and actionable next steps
- [ ] T064 [US5] Add bulk operation confirmation to PendingConfirmation: track bulk_update operations with affected todo IDs
- [ ] T065 [US5] Update system prompt to include smart suggestion capabilities and bulk operation guidance

**Checkpoint**: User Story 5 complete - users can perform bulk operations and get smart suggestions

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and production readiness

- [ ] T066 [P] Add comprehensive error handling to chat_routes.py: catch OpenAI API errors, Phase II API errors, validation errors, return user-friendly messages
- [ ] T067 [P] Implement rate limiting in chat endpoint: max 60 messages per user per hour using user_id from JWT
- [X] T068 [P] Add input validation to chat endpoint: max message length 10,000 characters, sanitize user input
- [X] T069 [P] Add logging to all chat services: log session creation, function calls, API errors, token usage for monitoring
- [X] T070 [P] Implement graceful degradation when OpenAI API is unavailable: return helpful error message, suggest retry
- [X] T071 [P] Add typing indicator to ChatInterface: show "Assistant is thinking..." while waiting for response
- [X] T072 [P] Add message timestamps to MessageBubble component
- [ ] T073 [P] Implement error message display in ChatInterface: show user-friendly errors for API failures, network issues
- [X] T074 [P] Add session persistence: store session_id in localStorage, restore conversation on page refresh
- [ ] T075 [P] Implement conversation history display: show message count, session duration in ChatInterface
- [ ] T076 [P] Add accessibility features to chat components: ARIA labels, keyboard navigation, screen reader support
- [ ] T077 [P] Optimize frontend performance: React.memo for MessageBubble, debounce input, lazy load message history
- [ ] T078 [P] Add connection pooling to Phase II API client for better performance
- [ ] T079 [P] Implement request queuing for OpenAI API to handle rate limits gracefully
- [X] T080 [P] Add health check endpoint to chat API: GET /api/v1/chat/health returns service status
- [X] T081 [P] Create README.md in `backend/app/chat/` documenting chat feature architecture and setup
- [ ] T082 [P] Update main project README.md with Phase III chat feature documentation
- [ ] T083 Validate implementation against quickstart.md: verify all manual testing scenarios work correctly
- [ ] T084 Run end-to-end validation: test all user scenarios from spec.md (task creation, queries, updates, deletion, bulk operations, suggestions)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - User stories can proceed in parallel (if staffed)
  - Or sequentially in priority order (US1 → US2 → US3 → US4 → US5)
- **Polish (Phase 8)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (US1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (US2)**: Can start after Foundational (Phase 2) - Builds on US1 but independently testable
- **User Story 3 (US3)**: Can start after Foundational (Phase 2) - Uses context from US2 but independently testable
- **User Story 4 (US4)**: Can start after Foundational (Phase 2) - Uses confirmation pattern, independently testable
- **User Story 5 (US5)**: Can start after Foundational (Phase 2) - Extends US3/US4 patterns, independently testable

### Within Each User Story

- Backend services before API endpoints
- API endpoints before frontend components
- Frontend components before integration
- Core implementation before polish
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel (T003, T004, T005, T006, T007)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- Within each user story, tasks marked [P] can run in parallel:
  - US1: T016, T017, T018 (backend services) and T023, T024, T025, T026, T027 (frontend components)
  - US2: T032, T033 (backend) and T038 (frontend)
  - US3: T042, T043, T044, T045 (backend functions)
  - US4: T050 (backend function)
  - US5: T058, T059 (backend functions)
  - Phase 8: Most polish tasks (T066-T082) can run in parallel

---

## Parallel Example: User Story 1

```bash
# Backend services can be built in parallel:
Task T016: "Implement LLM service in backend/app/chat/services/llm_service.py"
Task T017: "Add streaming response generation to LLM service"
Task T018: "Implement function executor in backend/app/chat/services/function_executor.py"

# Frontend components can be built in parallel:
Task T023: "Create chat page in frontend/src/app/chat/page.tsx"
Task T024: "Implement ChatInterface component"
Task T025: "Create MessageList component"
Task T026: "Create MessageBubble component"
Task T027: "Create InputBox component"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T007)
2. Complete Phase 2: Foundational (T008-T015) - CRITICAL
3. Complete Phase 3: User Story 1 (T016-T031)
4. **STOP and VALIDATE**: Test basic chat and task creation independently
5. Deploy/demo if ready

**MVP Deliverable**: Users can chat with AI assistant and create todos through natural language

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo (queries + context)
4. Add User Story 3 → Test independently → Deploy/Demo (updates + completion)
5. Add User Story 4 → Test independently → Deploy/Demo (deletion + confirmation)
6. Add User Story 5 → Test independently → Deploy/Demo (bulk ops + suggestions)
7. Add Polish → Final production release

Each story adds value without breaking previous stories.

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001-T015)
2. Once Foundational is done:
   - Developer A: User Story 1 (T016-T031)
   - Developer B: User Story 2 (T032-T041)
   - Developer C: User Story 3 (T042-T049)
3. Stories complete and integrate independently
4. Continue with US4, US5, and Polish

---

## Success Metrics

### Functional Metrics (from spec.md)

- 95% task creation accuracy from natural language
- 90% intent classification accuracy
- 95% query result accuracy
- System maintains context for 10+ message turns

### Performance Metrics (from spec.md)

- <1 second first token (p95)
- <3 seconds complete response (p95)
- 100 concurrent users supported
- 1000+ messages per minute

### User Experience Metrics (from spec.md)

- 40% faster task creation vs. traditional UI
- 80% conversation naturalness rating
- 90% error recovery success rate

---

## Notes

- [P] tasks = different files, no dependencies, can run in parallel
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- All paths relative to `phase-3-ai-chatbot/` directory
- Backend uses Python 3.11+ with FastAPI
- Frontend uses TypeScript with Next.js 14+
- No Phase II code modifications - all integration via APIs
- Session storage is in-memory for MVP (can upgrade to Redis for production)
- OpenAI API key required in environment variables
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Tests not included per spec (not explicitly requested)
