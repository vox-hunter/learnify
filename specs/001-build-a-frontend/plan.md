
# Implementation Plan: AI Loom React Frontend

**Branch**: `001-build-a-frontend` | **Date**: 2025-09-28 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-build-a-frontend/spec.md`

## Execution Flow (/plan command scope)
```
1. Load feature spec from Input path
   → If not found: ERROR "No feature spec at {path}"
2. Fill Technical Context (scan for NEEDS CLARIFICATION)
   → Detect Project Type from file system structure or context (web=frontend+backend, mobile=app+api)
   → Set Structure Decision based on project type
3. Fill the Constitution Check section based on the content of the constitution document.
4. Evaluate Constitution Check section below
   → If violations exist: Document in Complexity Tracking
   → If no justification possible: ERROR "Simplify approach first"
   → Update Progress Tracking: Initial Constitution Check
5. Execute Phase 0 → research.md
   → If NEEDS CLARIFICATION remain: ERROR "Resolve unknowns"
6. Execute Phase 1 → contracts, data-model.md, quickstart.md, agent-specific template file (e.g., `CLAUDE.md` for Claude Code, `.github/copilot-instructions.md` for GitHub Copilot, `GEMINI.md` for Gemini CLI, `QWEN.md` for Qwen Code or `AGENTS.md` for opencode).
7. Re-evaluate Constitution Check section
   → If new violations: Refactor design, return to Phase 1
   → Update Progress Tracking: Post-Design Constitution Check
