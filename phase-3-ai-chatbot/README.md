# Phase III: AI-Powered Todo Chatbot

**Status**: 🔜 Planned
**Points**: 200
**Due Date**: Dec 21, 2025
**Technology Stack**: OpenAI ChatKit, Agents SDK, Official MCP SDK

## Overview

Phase III transforms the todo application into an AI-powered chatbot that allows users to manage their todos through natural language conversations. This phase integrates cutting-edge AI technologies to provide an intelligent, conversational interface.

## Planned Features

### AI Chatbot Interface
- 🔜 Natural language todo management
- 🔜 Conversational UI with context awareness
- 🔜 Multi-turn dialogue support
- 🔜 Intent recognition and entity extraction
- 🔜 Smart suggestions and recommendations
- 🔜 Voice input support (optional)

### OpenAI ChatKit Integration
- 🔜 Chat-based UI components
- 🔜 Message history and threading
- 🔜 Real-time streaming responses
- 🔜 Rich message formatting
- 🔜 File attachments and media support
- 🔜 User presence and typing indicators

### Agents SDK
- 🔜 Custom AI agents for todo operations
- 🔜 Agent orchestration and workflows
- 🔜 Tool calling and function execution
- 🔜 Agent memory and context management
- 🔜 Multi-agent collaboration
- 🔜 Agent monitoring and debugging

### Official MCP SDK
- 🔜 Model Context Protocol implementation
- 🔜 Context management and optimization
- 🔜 Prompt engineering and templates
- 🔜 Response parsing and validation
- 🔜 Error handling and retry logic
- 🔜 Performance monitoring

### Natural Language Capabilities
- 🔜 "Add a todo to buy groceries tomorrow"
- 🔜 "Show me all high priority tasks"
- 🔜 "Mark the meeting task as complete"
- 🔜 "What do I need to do today?"
- 🔜 "Reschedule my dentist appointment to next week"
- 🔜 "Find all todos tagged with 'work'"

## Architecture

```
phase-3-ai-chatbot/
├── frontend/              # Chat UI (React/Next.js)
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatInterface.tsx
│   │   │   ├── MessageList.tsx
│   │   │   ├── InputBox.tsx
│   │   │   └── TodoCard.tsx
│   │   ├── lib/
│   │   │   ├── chatkit-client.ts
│   │   │   └── api-client.ts
│   │   └── hooks/
│   │       ├── useChat.ts
│   │       └── useTodos.ts
│   └── package.json
├── backend/               # AI Agent Backend
│   ├── agents/
│   │   ├── todo_agent.py      # Main todo management agent
│   │   ├── nlp_agent.py       # NLP processing agent
│   │   └── orchestrator.py    # Agent orchestration
│   ├── mcp/
│   │   ├── context.py         # MCP context management
│   │   ├── prompts.py         # Prompt templates
│   │   └── tools.py           # Tool definitions
│   ├── services/
│   │   ├── openai_service.py  # OpenAI API integration
│   │   ├── intent_service.py  # Intent recognition
│   │   └── entity_service.py  # Entity extraction
│   └── requirements.txt
└── README.md             # This file
```

## Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Chat UI | OpenAI ChatKit | Pre-built chat interface components |
| AI Framework | Agents SDK | Agent orchestration and management |
| Context Protocol | Official MCP SDK | Model context management |
| LLM | OpenAI GPT-4 | Natural language understanding |
| Backend | FastAPI | API endpoints for agents |
| Database | Neon DB | Persistent storage (from Phase II) |
| Real-time | WebSockets | Live chat updates |

## Natural Language Examples

### Adding Todos
```
User: "Add a todo to finish the project report by Friday"
Bot: "✅ I've added 'Finish the project report' with a due date of Friday, Dec 20. Would you like to set a priority?"

User: "Make it high priority"
Bot: "✅ Updated to high priority. Anything else?"
```

### Querying Todos
```
User: "What do I have to do today?"
Bot: "You have 3 tasks due today:
1. 🔴 Finish project report (High priority)
2. 🟡 Team meeting at 2pm (Medium priority)
3. 🟢 Review pull requests (Low priority)"
```

### Updating Todos
```
User: "Move the dentist appointment to next Tuesday"
Bot: "✅ I've rescheduled 'Dentist appointment' from Dec 15 to Dec 23 (next Tuesday)."
```

