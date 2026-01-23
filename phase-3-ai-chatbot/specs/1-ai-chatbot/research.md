# Research: AI-Powered Todo Chatbot

**Feature**: 1-ai-chatbot
**Date**: 2026-01-22
**Phase**: 0 - Technical Research

---

## Overview

This document captures research findings and technology decisions for implementing the AI-Powered Todo Chatbot feature. All decisions are based on the constraints that we cannot modify Phase II code and must use existing APIs.

---

## Research Questions & Decisions

### 1. Large Language Model (LLM) Service

**Question**: Which LLM service should we use for natural language understanding, intent classification, and entity extraction?

**Options Considered**:
1. **OpenAI API (GPT-4/GPT-3.5-turbo)**
   - Pros: Excellent NLU capabilities, function calling support, well-documented
   - Cons: Cost per request, rate limits, external dependency

2. **Anthropic Claude API**
   - Pros: Strong reasoning, tool use capabilities, longer context windows
   - Cons: Cost, external dependency

3. **Local LLM (Ollama/LLaMA)**
   - Pros: No API costs, data privacy, no rate limits
   - Cons: Requires GPU resources, slower inference, setup complexity

**Decision**: **OpenAI API (GPT-4 or GPT-3.5-turbo)**

**Rationale**:
- Function calling feature maps perfectly to our todo operations (create, read, update, delete)
- Proven track record for intent classification and entity extraction
- Extensive documentation and community support
- Can start with GPT-3.5-turbo for cost optimization, upgrade to GPT-4 if needed
- Acceptable latency for chat use case (1-3 seconds)

**Implementation Notes**:
- Use OpenAI Python SDK (`openai` package)
- Implement function calling for todo operations
- Define functions that map to Phase II API endpoints
- Use system prompts to guide behavior and maintain context

---

### 2. Agent Orchestration Framework

**Question**: How should we orchestrate multi-turn conversations and tool calling?

**Options Considered**:
1. **LangChain**
   - Pros: Comprehensive framework, agent abstractions, memory management
   - Cons: Heavy dependency, learning curve, potential over-engineering

2. **Custom Implementation with OpenAI Function Calling**
   - Pros: Lightweight, full control, minimal dependencies
   - Cons: Need to implement conversation management manually

3. **Semantic Kernel**
   - Pros: Microsoft-backed, good abstractions
   - Cons: Less mature, smaller community

**Decision**: **Custom Implementation with OpenAI Function Calling**

**Rationale**:
- Our use case is focused: map natural language to existing API calls
- OpenAI's function calling provides the core orchestration we need
- Avoid over-engineering with a heavy framework
- Easier to maintain and debug
- Aligns with constitution principle: "Prefer small, testable changes"

**Implementation Notes**:
- Create a conversation manager class to handle message history
- Define functions for each todo operation (create_todo, get_todos, update_todo, etc.)
- Implement function execution layer that calls Phase II APIs
- Handle multi-turn context by maintaining conversation history

---

### 3. Chat UI Framework

**Question**: What should we use for the conversational interface?

**Options Considered**:
1. **Custom React Components**
   - Pros: Full control, lightweight, matches existing Next.js stack
   - Cons: Need to build from scratch

2. **ChatUI Libraries (react-chat-elements, react-chat-widget)**
   - Pros: Pre-built components, faster development
   - Cons: Customization limitations, additional dependencies

3. **Vercel AI SDK UI Components**
   - Pros: Designed for AI chat, streaming support, React integration
   - Cons: Relatively new, tied to Vercel ecosystem

**Decision**: **Custom React Components**

**Rationale**:
- Phase II already uses Next.js and React
- Chat interface requirements are straightforward (message list, input box, typing indicator)
- Full control over styling to match existing UI
- No additional heavy dependencies
- Can reuse existing Phase II components and styling patterns

**Implementation Notes**:
- Create ChatInterface component with message history
- Create MessageBubble component for user/assistant messages
- Create TodoCard component to display todos inline
- Use existing Phase II styling (Tailwind CSS if present, or CSS modules)
- Implement real-time updates with React state management

---

### 4. Real-Time Communication Protocol

**Question**: How should we handle bidirectional communication between frontend and backend?

**Options Considered**:
1. **WebSockets**
   - Pros: True bidirectional, low latency, persistent connection
   - Cons: More complex server setup, connection management overhead

2. **Server-Sent Events (SSE)**
   - Pros: Simpler than WebSockets, good for streaming responses
   - Cons: Unidirectional (server to client only)

3. **HTTP Polling**
   - Pros: Simple, works everywhere
   - Cons: Inefficient, higher latency

