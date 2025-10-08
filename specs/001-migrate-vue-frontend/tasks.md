# tasks.md

Feature: Migrate `vue-frontend/` to `next-frontend/` (Next.js App Router + TypeScript + shadcn/ui)
Branch: `001-migrate-vue-frontend`

Summary: This tasks list implements the migration in small, independently testable slices. Follow phases in order: Setup → Foundational → User Stories (P1/P1/P2) → Polish & Retirement.

Total tasks: T001..T030 (numbered sequentially)

Phase 1 — Setup (project initialization & infra)

- T001: [SETUP] Create `next-frontend/` scaffold using Create Next App (TypeScript).
  - Path: /next-frontend/ (repo root)
  - Command: `npx create-next-app@latest next-frontend --ts --use-npm`
  - Output: next-frontend package.json, tsconfig, app/ directory
  - Parallel: no (single scaffold)

- T002: [SETUP] Install Tailwind CSS and configure per Next.js docs.
  - Path: /next-frontend/
  - Steps: install tailwindcss; create tailwind.config.cjs; add globals.css
  - Parallel: [P]

- T003: [SETUP] Install shadcn/ui primitives and run component generator scaffolding.
  - Path: /next-frontend/
  - Steps: `npm i @shadcn/ui` (or follow shadcn install instructions), scaffold a sample component
  - Parallel: [P]

- T004: [SETUP] Add TypeScript strict config and initial linting rules.
  - Path: /next-frontend/tsconfig.json
  - Steps: enable strict, noImplicitAny; add eslint + prettier config and CI-friendly rules
  - Parallel: [P]

- T005: [SETUP] Add basic telemetry & feature-flag helpers library (lib/telemetry.ts, lib/featureFlags.ts) in `next-frontend/`.
  - Path: /next-frontend/lib/
  - Steps: create telemetry interface, placeholder client that logs to console or emits structured events; feature-flag helper that reads server-set cookie and local override
  - Parallel: [P]

- T006: [SETUP] Add initial CI job scaffold for `next-frontend` (type-check, build, tests)
  - Path: .github/workflows/ (or existing CI config)
  - Steps: add a job that runs `npm ci`, `npm run build`, `npm run type-check`, `npm test` for `next-frontend`
  - Parallel: [P]

Checkpoint: Setup complete (T001..T006) — Proceed to Foundational tasks

Phase 2 — Foundational (blocking prerequisites)

- T007: [FOUNDATION] Generate TypeScript types from backend OpenAPI stub.
  - Path: /specs/001-migrate-vue-frontend/contracts/openapi-primary.yaml -> /next-frontend/src/types/api.d.ts
  - Steps: run `npx openapi-typescript specs/001-migrate-vue-frontend/contracts/openapi-primary.yaml --output next-frontend/src/types/api.ts`
  - Parallel: no (types are used by subsequent work)

- T008: [FOUNDATION] Implement a lightweight adapter route strategy (server middleware) to toggle between Next.js and Vue routes based on feature-flag.
  - Path: /next-frontend/lib/flagAdapter.ts and server routing or CDN config
  - Steps: create middleware that checks a server-set cookie or header and proxies to Next.js page or Vue static asset
  - Parallel: no

- T009: [FOUNDATION] Add Playwright contract test harness that can run critical user flows against a staging backend.
  - Path: /next-frontend/tests/playwright/ or /tests/playwright/
  - Steps: create Playwright config, basic test for /courses/{id} and /chat
  - Parallel: [P]

- T010: [FOUNDATION] Capture performance and error baselines for primary flows (SC-002).
  - Path: /specs/001-migrate-vue-frontend/baselines/
  - Steps: run a small Playwright script that loads homepage, opens a course, submits a quiz, sends a chat; record frontend error count and timing metrics
  - Parallel: no

- T011: [FOUNDATION] Wire telemetry events for: page_view, course_open, quiz_submit, chat_message_sent, upload_started/completed, error.
  - Path: /next-frontend/lib/telemetry.ts + instrument P1 components as they are built
  - Parallel: [P]