### Smart Suggestions
```
User: "I'm feeling overwhelmed"
Bot: "I understand. You have 12 pending tasks. Here are some suggestions:
- 3 tasks are overdue - would you like to reschedule them?
- 5 tasks have no priority set - shall we prioritize them together?
- 2 tasks could be delegated - want to mark them for review?"
```

## AI Agent Capabilities

### Todo Management Agent
- Create, read, update, delete todos
- Set priorities, tags, due dates
- Mark tasks complete/incomplete
- Filter and search todos

### NLP Processing Agent
- Intent classification (add, update, delete, query, etc.)
- Entity extraction (dates, priorities, tags, titles)
- Context understanding (pronouns, references)
- Sentiment analysis

### Orchestrator Agent
- Route requests to appropriate agents
- Manage multi-turn conversations
- Handle complex workflows
- Coordinate agent responses

## MCP Integration

### Context Management
- Maintain conversation history
- Track user preferences
- Store todo context
- Manage session state

### Prompt Engineering
- System prompts for each agent
- Few-shot examples for common tasks
- Dynamic prompt construction
- Response formatting templates

### Tool Definitions
```python
tools = [
    {
        "name": "add_todo",
        "description": "Add a new todo item",
        "parameters": {
            "title": "string",
            "priority": "enum[high,medium,low]",
            "due_date": "date",
            "tags": "array[string]"
        }
    },
    # ... more tools
]
```

## Development Roadmap

### Phase 3.1: OpenAI Integration
- [ ] Setup OpenAI API access
- [ ] Implement basic chat completion
- [ ] Create prompt templates
- [ ] Add streaming responses
- [ ] Implement error handling

### Phase 3.2: Agents SDK Setup
- [ ] Initialize Agents SDK project
- [ ] Create todo management agent
- [ ] Implement tool calling
- [ ] Add agent memory
- [ ] Setup agent monitoring

### Phase 3.3: MCP Implementation
- [ ] Integrate Official MCP SDK
- [ ] Implement context management
- [ ] Create prompt engineering system
- [ ] Add response parsing
- [ ] Optimize context usage

### Phase 3.4: NLP Capabilities
- [ ] Intent recognition system
- [ ] Entity extraction
- [ ] Date/time parsing
- [ ] Context resolution
- [ ] Multi-turn dialogue

### Phase 3.5: ChatKit UI
- [ ] Setup OpenAI ChatKit
- [ ] Build chat interface
- [ ] Add message components
- [ ] Implement real-time updates
- [ ] Add voice input (optional)

### Phase 3.6: Integration & Testing
- [ ] Connect UI to agents
- [ ] End-to-end testing
- [ ] Performance optimization
- [ ] User acceptance testing
- [ ] Documentation

## Prerequisites

- OpenAI API key
- Node.js 18+ (for ChatKit)
- Python 3.13+ (for Agents)
- Phase II backend running
- Neon DB configured

## Getting Started (Coming Soon)

```bash
# Backend
cd phase-3-ai-chatbot/backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
export OPENAI_API_KEY=your_key_here
uvicorn main:app --reload

# Frontend
cd phase-3-ai-chatbot/frontend
npm install
npm run dev
```

## Environment Variables

```env
# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4-turbo-preview

# MCP
MCP_CONTEXT_WINDOW=128000
MCP_MAX_TOKENS=4096

# Agents SDK
AGENTS_LOG_LEVEL=info
AGENTS_MEMORY_SIZE=10

# Backend
API_BASE_URL=http://localhost:8000
DATABASE_URL=postgresql://...
```

## Migration from Phase II

The Phase II REST API will be extended with:
- WebSocket endpoints for real-time chat
- Agent endpoints for AI operations
- Context management endpoints
- Tool execution endpoints

## Next Phase

**Phase IV: Local Kubernetes Deployment**
- Docker containerization
- Minikube local cluster
- Helm charts
- kubectl-ai integration
- kagent for Kubernetes management

See [../phase-4-kubernetes/README.md](../phase-4-kubernetes/README.md) for Phase IV details.

## Status

🔜 **Not Started** - Waiting for Phase II completion and approval.

---

**Previous Phase**: [Phase II - Web App](../phase-2-web-app/README.md)
**Next Phase**: [Phase IV - Kubernetes](../phase-4-kubernetes/README.md)
