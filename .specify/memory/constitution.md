# Learnify Constitution

<!--
Sync Impact Report

Version change: v0.0.0 -> v0.1.0
Modified principles: Added explicit web-stack migration principle (Vue -> Next.js/TypeScript + shadcn/ui)
Added sections: Frontend Migration Constraints
Templates requiring updates: .specify/templates/plan-template.md ✅ updated, .specify/templates/spec-template.md ✅ updated, .specify/templates/tasks-template.md ✅ updated
Follow-up TODOs: TODO(RATIFICATION_DATE): confirm original ratification date if required by compliance
-->

## Core Principles

### I. User-first, Incremental Migration (NON-NEGOTIABLE)
The project MUST prioritise user-facing continuity: ship small, reversible increments that keep the product usable during the migration from Vue to Next.js. Migration work MUST be split into independently deployable slices (feature flags, adapter layers, or parallel routes). Rationale: large all-at-once rewrites increase risk and block product improvements.

### II. Type Safety & Maintainability
All new frontend code MUST use TypeScript end-to-end (types for props, API clients, and shared contracts). The repository SHOULD adopt strict tsconfig rules (noImplicitAny, strict) progressively. Rationale: type safety prevents regressions and accelerates collaboration across frontend/backend boundaries.

### III. Design System & Accessibility
Adopt and standardise on shadcn/ui components (React + Tailwind) for the new Next.js UI. All components MUST meet WCAG AA accessibility guidelines for core flows (auth, content consumption, quizzes). Rationale: consistent UI primitives reduce duplication and improve accessibility for learners.

### IV. Preserve Backend Contracts & Tests
Backend APIs and data contracts (FastAPI endpoints, Pydantic schemas) are the source of truth during migration. Frontend changes MUST not alter APIs without documented versioning and compatibility tests. All contract-level changes REQUIRE integration tests and a migration plan. Rationale: protect existing users and automated tests from silent breaking changes.

### V. Observability, Performance & Simplicity
Instrumentation (structured logging, telemetry events for key flows, and performance budget checks) MUST be in place for migrated features. Performance budgets for primary flows (page load, quiz interactions) MUST be defined and monitored. Keep implementations simple: prefer readable, well-tested code over clever but fragile patterns.

## Frontend Migration Constraints

- Target stack: Next.js (App Router) with TypeScript and shadcn/ui components styled with Tailwind CSS.
- Maintain a compatibility layer during migration: keep `vue-frontend/` until parity endpoints/pages are ported and validated.
- Build outputs and deploy pipelines MUST be updated to reference Next.js `.next` output and Vercel/Render static build steps when frontend is replaced.

## Development Workflow and Quality Gates

- Feature PRs touching migrated frontend code MUST include: Type-checked code, unit tests for components, integration tests for critical user journeys, and a migration checklist entry.
- Constitution Check: Plans (specs/plan.md) MUST include a short "Constitution Compliance" section stating which principles the feature depends on and how gates are satisfied.
- Reviewers MUST verify TypeScript strictness, accessibility checks, and API contract compatibility before merge.

## Governance

Amendments to this constitution MUST be documented in a PR describing the change, the rationale, and a migration/rollout plan when governance-affecting principles change. Minor clarifications (typos, wording) can be applied as a patch-level amendment.

**Version**: v0.1.0 | **Ratified**: TODO(RATIFICATION_DATE) | **Last Amended**: 2025-10-08