Checkpoint: Foundations complete (T007..T011)

Phase 3 — User Story 1 (US1) — Browse and Complete Course (Priority: P1)
Goal: Implement course browsing, lesson rendering, and quiz interactions for an MVP course type. Independent test: end-to-end test that navigates to a course, completes a quiz, and observes persisted progress.

- T012: [US1] Create Course Page route and layout in Next.js App Router.
  - Path: /next-frontend/app/courses/[id]/page.tsx
  - Steps: implement server-side fetch to backend `/courses/{id}`, render content, include quiz component placeholder
  - Parallel: no (route file must exist before page-level components)

- T013: [US1] Implement Course API client that calls backend endpoints using generated types.
  - Path: /next-frontend/lib/api/course.ts
  - Steps: create typed API calls for getCourse(id) and submitQuiz responses
  - Parallel: [P]

- T014: [US1] Build Quiz UI components (QuizQuestion, QuizForm) using shadcn/ui primitives and accessibility guidelines.
  - Path: /next-frontend/components/QuizQuestion.tsx, /next-frontend/components/QuizForm.tsx
  - Steps: implement multiple choice, fill-in-the-blank, true/false renderers, keyboard accessible focus, aria labels
  - Parallel: [P]

- T015: [US1] Implement progress-saving logic for quiz submissions and update UI to reflect progress.
  - Path: /next-frontend/lib/progress.ts, integrated in QuizForm
  - Steps: call course API submit endpoints; update local UI and emit telemetry events
  - Parallel: no (integration step)

- T016: [US1] Add automated accessibility checks for the Course and Quiz pages (axe-core in CI or Playwright checks).
  - Path: /next-frontend/tests/accessibility/course.spec.ts
  - Steps: include axe checks in Playwright run for the rendered course page
  - Parallel: [P]

- T017: [US1] Add Playwright E2E test that performs the Independent Test described above.
  - Path: /next-frontend/tests/playwright/us1-course.spec.ts
  - Steps: script navigates to `/courses/{id}`, answers quiz, submits, verifies progress persisted; asserts telemetry events emitted and no errors
  - Parallel: [P]

Checkpoint: US1 complete (T012..T017)

Phase 4 — User Story 2 (US2) — Conversational Chat (Priority: P1)
Goal: Implement Chat UI and file upload for course generation. Independent test: send a chat, receive a response, upload a small PDF and observe course generation request/preview.

- T018: [US2] Create Chat Page route and base layout in Next.js.
  - Path: /next-frontend/app/chat/page.tsx
  - Steps: implement client-side component that posts messages to `/chat` endpoint and renders responses
  - Parallel: no

- T019: [US2] Implement Chat API client and file upload adapter (multipart) with progress indicators.
  - Path: /next-frontend/lib/api/chat.ts and /next-frontend/lib/upload.ts
  - Steps: implement sendMessage(), uploadFile() with progress callbacks and telemetry hooks
  - Parallel: [P]