8. Plan Phase 2 → Describe task generation approach (DO NOT create tasks.md)
9. STOP - Ready for /tasks command
```

**IMPORTANT**: The /plan command STOPS at step 7. Phases 2-4 are executed by other commands:
- Phase 2: /tasks command creates tasks.md
- Phase 3-4: Implementation execution (manual or via tools)

## Summary
Replace the existing Streamlit frontend with a performant, modular React + Vite frontend that maintains full compatibility with the existing Python backend APIs. The new frontend will provide enhanced user experience through optimized performance, reduced CSS bloat, and improved responsiveness while preserving all current functionality including custom components and analytics.

## Technical Context
**Language/Version**: TypeScript 5.x with React 18+ and Vite 5.x  
**Primary Dependencies**: React, Vite, React Router, Axios, React Query, React Testing Library, Jest  
**Storage**: Browser localStorage/sessionStorage for client state, existing Python backend for persistence  
**Testing**: Jest + React Testing Library for unit/integration, Playwright for E2E  
**Target Platform**: Modern web browsers (Chrome 90+, Firefox 88+, Safari 14+, Edge 90+)
**Project Type**: web (frontend only - replaces Streamlit UI)  
**Performance Goals**: <500KB gzipped bundle, <3s initial load, 60fps animations, Lighthouse scores ≥90  
**Constraints**: Must preserve all existing backend API contracts, maintain custom components, mobile-responsive  
**Scale/Scope**: 5 main pages, ~20 React components, existing backend handles user scale

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Code Quality Gates**:

- [x] Components designed for single responsibility and reusability
- [x] Clear separation of concerns (UI, business logic, utilities)
- [x] Consistent naming conventions planned (PascalCase/camelCase/kebab-case)

**Testing Standards Gates**:

- [x] Unit test strategy defined for all React components
- [x] Integration test plan for API interactions
- [x] Critical user paths identified for E2E coverage
- [x] Target coverage ≥80% components, ≥90% utilities

**UX Consistency Gates**:

- [x] Design system compliance verified
- [x] Responsive breakpoints defined (768px, 1024px, 1440px)
- [x] Navigation patterns follow established conventions

**Performance Gates**:

- [x] Bundle size budget established (<500KB gzipped)
- [x] Lazy loading strategy for heavy components (>50KB)
- [x] Animation performance considerations (60fps, non-blocking)

**Maintainability Gates**:

- [x] Folder structure follows established patterns
- [x] Documentation requirements defined for components/hooks/services
- [x] Onboarding process designed for <2 hour setup

## Project Structure

### Documentation (this feature)
```
specs/[###-feature]/
├── plan.md              # This file (/plan command output)
├── research.md          # Phase 0 output (/plan command)
├── data-model.md        # Phase 1 output (/plan command)
├── quickstart.md        # Phase 1 output (/plan command)
├── contracts/           # Phase 1 output (/plan command)
└── tasks.md             # Phase 2 output (/tasks command - NOT created by /plan)
```

### Source Code (repository root)
```
backend/                    # Existing Python backend (preserved)
├── src/
│   ├── models/
│   ├── services/
│   └── api/
└── tests/

frontend/                   # New React frontend (to be created)
├── src/
│   ├── components/         # Reusable UI components
│   │   ├── common/         # Generic components (Button, Input, etc.)
│   │   ├── forms/          # Form-specific components
│   │   └── quiz/           # Quiz-specific components (fill-in-blanks, etc.)
│   ├── pages/              # Route-level page components
│   │   ├── HomePage/
│   │   ├── CoursePage/
│   │   ├── LoginPage/
│   │   └── LegalPages/
│   ├── services/           # API communication layer
│   ├── hooks/              # Custom React hooks
│   ├── utils/              # Pure utility functions
│   ├── types/              # TypeScript type definitions
│   └── styles/             # Global styles and CSS modules
├── tests/
│   ├── unit/               # Component unit tests
│   ├── integration/        # API integration tests
│   └── e2e/                # End-to-end tests
├── public/                 # Static assets
└── vite.config.ts          # Vite configuration
```

**Structure Decision**: Web application with separate frontend directory. Backend remains unchanged to preserve existing APIs and functionality. Frontend uses modern React project structure with clear separation of concerns following constitutional requirements.

## Phase 0: Outline & Research
1. **Extract unknowns from Technical Context** above:
   - For each NEEDS CLARIFICATION → research task
   - For each dependency → best practices task
   - For each integration → patterns task

2. **Generate and dispatch research agents**:
   ```
   For each unknown in Technical Context:
     Task: "Research {unknown} for {feature context}"
   For each technology choice:
     Task: "Find best practices for {tech} in {domain}"
   ```

3. **Consolidate findings** in `research.md` using format:
   - Decision: [what was chosen]
   - Rationale: [why chosen]
   - Alternatives considered: [what else evaluated]

**Output**: research.md with all NEEDS CLARIFICATION resolved

## Phase 1: Design & Contracts
*Prerequisites: research.md complete*

1. **Extract entities from feature spec** → `data-model.md`:
   - Entity name, fields, relationships
   - Validation rules from requirements
   - State transitions if applicable

2. **Generate API contracts** from functional requirements:
   - For each user action → endpoint
   - Use standard REST/GraphQL patterns
   - Output OpenAPI/GraphQL schema to `/contracts/`

3. **Generate contract tests** from contracts:
   - One test file per endpoint
   - Assert request/response schemas
   - Tests must fail (no implementation yet)

4. **Extract test scenarios** from user stories:
   - Each story → integration test scenario
   - Quickstart test = story validation steps

5. **Update agent file incrementally** (O(1) operation):
   - Run `.specify/scripts/powershell/update-agent-context.ps1 -AgentType copilot`
     **IMPORTANT**: Execute it exactly as specified above. Do not add or remove any arguments.
   - If exists: Add only NEW tech from current plan
   - Preserve manual additions between markers
   - Update recent changes (keep last 3)
   - Keep under 150 lines for token efficiency
   - Output to repository root

**Output**: data-model.md, /contracts/*, failing tests, quickstart.md, agent-specific file

## Phase 2: Task Planning Approach
*This section describes what the /tasks command will do - DO NOT execute during /plan*

**Task Generation Strategy**:
- Load `.specify/templates/tasks-template.md` as React frontend base
- Generate tasks from Phase 1 design docs (contracts, data model, quickstart)
- Each API contract → integration test task [P]
- Each React component → unit test task [P]
- Each data entity → TypeScript type definition task [P]
- Implementation tasks following TDD approach

**Ordering Strategy**:
- Setup: Vite project, TypeScript config, testing setup
- Types & Services: TypeScript interfaces, API service layer
- Components: React components with tests first
- Pages: Route-level components and navigation
- Integration: E2E tests, performance optimization
- Mark [P] for parallel execution (independent files)

**Estimated Output**: 20-25 numbered, ordered tasks in tasks.md

**IMPORTANT**: This phase is executed by the /tasks command, NOT by /plan

## Phase 3+: Future Implementation
*These phases are beyond the scope of the /plan command*

**Phase 3**: Task execution (/tasks command creates tasks.md)  
**Phase 4**: Implementation (execute tasks.md following constitutional principles)  
**Phase 5**: Validation (run tests, execute quickstart.md, performance validation)

## Complexity Tracking
*Fill ONLY if Constitution Check has violations that must be justified*

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |


## Progress Tracking
*This checklist is updated during execution flow*

**Phase Status**:
- [x] Phase 0: Research complete (/plan command)
- [x] Phase 1: Design complete (/plan command)
- [x] Phase 2: Task planning complete (/plan command - describe approach only)
- [ ] Phase 3: Tasks generated (/tasks command)
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:
- [x] Initial Constitution Check: PASS
- [x] Post-Design Constitution Check: PASS
- [x] All NEEDS CLARIFICATION resolved
- [x] Complexity deviations documented

---
*Based on Constitution v1.0.0 - See `/memory/constitution.md`*