4. **HTTP Streaming (Fetch API with ReadableStream)**
   - Pros: Simple, supports streaming LLM responses, no special server setup
   - Cons: Unidirectional for streaming, but can use regular POST for user messages

**Decision**: **HTTP Streaming with Fetch API**

**Rationale**:
- User sends message via POST request
- Server streams LLM response back using Server-Sent Events or chunked transfer encoding
- Simpler than WebSockets for this use case
- Works well with OpenAI's streaming API
- No need for persistent connection management
- Aligns with REST API patterns already in use

**Implementation Notes**:
- Frontend: POST user message to `/api/v1/chat/message`
- Backend: Stream response using FastAPI's StreamingResponse
- Use OpenAI's streaming API to get tokens as they're generated
- Display typing indicator while waiting for first token
- Render response incrementally as tokens arrive

---

### 5. Conversation History Storage

**Question**: Should conversation history persist across user sessions, or be session-based only?

**Clarification from Spec**: [NEEDS CLARIFICATION: Should conversation history persist across user sessions (e.g., user logs out and back in), or should each session start fresh?]

**Options Considered**:
1. **Session-Based (In-Memory)**
   - Pros: Simple, no database changes, privacy-friendly
   - Cons: Lost on logout/refresh, can't review past conversations

2. **Persistent (Database Storage)**
   - Pros: Users can review history, better UX, enables analytics
   - Cons: Requires new database tables, storage costs, privacy concerns

**Decision**: **Session-Based (In-Memory) for MVP**

**Rationale**:
- Aligns with constraint: "Cannot modify existing Phase II database schemas"
- Simpler implementation for initial release
- Reduces privacy concerns (no long-term storage of conversations)
- Can be enhanced later with separate conversation database if needed
- Session storage can use Redis or in-memory dict for multi-instance deployments

**Implementation Notes**:
- Store conversation history in backend memory (Python dict keyed by session_id)
- Generate session_id on first message (UUID)
- Client stores session_id in localStorage or sessionStorage
- Conversation expires after 30 minutes of inactivity
- For production: use Redis for session storage to support multiple backend instances

**Future Enhancement Path**:
- Phase 3.1 could add conversation persistence with new tables:
  - `conversations` table (id, user_id, created_at, last_message_at)
  - `messages` table (id, conversation_id, role, content, timestamp)

---

### 6. Context Management Strategy

**Question**: How do we maintain conversation context for multi-turn interactions?

**Options Considered**:
1. **Full History (All Messages)**
   - Pros: Complete context, best for complex conversations
   - Cons: Token costs grow linearly, may hit context limits

2. **Sliding Window (Last N Messages)**
   - Pros: Bounded token usage, works for most conversations
   - Cons: May lose important context from earlier messages

3. **Summarization (Compress Old Messages)**
   - Pros: Maintains key context, bounded tokens
   - Cons: Complex to implement, may lose details

**Decision**: **Sliding Window (Last 10 Messages) with Smart Truncation**

**Rationale**:
- Spec requires "at least 10 message turns" of context
- Most todo conversations are short (5-20 messages per spec assumption)
- Sliding window keeps token costs predictable
- Can include system message with recent todo context (last query results)

**Implementation Notes**:
- Maintain last 10 user/assistant message pairs (20 messages total)
- Always include system prompt with:
  - User context (user_id, username)
  - Available functions (todo operations)
  - Recently referenced todos (from last query)
- If conversation exceeds 10 turns, offer "start fresh" option
- Track referenced todo IDs separately for context resolution

---

### 7. Intent Classification & Entity Extraction

**Question**: Should we use a separate NLU service or rely on LLM function calling?

**Options Considered**:
1. **Separate NLU Service (Rasa, Dialogflow)**
   - Pros: Specialized for intent/entity extraction, potentially faster
   - Cons: Additional service to maintain, training data required

2. **LLM Function Calling**
   - Pros: No separate service, leverages LLM's understanding, no training needed
   - Cons: Slightly higher latency, token costs

**Decision**: **LLM Function Calling**

**Rationale**:
- OpenAI's function calling handles intent classification implicitly
- LLM can extract entities (dates, priorities, tags) from natural language
- No need to maintain separate NLU training data
- Simpler architecture with fewer moving parts
- Can handle complex, ambiguous requests better than rule-based NLU

**Implementation Notes**:
- Define functions with detailed descriptions and parameters
- Use JSON Schema for parameter validation
- LLM will choose appropriate function based on user intent
- Extract entities through function parameters (title, due_date, priority, etc.)
- Handle ambiguity by having LLM ask clarifying questions

---

### 8. Date/Time Parsing

**Question**: How should we parse natural language dates ("tomorrow", "next Monday", etc.)?

