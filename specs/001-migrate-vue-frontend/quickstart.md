# quickstart.md

## Quickstart (developer)

1. From repo root, scaffold Next.js app in `next-frontend/`:

```bash
npx create-next-app@latest next-frontend --ts --use-npm
cd next-frontend
npm install
```

2. Install Tailwind and shadcn/ui per their docs.

3. Run local dev server:

```bash
npm run dev --prefix ./next-frontend
```

4. Run frontend type checks and tests in CI:

```bash
npm run type-check --prefix ./next-frontend
npm test --prefix ./next-frontend
```

## Notes
- Follow `research.md` tasks to wire feature flags and telemetry.
