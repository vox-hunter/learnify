# Feature Specification: [FEATURE NAME]
<!-- Constitution Compliance: This feature relies on the following principles from `.specify/memory/constitution.md`:
- User-first, Incremental Migration
- Type Safety & Maintainability
- Design System & Accessibility
- Preserve Backend Contracts & Tests
Targeted migration approach: move the user-facing Vue SPA to a React-based Next.js App Router codebase that uses TypeScript and shadcn/ui components. The migration MUST be incremental (feature-by-feature or route-by-route), preserve existing backend contracts, include a compatibility/adapter layer during rollout, and keep `vue-frontend/` in the repo until parity is validated. -->
**Feature Branch**: `[###-feature-name]`  
**Created**: [DATE]  
**Status**: Draft  
**Input**: User description: "$ARGUMENTS"

## User Scenarios & Testing *(mandatory)*

<!--
  IMPORTANT: User stories should be PRIORITIZED as user journeys ordered by importance.
  Each user story/journey must be INDEPENDENTLY TESTABLE - meaning if you implement just ONE of them,
  you should still have a viable MVP (Minimum Viable Product) that delivers value.
  
  Assign priorities (P1, P2, P3, etc.) to each story, where P1 is the most critical.
  Think of each story as a standalone slice of functionality that can be:
  - Developed independently
  - Tested independently
  - Deployed independently
  - Demonstrated to users independently
-->

### User Story 1 - [Brief Title] (Priority: P1)

[Describe this user journey in plain language]

**Why this priority**: [Explain the value and why it has this priority level]

**Independent Test**: [Describe how this can be tested independently - e.g., "Can be fully tested by [specific action] and delivers [specific value]"]

**Acceptance Scenarios**:

1. **Given** [initial state], **When** [action], **Then** [expected outcome]
2. **Given** [initial state], **When** [action], **Then** [expected outcome]

---

### User Story 2 - [Brief Title] (Priority: P2)

[Describe this user journey in plain language]

**Why this priority**: [Explain the value and why it has this priority level]

**Independent Test**: [Describe how this can be tested independently]

**Acceptance Scenarios**:

1. **Given** [initial state], **When** [action], **Then** [expected outcome]

---

### User Story 3 - [Brief Title] (Priority: P3)

[Describe this user journey in plain language]

**Why this priority**: [Explain the value and why it has this priority level]

**Independent Test**: [Describe how this can be tested independently]

**Acceptance Scenarios**:

1. **Given** [initial state], **When** [action], **Then** [expected outcome]

---

[Add more user stories as needed, each with an assigned priority]

### Edge Cases

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right edge cases.
-->

- What happens when [boundary condition]?
- How does system handle [error scenario]?

## Requirements *(mandatory)*

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right functional requirements.
-->

### Functional Requirements

- **FR-001**: System MUST [specific capability, e.g., "allow users to create accounts"]
- **FR-002**: System MUST [specific capability, e.g., "validate email addresses"]  
- **FR-003**: Users MUST be able to [key interaction, e.g., "reset their password"]
- **FR-004**: System MUST [data requirement, e.g., "persist user preferences"]
- **FR-005**: System MUST [behavior, e.g., "log all security events"]

<!-- Constitution Compliance: Add a short section near the top of the spec that states which
principles from `.specify/memory/constitution.md` this feature relies on (for example: "Type Safety",
"Design System", "API Contract Stability"). If this spec affects frontend technology choices,
note the targeted stack (e.g., Next.js + TypeScript + shadcn/ui) and any migration compatibility
requirements. -->

*Example of marking unclear requirements:*

- **FR-006**: System MUST authenticate users via Google OAuth (existing backend includes Google OAuth flows in `backend/google_oauth*.py`). Frontend must continue to support Google sign-in and the existing guest flow.
- **FR-007**: System MUST retain user data per existing backend policy; if no explicit policy exists, the default retention for migrated data will be 365 days unless a legal/compliance requirement mandates otherwise.

# Feature Specification: Migrate Vue frontend to Next.js (TypeScript + shadcn/ui)

**Feature Branch**: `001-migrate-vue-frontend`
**Created**: 2025-10-08
**Status**: Draft
**Input**: User description: "Migrate vue frontend to Next.js (TypeScript + shadcn/ui). Backend remains FastAPI (Python)."

<!-- Constitution Compliance: This feature relies on the following principles from `.specify/memory/constitution.md`:
- User-first, Incremental Migration
- Type Safety & Maintainability
- Design System & Accessibility
- Preserve Backend Contracts & Tests

Targeted migration approach: move the user-facing Vue SPA to a React-based Next.js App Router codebase that uses TypeScript and shadcn/ui components. The migration MUST be incremental (feature-by-feature or route-by-route), preserve existing backend contracts, include a compatibility/adapter layer during rollout, and keep `vue-frontend/` in the repo until parity is validated. -->

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Browse and Complete Course (Priority: P1)
A learner visits the site, opens a course, reads the content, and completes associated quizzes.

**Why this priority**: This is the core product experience; migration must not reduce content accessibility or correctness.

**Independent Test**: Run an end-to-end scenario that signs in (or uses guest flow), navigates to a course, opens at least one section, answers quiz items, and observes progress saved/updated.

**Acceptance Scenarios**:
1. **Given** an authenticated or guest learner on the homepage, **When** they open a course and navigate to a lesson, **Then** the lesson content loads and renders quiz questions correctly.
2. **Given** a learner answers and submits quiz questions, **When** submission completes, **Then** progress is persisted and reflected in course progress UI.

---

