# Evolution of Todo Constitution
<!-- Spec-Driven Development for the Five-Phase Todo Application -->

## Core Principles

### I. Spec-Driven Development (SDD) – Non-Negotiable
All code MUST be generated from written specifications. Manual code writing is prohibited at every stage. If output is incorrect, the SPEC must be refined—never the code. Every feature requires clear intent, defined inputs/outputs, explicit constraints, and acceptance criteria before implementation.

### II. Strict Data Model Compliance
The canonical Todo schema is fixed and immutable across all five phases. Deviations are not permitted. The schema includes: id (unique auto-increment integer), title (required string), description (optional string), and completion metadata. All phases must preserve this contract.

### III. Phase Isolation & Forward Compatibility
Each phase must be architecturally independent. Decisions made in early phases (Python CLI, Web, AI) MUST NOT block later phases (Kubernetes, Cloud-native). Every API contract and data interface must support extension without breaking existing consumers.

### IV. Feature Completeness
Every feature must have:
- Clear intent (what problem does it solve?)
- Defined inputs and outputs (API/UI contracts)
- Explicit constraints (limits, assumptions, edge cases)
- Acceptance criteria (testable pass/fail conditions)

### V. Code Generation & Validation
Claude Code is the sole authority for code generation. All implementations are validated against the specification. If tests fail or behavior diverges from spec, the issue is diagnosed via spec refinement, not ad-hoc code patching.

## Architectural Vision

The project evolves across five phases with distinct goals:

- **Phase I**: In-memory Python CLI application (specification & prototyping)
- **Phase II**: Full-stack Web Application (UI, API, persistence)
- **Phase III**: AI-powered conversational Todo management (natural language interface)
- **Phase IV**: Local Kubernetes deployment (orchestration & scaling)
- **Phase V**: Cloud-native distributed deployment (multi-region, serverless)

Each phase ships independently and must support the canonical Todo schema without modification.

## Development Standards

### Testing Discipline
- All features are test-first: specification → test design → implementation
- Unit tests are mandatory for business logic; integration tests for inter-component contracts
- Test output must be reproducible and tied to acceptance criteria

### Error Handling & Constraints
- Errors are explicit and documented in the spec (error taxonomy with codes/messages)
- Idempotency and timeouts must be specified upfront
- Edge cases and failure modes are addressed before implementation

### Code Quality & Simplicity
- Prefer small, testable changes over large refactors
- No unrelated cleanup in feature commits
- Do not hardcode secrets or configuration; use environment variables and documentation
- Keep reasoning private; output decisions, artifacts, and justifications

## Governance

### Amendment Procedure
1. Amendments to this constitution require explicit ratification via `/sp.constitution`
2. Version bumps follow semantic versioning:
   - **MAJOR**: Backward-incompatible principle removals or redefinitions
   - **MINOR**: New principle/section added or materially expanded guidance
   - **PATCH**: Clarifications, wording, or non-semantic refinements
3. All PRs and code reviews must verify compliance with active principles
4. Deviations require documented justification tied to risk/benefit analysis

### Prompt History Records (PHRs)
Every user prompt receives a Prompt History Record in `history/prompts/`:
- Constitution changes → `history/prompts/constitution/`
- Feature-specific work → `history/prompts/<feature-name>/`
- General tasks → `history/prompts/general/`

PHRs preserve the full user input, key assistant output, files modified, tests run, and outcome.

### Architectural Decision Records (ADRs)
Significant architectural decisions (framework choices, data models, deployment strategies) are documented in `history/adr/` with full reasoning, alternatives considered, and tradeoffs. ADRs are created by explicit user request; never auto-generated.

**Version**: 1.0.0 | **Ratified**: 2026-01-09 | **Last Amended**: 2026-01-09
