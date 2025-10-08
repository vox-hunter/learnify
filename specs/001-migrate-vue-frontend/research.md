# research.md

## Purpose
Resolve open questions marked as NEEDS CLARIFICATION in the plan and capture decisions for the migration to Next.js + TypeScript + shadcn/ui.

## Open questions and decisions

- Scaffold location for new frontend
  - Decision: Create a new top-level folder `next-frontend/` in the repository root. Rationale: keeps the existing `vue-frontend/` intact until retirement and aligns with repo conventions.

- Routing approach
  - Decision: Next.js App Router (server components where appropriate) with a page-per-route mapping. Use edge/SSR for dynamic chat and course pages needing SEO where beneficial.

- Feature flags / rollout pattern
  - Decision: Server-controlled feature flags (simple JSON config or third-party flags like LaunchDarkly) with per-user/per-account toggles. Provide a client-side SDK and a server-side cookie fallback to ensure rollback capability.

- CI adjustments
  - Decision: Add `next-frontend` job to CI that runs `pnpm install`, `pnpm build`, `pnpm type-check`, `pnpm test` and runs Playwright contract tests against staging. Ensure cache of node modules for speed.

- Telemetry & observability
  - Decision: Instrument migrated flows with a lightweight telemetry client (e.g., segment/GA4 or Sentry for errors). Emit structured events for: page_view, course_open, quiz_submit, chat_message_sent, upload_started, upload_completed, error. Ensure privacy and PII rules followed.

## Alternatives considered

- Single-monorepo replacement (delete `vue-frontend/` immediately): rejected due to high risk and inability to rollback quickly.
- Client-only feature flags: rejected in favor of server-controlled flags to allow instant rollbacks and coarse-grained control.

## Actionable research tasks

- Task: Create `next-frontend/` scaffold using `create-next-app --ts` and install Tailwind + shadcn/ui.
- Task: Prototype feature-flag helper and adapter layer that routes requests to Next.js pages when feature is enabled.
- Task: Add telemetry helper library and define telemetry event schema for primary flows.
- Task: Capture existing performance and error baselines for primary flows (SC-002) before any rollout.

## Research summary

- Decision: Proceed with `next-frontend/` scaffold, App Router, TypeScript strict mode, shadcn/ui, server-side feature flags, CI changes, and telemetry events as above.
