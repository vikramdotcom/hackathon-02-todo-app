# Implementation Tasks: AI-Powered Todo Chatbot

**Feature**: 1-ai-chatbot
**Branch**: `1-ai-chatbot`
**Date**: 2026-01-22
**Status**: Ready for Implementation

---

## Overview

This document provides a complete, ordered list of implementation tasks for the AI-Powered Todo Chatbot feature. Tasks are organized by user story to enable independent implementation and testing of each capability.

**Task Format**: `- [ ] T### [P] [US#] Description with file path`
- **T###**: Sequential task ID
- **[P]**: Parallelizable (can run concurrently with other [P] tasks)
- **[US#]**: User Story number (US1, US2, etc.)
- **File path**: Exact location of code to create/modify

---

## Implementation Strategy

### MVP Scope (Recommended First Release)
- **Phase 1**: Setup
- **Phase 2**: Foundational Infrastructure
- **Phase 3**: US1 - Task Creation via Chat
- **Phase 4**: US2 - Task Queries via Chat
- **Phase 9**: Basic Polish (error handling, UI improvements)

This provides a working chatbot that can create and query tasks, demonstrating core value.

### Full Feature Scope
Complete all phases (US1-US6) for full conversational task management with context retention.

---

## Task Summary

| Phase | User Story | Task Count | Can Parallelize |
|-------|------------|------------|-----------------|
| Phase 1 | Setup | 8 | Yes (T002-T008) |
| Phase 2 | Foundational | 12 | Partial (T010-T015) |
| Phase 3 | US1 - Task Creation | 10 | Partial (T022-T026) |
| Phase 4 | US2 - Task Queries | 8 | Partial (T030-T034) |
| Phase 5 | US3 - Task Updates | 7 | Partial (T038-T042) |
| Phase 6 | US4 - Task Completion | 6 | Partial (T045-T048) |
| Phase 7 | US5 - Task Deletion | 8 | Partial (T051-T055) |
| Phase 8 | US6 - Multi-Turn Context | 9 | Partial (T059-T063) |
| Phase 9 | Polish & Cross-Cutting | 10 | Partial (T068-T074) |
| **Total** | | **78** | **~40% parallelizable** |

---

## Dependencies

### Story Completion Order

```
Phase 1 (Setup)
    ↓
Phase 2 (Foundational) ← BLOCKS ALL USER STORIES
    ↓
    ├─→ Phase 3 (US1: Task Creation) ← MVP PRIORITY
    ├─→ Phase 4 (US2: Task Queries) ← MVP PRIORITY
    ├─→ Phase 5 (US3: Task Updates)
    ├─→ Phase 6 (US4: Task Completion)
    ├─→ Phase 7 (US5: Task Deletion)
    └─→ Phase 8 (US6: Multi-Turn Context)
    ↓
Phase 9 (Polish) ← Depends on all user stories
```

**Key Dependencies**:
- Phase 2 must complete before any user story
- US1-US7 are independent and can be implemented in parallel after Phase 2
- US8 (Multi-Turn Context) enhances all other stories but doesn't block them
- Phase 9 should be done after core user stories are complete

---

## Phase 1: Setup

**Goal**: Initialize project structure, install dependencies, configure environment

**Independent Test**: Project builds successfully, all dependencies installed, environment variables configured

### Tasks

- [ ] T001 Create chat module directory structure in phase-3-ai-chatbot/backend/app/chat/
- [ ] T002 [P] Create chat models directory and __init__.py in phase-3-ai-chatbot/backend/app/chat/models/
- [ ] T003 [P] Create chat services directory and __init__.py in phase-3-ai-chatbot/backend/app/chat/services/
- [ ] T004 [P] Create chat API directory and __init__.py in phase-3-ai-chatbot/backend/app/chat/api/
- [ ] T005 [P] Create chat tests directory structure in phase-3-ai-chatbot/backend/tests/chat/
- [ ] T006 [P] Create requirements-chat.txt with OpenAI SDK, httpx, dateparser dependencies in phase-3-ai-chatbot/backend/
- [ ] T007 [P] Create frontend chat components directory in phase-3-ai-chatbot/frontend/src/components/chat/
- [ ] T008 [P] Create frontend chat types file in phase-3-ai-chatbot/frontend/src/types/chat.ts
- [ ] T009 Add OpenAI API key and chat configuration to .env file in phase-3-ai-chatbot/backend/

**Acceptance**: All directories exist, dependencies listed, environment template ready

---

## Phase 2: Foundational Infrastructure

**Goal**: Build core services that all user stories depend on

**Independent Test**:
- Conversation sessions can be created and retrieved
- Phase II API client can authenticate and make requests
- LLM service can call OpenAI API with function definitions
- Chat API endpoint accepts messages and returns responses

### Tasks

#### Data Models
- [ ] T010 [P] Implement ConversationSession model in phase-3-ai-chatbot/backend/app/chat/models/chat_models.py
- [ ] T011 [P] Implement ChatMessage model in phase-3-ai-chatbot/backend/app/chat/models/chat_models.py
- [ ] T012 [P] Implement ConversationContext model in phase-3-ai-chatbot/backend/app/chat/models/chat_models.py
- [ ] T013 [P] Implement MessageMetadata and PendingConfirmation models in phase-3-ai-chatbot/backend/app/chat/models/chat_models.py

#### Core Services
- [ ] T014 [P] Implement ConversationManager with session CRUD operations in phase-3-ai-chatbot/backend/app/chat/services/conversation_manager.py
- [ ] T015 [P] Implement Phase2Client with HTTP methods for todo API calls in phase-3-ai-chatbot/backend/app/chat/services/phase2_client.py
- [ ] T016 Implement LLMService with OpenAI API integration in phase-3-ai-chatbot/backend/app/chat/services/llm_service.py
- [ ] T017 Implement FunctionExecutor base class with function registry in phase-3-ai-chatbot/backend/app/chat/services/function_executor.py
- [ ] T018 Add session cleanup background task to ConversationManager in phase-3-ai-chatbot/backend/app/chat/services/conversation_manager.py

#### API Layer
- [ ] T019 Implement POST /api/v1/chat/message endpoint with streaming in phase-3-ai-chatbot/backend/app/chat/api/chat_routes.py
- [ ] T020 Implement GET /api/v1/chat/sessions/{session_id} endpoint in phase-3-ai-chatbot/backend/app/chat/api/chat_routes.py
- [ ] T021 Register chat routes in main FastAPI app in phase-3-ai-chatbot/backend/app/main.py

**Acceptance**:
- Can create session, send message, receive streaming response
- Phase II API client successfully calls existing endpoints
- LLM service connects to OpenAI and handles function calls

---

## Phase 3: US1 - Task Creation via Chat

**User Story**: As a user, I want to create todos through natural language so I can quickly add tasks without filling forms

**Functional Requirements**: FR-1 (Natural Language Task Creation)

**Independent Test**:
- User sends "Add a task to buy groceries tomorrow"
- System creates todo with title "buy groceries" and due date = tomorrow
- System confirms creation in chat
- Todo appears in Phase II database via API

### Tasks

#### Function Implementation
- [ ] T022 [P] [US1] Define create_todo function schema in LLMService in phase-3-ai-chatbot/backend/app/chat/services/llm_service.py
- [ ] T023 [P] [US1] Implement create_todo function executor in phase-3-ai-chatbot/backend/app/chat/services/function_executor.py
- [ ] T024 [P] [US1] Implement date parsing with dateparser in phase-3-ai-chatbot/backend/app/chat/services/function_executor.py
- [ ] T025 [P] [US1] Add create_todo method to Phase2Client in phase-3-ai-chatbot/backend/app/chat/services/phase2_client.py

#### System Prompt
- [ ] T026 [P] [US1] Add task creation examples to system prompt in phase-3-ai-chatbot/backend/app/chat/services/llm_service.py

#### Integration
- [ ] T027 [US1] Wire create_todo function to chat message handler in phase-3-ai-chatbot/backend/app/chat/api/chat_routes.py
- [ ] T028 [US1] Add task creation confirmation response formatting in phase-3-ai-chatbot/backend/app/chat/services/llm_service.py

#### Frontend
- [ ] T029 [P] [US1] Create TodoCard component to display created tasks in phase-3-ai-chatbot/frontend/src/components/chat/TodoCard.tsx
- [ ] T030 [P] [US1] Add todo card rendering to MessageBubble component in phase-3-ai-chatbot/frontend/src/components/chat/MessageBubble.tsx

#### Testing
- [ ] T031 [US1] Test task creation with various date formats ("tomorrow", "next Monday", "Jan 25")

**Acceptance**:
- ✅ User can create task with natural language
- ✅ System extracts title, due date, priority, tags
- ✅ Task appears in Phase II database
- ✅ User receives confirmation with task details
- ✅ Todo card displays in chat interface

---

## Phase 4: US2 - Task Queries via Chat

**User Story**: As a user, I want to query and filter my todos through natural language so I can quickly find specific tasks

**Functional Requirements**: FR-3 (Natural Language Task Queries)

**Independent Test**:
- User sends "Show me all high priority tasks"
- System retrieves todos with priority=high via Phase II API
- System displays results as todo cards in chat
- User sends "What tasks are due this week?"
- System correctly filters by date range

### Tasks

#### Function Implementation
- [ ] T032 [P] [US2] Define get_todos function schema with filter parameters in phase-3-ai-chatbot/backend/app/chat/services/llm_service.py
- [ ] T033 [P] [US2] Implement get_todos function executor with filtering in phase-3-ai-chatbot/backend/app/chat/services/function_executor.py
- [ ] T034 [P] [US2] Add get_todos method to Phase2Client in phase-3-ai-chatbot/backend/app/chat/services/phase2_client.py
- [ ] T035 [P] [US2] Implement date range parsing for queries in phase-3-ai-chatbot/backend/app/chat/services/function_executor.py

#### Response Formatting
- [ ] T036 [US2] Add query result formatting with counts and grouping in phase-3-ai-chatbot/backend/app/chat/services/llm_service.py
- [ ] T037 [US2] Implement empty result handling with helpful messages in phase-3-ai-chatbot/backend/app/chat/services/llm_service.py

#### Context Management
- [ ] T038 [US2] Store query results in ConversationContext.last_query_results in phase-3-ai-chatbot/backend/app/chat/services/conversation_manager.py
- [ ] T039 [US2] Cache referenced todos in ConversationContext for follow-up questions in phase-3-ai-chatbot/backend/app/chat/services/conversation_manager.py

**Acceptance**:
- ✅ User can query tasks by status, priority, due date, tags
- ✅ System correctly interprets date ranges ("this week", "next month")
- ✅ Results display as todo cards with count
- ✅ Empty results show helpful message
- ✅ Query results stored in context for follow-up

---

## Phase 5: US3 - Task Updates via Chat

**User Story**: As a user, I want to update task details through natural language so I can modify tasks without navigating to edit forms

**Functional Requirements**: FR-2 (Natural Language Task Updates)

**Independent Test**:
- User sends "Show my tasks" (creates context)
- User sends "Change the priority of the first one to high"
- System identifies task from context
- System updates task via Phase II API
- System confirms update

### Tasks

#### Function Implementation
- [ ] T040 [P] [US3] Define update_todo function schema in phase-3-ai-chatbot/backend/app/chat/services/llm_service.py
- [ ] T041 [P] [US3] Implement update_todo function executor in phase-3-ai-chatbot/backend/app/chat/services/function_executor.py
- [ ] T042 [P] [US3] Add update_todo method to Phase2Client in phase-3-ai-chatbot/backend/app/chat/services/phase2_client.py

#### Context Resolution
- [ ] T043 [US3] Implement task reference resolution ("the first one", "task #2") in phase-3-ai-chatbot/backend/app/chat/services/function_executor.py
- [ ] T044 [US3] Add ambiguity detection and clarification requests in phase-3-ai-chatbot/backend/app/chat/services/llm_service.py

#### Response
- [ ] T045 [US3] Add update confirmation with before/after details in phase-3-ai-chatbot/backend/app/chat/services/llm_service.py
- [ ] T046 [US3] Update referenced todos in context after modification in phase-3-ai-chatbot/backend/app/chat/services/conversation_manager.py

**Acceptance**:
- ✅ User can update title, due date, priority, tags, status
- ✅ System resolves task references from context
- ✅ System asks for clarification when reference is ambiguous
- ✅ System confirms what changed
- ✅ Partial updates work (only specified fields change)

---

## Phase 6: US4 - Task Completion via Chat

**User Story**: As a user, I want to mark tasks complete through natural language so I can quickly update task status

**Functional Requirements**: FR-5 (Task Completion Management)

**Independent Test**:
- User sends "Show incomplete tasks"
- User sends "Mark the first two as complete"
- System identifies both tasks from context
- System marks both complete via Phase II API
- System confirms completion

### Tasks

#### Function Implementation
- [ ] T047 [P] [US4] Define complete_todo function schema in phase-3-ai-chatbot/backend/app/chat/services/llm_service.py
- [ ] T048 [P] [US4] Implement complete_todo function executor in phase-3-ai-chatbot/backend/app/chat/services/function_executor.py
- [ ] T049 [P] [US4] Add complete_todo method to Phase2Client in phase-3-ai-chatbot/backend/app/chat/services/phase2_client.py

#### Bulk Operations
- [ ] T050 [US4] Implement bulk completion (multiple tasks at once) in phase-3-ai-chatbot/backend/app/chat/services/function_executor.py
- [ ] T051 [US4] Add completion confirmation with task list in phase-3-ai-chatbot/backend/app/chat/services/llm_service.py

#### Context Update
- [ ] T052 [US4] Update completed tasks in conversation context in phase-3-ai-chatbot/backend/app/chat/services/conversation_manager.py

**Acceptance**:
- ✅ User can mark single task complete
- ✅ User can mark multiple tasks complete at once
- ✅ System resolves task references ("the first one", "all of them")
- ✅ System confirms completion with task details
- ✅ Context reflects updated completion status

---

## Phase 7: US5 - Task Deletion via Chat

**User Story**: As a user, I want to delete tasks through natural language with confirmation so I can safely remove unwanted tasks

**Functional Requirements**: FR-4 (Natural Language Task Deletion)

**Independent Test**:
- User sends "Delete all completed tasks"
- System identifies matching tasks
- System asks "Delete 5 completed tasks?"
- User sends "Yes"
- System deletes tasks via Phase II API
- System confirms deletion count

### Tasks

#### Function Implementation
- [ ] T053 [P] [US5] Define delete_todo function schema in phase-3-ai-chatbot/backend/app/chat/services/llm_service.py
- [ ] T054 [P] [US5] Implement delete_todo function executor in phase-3-ai-chatbot/backend/app/chat/services/function_executor.py
- [ ] T055 [P] [US5] Add delete_todo method to Phase2Client in phase-3-ai-chatbot/backend/app/chat/services/phase2_client.py

#### Confirmation Flow
- [ ] T056 [US5] Implement PendingConfirmation creation for delete operations in phase-3-ai-chatbot/backend/app/chat/services/function_executor.py
- [ ] T057 [US5] Add confirmation request detection in LLMService in phase-3-ai-chatbot/backend/app/chat/services/llm_service.py
- [ ] T058 [US5] Implement confirmation response handling ("yes", "no", "cancel") in phase-3-ai-chatbot/backend/app/chat/services/function_executor.py
- [ ] T059 [US5] Add confirmation timeout (2 minutes) in phase-3-ai-chatbot/backend/app/chat/services/conversation_manager.py

#### Response
- [ ] T060 [US5] Add deletion confirmation with count in phase-3-ai-chatbot/backend/app/chat/services/llm_service.py

**Acceptance**:
- ✅ System requests confirmation before deleting
- ✅ User can confirm or cancel deletion
- ✅ Bulk deletion works with confirmation
- ✅ Confirmation expires after 2 minutes
- ✅ System confirms deletion count
- ✅ Deleted tasks removed from context

---

## Phase 8: US6 - Multi-Turn Context Management

**User Story**: As a user, I want the system to remember our conversation so I can reference previous messages without repeating information

**Functional Requirements**: FR-6 (Multi-Turn Context Management)

**Independent Test**:
- User sends "Show high priority tasks" (message 1)
- User sends "Mark the first one complete" (message 2 - references message 1)
- User sends "What's the due date?" (message 3 - references task from message 1)
- System maintains context across all 3 messages
- System correctly resolves references

### Tasks

#### Context Storage
- [ ] T061 [P] [US6] Implement sliding window message history (max 20 messages) in phase-3-ai-chatbot/backend/app/chat/services/conversation_manager.py
- [ ] T062 [P] [US6] Add referenced todo tracking with timestamps in phase-3-ai-chatbot/backend/app/chat/models/chat_models.py
- [ ] T063 [P] [US6] Implement context pruning for old references (>10 minutes) in phase-3-ai-chatbot/backend/app/chat/services/conversation_manager.py

#### Context Resolution
- [ ] T064 [US6] Implement pronoun resolution ("it", "that task", "those") in phase-3-ai-chatbot/backend/app/chat/services/function_executor.py
- [ ] T065 [US6] Implement ordinal resolution ("the first one", "the second task") in phase-3-ai-chatbot/backend/app/chat/services/function_executor.py
- [ ] T066 [US6] Add context loss detection and clarification requests in phase-3-ai-chatbot/backend/app/chat/services/llm_service.py

#### System Prompt Enhancement
- [ ] T067 [US6] Add recent context summary to system prompt in phase-3-ai-chatbot/backend/app/chat/services/llm_service.py
- [ ] T068 [US6] Include last query results in system prompt in phase-3-ai-chatbot/backend/app/chat/services/llm_service.py

#### Testing
- [ ] T069 [US6] Test 10+ turn conversations with context retention

**Acceptance**:
- ✅ System maintains context for 10+ message turns
- ✅ System resolves references to previous messages
- ✅ System tracks recently discussed tasks
- ✅ System asks for clarification when context is unclear
- ✅ Context pruning prevents memory bloat

---

## Phase 9: Polish & Cross-Cutting Concerns

**Goal**: Enhance user experience, error handling, and production readiness

**Independent Test**:
- All error scenarios show user-friendly messages
- UI is polished and responsive
- System handles edge cases gracefully
- Performance meets targets (<2s response time)

### Tasks

#### Error Handling
- [ ] T070 [P] Implement comprehensive error handling in Phase2Client in phase-3-ai-chatbot/backend/app/chat/services/phase2_client.py
- [ ] T071 [P] Add user-friendly error message translation in phase-3-ai-chatbot/backend/app/chat/services/llm_service.py
- [ ] T072 [P] Implement retry logic for transient failures in phase-3-ai-chatbot/backend/app/chat/services/phase2_client.py
- [ ] T073 [P] Add OpenAI API error handling and fallbacks in phase-3-ai-chatbot/backend/app/chat/services/llm_service.py

#### Frontend Polish
- [ ] T074 [P] Implement ChatInterface component with message list in phase-3-ai-chatbot/frontend/src/components/chat/ChatInterface.tsx
- [ ] T075 [P] Implement MessageList component with auto-scroll in phase-3-ai-chatbot/frontend/src/components/chat/MessageList.tsx
- [ ] T076 [P] Implement MessageBubble component with role styling in phase-3-ai-chatbot/frontend/src/components/chat/MessageBubble.tsx
- [ ] T077 [P] Implement InputBox component with send button in phase-3-ai-chatbot/frontend/src/components/chat/InputBox.tsx
- [ ] T078 [P] Add typing indicator component in phase-3-ai-chatbot/frontend/src/components/chat/TypingIndicator.tsx
- [ ] T079 [P] Create chat page at /chat route in phase-3-ai-chatbot/frontend/src/app/chat/page.tsx

#### Performance & Monitoring
- [ ] T080 Add request logging and metrics in phase-3-ai-chatbot/backend/app/chat/api/chat_routes.py
- [ ] T081 Implement token usage tracking in phase-3-ai-chatbot/backend/app/chat/services/llm_service.py
- [ ] T082 Add session metrics (creation rate, expiration rate) in phase-3-ai-chatbot/backend/app/chat/services/conversation_manager.py

#### Documentation
- [ ] T083 Add inline code documentation and docstrings across all chat modules
- [ ] T084 Create deployment guide for chat feature in phase-3-ai-chatbot/backend/CHAT_DEPLOYMENT.md

**Acceptance**:
- ✅ All error scenarios handled gracefully
- ✅ UI is polished and responsive
- ✅ Performance meets targets
- ✅ Logging and monitoring in place
- ✅ Code is well-documented

---

## Parallel Execution Examples

### Phase 1 (Setup) - All Parallel
```bash
# All T002-T008 can run simultaneously
T002, T003, T004, T005, T006, T007, T008
```

### Phase 2 (Foundational) - Partial Parallel
```bash
# Round 1: Data models (all parallel)
T010, T011, T012, T013

# Round 2: Services (all parallel, depend on models)
T014, T015, T016, T017

# Round 3: API layer (sequential, depends on services)
T018 → T019 → T020 → T021
```

### Phase 3 (US1) - Partial Parallel
```bash
# Round 1: Function definitions (all parallel)
T022, T023, T024, T025, T026

# Round 2: Integration (sequential)
T027 → T028

# Round 3: Frontend (parallel)
T029, T030

# Round 4: Testing
T031
```

### Phases 3-8 (User Stories) - Fully Parallel
```bash
# After Phase 2 completes, all user stories can proceed in parallel:
Phase 3 (US1) || Phase 4 (US2) || Phase 5 (US3) || Phase 6 (US4) || Phase 7 (US5) || Phase 8 (US6)
```

---

## Testing Strategy

### Unit Tests (Per Phase)
- **Phase 2**: Test each service in isolation with mocks
  - ConversationManager: Session CRUD, cleanup
  - Phase2Client: HTTP calls, error handling
  - LLMService: OpenAI integration, function calling
  - FunctionExecutor: Function execution, date parsing

- **Phase 3-8**: Test each function executor
  - Input validation
  - API call construction
  - Response formatting
  - Error handling

### Integration Tests (Per User Story)
- **US1**: End-to-end task creation flow
- **US2**: End-to-end query flow with filtering
- **US3**: End-to-end update flow with context
- **US4**: End-to-end completion flow
- **US5**: End-to-end deletion flow with confirmation
- **US6**: Multi-turn conversation flow

### Manual Testing Scenarios
1. "Add a task to buy groceries tomorrow at 3pm"
2. "Show me all high priority tasks"
3. "Mark the first one as complete"
4. "Delete all completed tasks" → "Yes"
5. "What tasks are due this week?"

---

## Success Metrics

### Functional Metrics (from spec.md)
- 95% task creation accuracy
- 90% intent classification accuracy
- 95% query result accuracy
- 90% of responses within 2 seconds

### Implementation Metrics
- All 78 tasks completed
- All unit tests passing
- All integration tests passing
- All manual test scenarios working
- Zero Phase II code modifications
- 100% API-only todo operations

---

## Notes

- **Task IDs are sequential**: T001-T084 in execution order
- **[P] marker**: Indicates task can run in parallel with other [P] tasks
- **[US#] label**: Maps task to user story for traceability
- **File paths**: Exact locations provided for each task
- **Dependencies**: Clearly marked in phase descriptions
- **MVP scope**: Phases 1-4 + 9 provide minimum viable chatbot
- **Full scope**: All phases provide complete conversational task management

---

## References

- [Feature Specification](./spec.md)
- [Implementation Plan](./plan.md)
- [Research Document](./research.md)
- [Data Model](./data-model.md)
- [API Contracts](./contracts/chat-api.yaml)
- [Quickstart Guide](./quickstart.md)
