# Implementation Plan: [FEATURE]

**Branch**: `[###-feature-name]` | **Date**: [DATE] | **Spec**: [link]
**Input**: Feature specification from `/specs/[###-feature-name]/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

This plan implements the migration of the existing `vue-frontend/` application to a new `next-frontend/` Next.js (App Router) + TypeScript + shadcn/ui codebase. The approach is incremental and feature-flag driven: scaffold a new Next.js app, port critical pages incrementally (homepage, course view, chat), verify behavior with contract tests and telemetry, then retire `vue-frontend/` after parity and monitoring windows complete.

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: Python 3.11+ (backend FastAPI); Node 18+ / TypeScript 5.x (frontend)
**Primary Dependencies**: FastAPI (backend), Pydantic (schemas), Next.js (App Router), React, TypeScript, Tailwind CSS, shadcn/ui, Vite (existing Vue), Axios/Fetch client
**Storage**: MongoDB (existing), backend persists course/user data; frontend uses localStorage for guest flows where applicable
**Testing**: pytest for backend, Vitest/Jest for frontend unit tests, Playwright for E2E/contract tests
**Target Platform**: Web (desktop and mobile browsers)
**Project Type**: Web application (separate frontend app for Next.js while `vue-frontend/` is kept until retirement)
**Performance Goals**: Maintain existing performance budgets; primary flows should keep p95 response times and client-side render times within current baselines. Action: capture performance and error baselines for primary flows as part of Phase 0 research (see `research.md`).
**Constraints**: Must preserve backend API contracts; feature-flag rollout required; CI must run type-check and contract tests before merge
**Scale/Scope**: User base and traffic unchanged for planning purposes; migration will be incremental by routes/features

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

and observability). For frontend-migration projects, specify the compatibility strategy
(adapter, feature-flag, or parallel routes) and the rollout/rollback plan.
*Constitution Compliance*

- Principles applied: User-first Incremental Migration; Type Safety & Maintainability; Design System & Accessibility; Preserve Backend Contracts & Tests; Observability
- How satisfied:
  - Type Safety: All new code will be TypeScript with strict tsconfig; CI will enforce type-checks.
  - Incremental migration: Feature flags + adapter routes will enable per-user toggles; `vue-frontend/` remains until retirement.
  - Accessibility: shadcn/ui + Tailwind + automated axe/pa11y checks in CI; manual spot audits for P1 pages.
  - API Contracts: Contract tests (Playwright or integration tests) will run against mocked/staging backend to assert compatibility.
  - Observability: Frontend telemetry events instrumented for primary flows; error logging wired to existing backend telemetry / Sentry-like service.

Compatibility strategy: Feature flags (per Clarification Session). Rollout/Rollback: per-feature toggles can be switched via server-side flagging or environment config; fallback to `vue-frontend/` route if critical regressions are detected.

## Project Structure

### Documentation (this feature)

```
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)

## Phase Outputs

- Phase 0 (research): `research.md` (resolved scaffold, routing, feature-flag pattern, CI, telemetry)
- Phase 1 (design): `data-model.md`, `quickstart.md`, `contracts/openapi-primary.yaml`
- Phase 2 (tasks): `tasks.md` (skeleton created; to be expanded by /speckit.tasks)

Phase 0 status: COMPLETE
```

### Source Code (repository root)
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```
# [REMOVE IF UNUSED] Option 1: Single project (DEFAULT)
src/
├── models/
├── services/
├── cli/
└── lib/

tests/
├── contract/
├── integration/
└── unit/

# [REMOVE IF UNUSED] Option 2: Web application (when "frontend" + "backend" detected)
backend/
├── src/
│   ├── models/
│   ├── services/
```
# Selected structure for migration (web application)
backend/                       # existing FastAPI app (unchanged)
vue-frontend/                  # existing Vue app (kept until retirement)
next-frontend/                 # NEW: Next.js App Router + TypeScript + shadcn/ui (scaffolded here)
  ├── app/                      # Next.js App Router pages and layouts
  ├── components/               # React components (shadcn/ui primitives)
  ├── lib/                      # API client, feature-flag helpers, telemetry helpers
  ├── tests/                    # unit and integration tests
  └── package.json

contracts/                      # API contract descriptions generated in Phase 1
specs/001-migrate-vue-frontend/ # plan, research, data-model, tasks, checklists
```

**Structure Decision**: We will scaffold a new top-level `next-frontend/` Next.js app. During migration, both `next-frontend/` and `vue-frontend/` will coexist; a server-side or CDN-level routing layer plus per-user feature flags will switch users to Next.js routes. Final deletion of `vue-frontend/` is gated behind parity, monitoring, and rollback testing (see FR-009).