### User Story 2 - Conversational Chat (Priority: P1)
A user interacts with the Chat interface to ask questions and receive AI replies, including uploading or referencing a file for course generation.

**Why this priority**: Chat is a primary interface for learning and content ingestion in the product.

**Independent Test**: Send a chat message to the existing backend chat endpoint and verify responses render in the UI; test file upload flow (small PDF) and confirm the backend accepts the file and returns a course-generation response.

**Acceptance Scenarios**:
1. **Given** the Chat view open, **When** the user sends a message, **Then** the response appears in the chat feed and UI remains responsive.
2. **Given** a user uploads a supported file from the chat UI, **When** the upload completes, **Then** a course-generation request is issued and a candidate course preview is presented.

---

### User Story 3 - Authentication & Account Management (Priority: P2)
Users sign in via Google OAuth and manage account preferences.

**Why this priority**: Authentication gates access to saved courses and progress.

**Independent Test**: Complete the OAuth sign-in flow, verify session persists across navigation, and confirm account page shows saved profile info.

**Acceptance Scenarios**:
1. **Given** a user choosing Google sign-in, **When** they complete OAuth consent, **Then** they return to the app signed in and see their username/profile.

---

### Edge Cases
- Network interruptions during content load or quiz submission: the UI must show a clear offline/error state and retry options.
- Backend changes in API shape: the frontend must detect contract validation errors and surface actionable messages.
- Large file uploads: progress indicators and size validation must prevent UI hangs or data loss.

## Requirements *(mandatory)*

### Functional Requirements
- **FR-001**: The migrated frontend MUST preserve existing backend contracts. Any contract changes require documented migration and compatibility tests.
- **FR-002**: Core product flows (course browsing, lesson rendering, quiz interactions, chat messaging, file upload) MUST work end-to-end as before migration.
- **FR-003**: Migration MUST be incremental: the project MUST support partial rollout strategies (adapter routes, feature flags, parallel routes) so users can be migrated without full cutover.
- **FR-004**: All new frontend code MUST be written in TypeScript with progressively stricter type checks enabled in CI.
- **FR-005**: UI components for core flows MUST meet WCAG AA accessibility standards; automated checks plus manual spot audits are required.
- **FR-006**: The CI pipeline MUST include type checks, unit tests, and end-to-end contract tests that assert API compatibility before merging migration PRs.
- **FR-007**: Performance and observability instrumentation (frontend telemetry events for key flows, error logging) MUST be included for migrated features.
- **FR-008**: Documentation: migration README must include rollout/rollback steps and a mapping of Vue routes → Next.js pages/components.

**FR-009**: The migration plan MUST include an explicit retirement and removal step for the existing `vue-frontend/` directory; removal may only occur after parity validation, monitoring window, and documented rollback procedures are in place. The team may schedule the actual deletion as part of the final migration phase.

*Assumptions*: Backend endpoints are stable and will retain existing contract semantics during the migration. The team can run parallel builds/deploys and update CI accordingly.

## Key Entities *(include if feature involves data)*
- **Course**: title, sections, lessons, quiz items (preserve shapes provided by backend schemas)
- **User**: id, username, auth token/session
- **ChatMessage**: message text, attachments, session id
- **Upload**: file metadata (name, size, type), upload status

## Success Criteria *(mandatory)*

### Measurable Outcomes
- **SC-001**: End-to-end automated tests for primary user flows (course browse, quiz submit, chat message) pass at >=98% on the migrated routes before deprecating Vue pages.
- **SC-002**: No more than 0.5% increase in user-facing error rate for primary flows during rollout (measured by frontend error telemetry and backend error logs) compared to baseline.
- **SC-003**: Accessibility: core flows meet WCAG AA as verified by automated audits (e.g., axe or similar) and a small manual audit checklist for P1 pages.
- **SC-004**: Developer checks: type-checking and unit tests must pass in CI; merge blocked until type errors are resolved.
- **SC-005**: Rollout safety: ability to rollback or route traffic back to `vue-frontend/` within a single deployment window if serious regressions occur.

## Implementation Constraints & Non-Goals
-- Non-goal: Re-architecting backend APIs is out of scope for this feature — backend changes must be minimal and coordinated.
-- Constraint (updated): Primary rollout strategy is Feature Flags (per Clarification Session). The migration will be performed behind feature flags that allow per-user/per-account toggles between Vue and Next.js implementations. The `vue-frontend/` directory will be retired and deleted only after parity is validated, the monitoring window completes with acceptable metrics, and rollback steps are tested.

## Clarifications

### Session 2025-10-08

- Q: Primary rollout strategy for the frontend migration? → A: A (Feature flags). The requester additionally specified: "completely migrate to Next.js and delete all vue frontend". This directive is recorded here and incorporated into the migration plan: the deletion of `vue-frontend/` will be a controlled, documented final step after parity and monitoring gates are satisfied.

## Migration Phases (high-level)
1. Foundation: Initialize Next.js repo, TypeScript config, Tailwind & shadcn/ui scaffold, CI type-check and test jobs.
2. Port smallest critical route(s): homepage and course view rendering for a single course type; validate E2E tests.
3. Add Chat view and file-upload adapter; validate chat flows with backend.
4. Iteratively port remaining pages, run A/B or feature-flagged rollout, retire `vue-frontend/` after parity and monitoring window.

## Notes & Risks
- Risk: subtle contract mismatches between Vue client code and backend serialization expectations — mitigate with contract tests and contract mock playback.
- Risk: accessibility regressions — mitigate with automated checks and manual spot audits.


---

SUCCESS (spec ready for planning)