- T020: [US2] Build Chat UI components (MessageList, MessageInput, FileUploadButton) with accessible keyboard support.
  - Path: /next-frontend/components/Chat/*
  - Steps: use shadcn/ui inputs and accessible list rendering
  - Parallel: [P]

- T021: [US2] Add Playwright test for chat messaging and the file upload flow (small PDF) that asserts the backend receives the file and returns a course candidate.
  - Path: /next-frontend/tests/playwright/us2-chat.spec.ts
  - Parallel: [P]

- T022: [US2] Add retry & error UX for upload and chat errors, instrument telemetry for upload_started/upload_completed/error.
  - Path: /next-frontend/components/Chat/ErrorHandler.tsx, /next-frontend/lib/telemetry.ts
  - Parallel: [P]

Checkpoint: US2 complete (T018..T022)

Phase 5 — User Story 3 (US3) — Authentication & Account Management (Priority: P2)
Goal: Ensure Google OAuth sign-in integrated and account page shows profile and preferences. Independent test: complete OAuth sign-in and view profile page.

- T023: [US3] Implement Google Sign-In UI that delegates to backend OAuth endpoints (existing backend code in `backend/google_oauth*.py`).
  - Path: /next-frontend/components/Auth/GoogleSignIn.tsx
  - Steps: Add sign-in button that navigates to backend OAuth flow and returns user session
  - Parallel: no

- T024: [US3] Create Account page and preferences UI.
  - Path: /next-frontend/app/account/page.tsx
  - Steps: fetch /user/{id}, render profile, allow editing preferences (local only for MVP)
  - Parallel: [P]

- T025: [US3] Ensure session persistence and client-side auth hooks (useAuth) to centralize user state.
  - Path: /next-frontend/lib/auth.ts
  - Steps: implement client-side hook that reads session cookie and fetches user profile
  - Parallel: [P]

- T026: [US3] Add Playwright test that performs OAuth sign-in flow (integration test) and verifies profile page.
  - Path: /next-frontend/tests/playwright/us3-auth.spec.ts
  - Parallel: [P]

Checkpoint: US3 complete (T023..T026)

Phase 6 — Polish, Integration & Retirement

- T027: [POLISH] Run accessibility spot audits and fix any WCAG AA failures discovered in automated runs.
  - Path: /next-frontend/ (various files)
  - Parallel: [P]

- T028: [POLISH] Add CI gating: require `next-frontend` type-check and Playwright contract tests pass before merge on migration PRs.
  - Path: .github/workflows/
  - Parallel: no

- T029: [RETIRE] Run parity verification checklist comparing Vue flows and Next flows (SC-001..SC-005). Produce a migration report and monitoring window plan.
  - Path: /specs/001-migrate-vue-frontend/parity-report.md
  - Parallel: no

- T030: [RETIRE] Remove `vue-frontend/` directory and update deploy/CI configs to build only `next-frontend/` (only after parity and monitoring window passed).
  - Path: repo root - PR that deletes `vue-frontend/` and updates CI
  - Parallel: no

Dependencies & Story Completion Order

- Foundations (T007..T011) must complete before any US implementation tasks (T012+).
- Recommended implementation order: US1 (T012..T017) → US2 (T018..T022) → US3 (T023..T026).

Parallel opportunities (examples)

- While T007 runs (type generation), T002 and T003 (Tailwind & shadcn installs) can run in parallel.
- Component implementation tasks (T014, T020) can be developed in parallel by different engineers [P].
- Tests (Playwright specs) can be written in parallel with component development but should be run after the component's basic implementation.

Independent Test Criteria per Story

- US1: Playwright E2E passes course browse & quiz submit and asserts persisted progress (T017).
- US2: Playwright test sends chat message and uploads PDF; verifies course generation request (T021).
- US3: Playwright test completes OAuth sign-in and validates profile page (T026).

Suggested MVP

- Implement only US1 (T012..T017) as the MVP to provide an independently testable product slice (course browse + quiz) that demonstrates parity for core flows.
# tasks.md

## Phase 0 - Research
- Create `next-frontend/` scaffold (create-next-app --ts)
- Define feature-flag approach and implement a small prototype
- Capture performance and error baselines for SC-002

## Phase 1 - Scaffold & Contracts
- Scaffold Next.js app with Tailwind and shadcn/ui
- Generate TypeScript types from OpenAPI or hand-author DTOs that match Pydantic schemas
- Add Playwright contract tests for primary flows

## Phase 2 - Porting (iterative)
- Port homepage and course view for a single course type; add unit tests and accessibility checks
- Port Chat view and upload adapters; validate end-to-end chat + upload flows
- Incrementally port remaining pages; monitor telemetry

## Phase 3 - Rollout & Retirement
- Rollout behind feature flags per cohort (internal users → beta users → all users)
- Monitor SC-002 metrics during rollout window (error rate, latency, UX regressions)
- When parity is validated, perform retirement PR to remove `vue-frontend/` and update CI/deploy configs

## CI / Automation
- Add `next-frontend` job in CI for build, type-check, unit tests, and Playwright contract tests
- Add accessibility checks (axe) as part of CI for P1 pages