**Options Considered**:
1. **LLM Extraction**
   - Pros: Handles complex expressions, no separate library
   - Cons: May be inconsistent, timezone handling unclear

2. **dateparser Library**
   - Pros: Robust, handles many formats, timezone-aware
   - Cons: Additional dependency

3. **Hybrid (LLM + dateparser)**
   - Pros: Best of both worlds, LLM extracts, dateparser normalizes
   - Cons: Slightly more complex

**Decision**: **Hybrid Approach (LLM + dateparser)**

**Rationale**:
- LLM extracts date expressions from natural language
- dateparser library normalizes to ISO 8601 format
- Handles timezone conversion properly
- Validates that extracted dates are reasonable

**Implementation Notes**:
- LLM function parameter: `due_date` (string, natural language)
- Backend uses `dateparser.parse()` to convert to datetime
- Use user's timezone (from browser or default to UTC)
- Validate parsed dates (reject dates in far past, warn for past dates)

---

### 9. Error Handling & Confirmation

**Question**: How should we handle destructive operations and API errors?

**Decision**: **Two-Step Confirmation for Destructive Operations**

**Rationale**:
- Spec requires: "System must request confirmation before deleting tasks"
- Prevents accidental data loss
- Builds user trust

**Implementation Notes**:
- For delete operations: LLM responds with confirmation request
- User must explicitly confirm ("yes", "confirm", "delete them")
- Track pending operations in conversation context
- Timeout pending confirmations after 2 minutes
- For API errors: LLM translates technical errors to user-friendly messages

---

### 10. Architecture Pattern

**Question**: What's the overall architecture for the chat service?

**Decision**: **Stateless Chat API with Session Management**

**Architecture**:
```
Frontend (Next.js)
    ↓ POST /api/v1/chat/message
Chat Backend (FastAPI)
    ↓ Conversation Manager (session storage)
    ↓ LLM Service (OpenAI API)
    ↓ Function Executor
    ↓ Phase II API Client
Phase II Backend (existing APIs)
    ↓ Database
```

**Components**:
1. **Chat API Endpoint** (`/api/v1/chat/message`)
   - Receives user message + session_id
   - Returns streaming response

2. **Conversation Manager**
   - Manages session storage (in-memory or Redis)
   - Maintains message history
   - Tracks context (referenced todos, pending confirmations)

3. **LLM Service**
   - Wraps OpenAI API
   - Handles function calling
   - Manages prompts and context

4. **Function Executor**
   - Maps LLM function calls to Phase II API calls
   - Handles authentication (passes user JWT)
   - Formats responses for LLM

5. **Phase II API Client**
   - HTTP client for Phase II endpoints
   - Handles errors and retries
   - Validates responses

---

## Technology Stack Summary

### Backend (Python)
- **Framework**: FastAPI (already in use)
- **LLM**: OpenAI API (openai package)
- **HTTP Client**: httpx (for Phase II API calls)
- **Date Parsing**: dateparser
- **Session Storage**: In-memory dict (MVP), Redis (production)
- **Authentication**: JWT (reuse Phase II tokens)

### Frontend (TypeScript/React)
- **Framework**: Next.js (already in use)
- **UI**: Custom React components
- **HTTP Client**: Fetch API with streaming
- **State Management**: React hooks (useState, useEffect)

### Infrastructure
- **Deployment**: Same as Phase II (Vercel frontend, backend on Hugging Face or similar)
- **Environment Variables**: OpenAI API key, Phase II API base URL

---

## Open Questions Resolved

### Conversation History Persistence
**Resolution**: Session-based (in-memory) for MVP. Conversations expire after 30 minutes of inactivity. Can be enhanced with database persistence in future iteration.

**Impact**:
- Simpler implementation
- No database schema changes
- Users start fresh each session
- Trade-off: Can't review past conversations

---

## Risk Mitigation Strategies

### 1. OpenAI Rate Limits
- **Mitigation**: Implement request queuing, exponential backoff, user-facing rate limit messages
- **Fallback**: Cache common responses, implement request throttling per user

### 2. Token Costs
- **Mitigation**: Use GPT-3.5-turbo by default, sliding window context, efficient prompts
- **Monitoring**: Track token usage per request, set budget alerts

### 3. API Latency
- **Mitigation**: Use streaming responses, show typing indicators, optimize prompts
- **Target**: First token within 1 second, complete response within 3 seconds

### 4. Context Loss
- **Mitigation**: Store referenced todo IDs separately, provide "show context" command
- **UX**: Offer conversation reset when context becomes unclear

---

## Next Steps

With research complete, proceed to Phase 1:
1. Design data model for conversation entities
2. Generate API contracts for chat endpoints
3. Create quickstart documentation
4. Update agent context with technology choices
