---
id: "0028"
title: "Fix Better Auth Registration User Persistence Issue"
stage: "general"
date: "2026-03-28"
surface: "agent"
model: "claude-sonnet-4.6"
feature: "none"
branch: "main"
user: "unknown"
command: "manual"
labels: ["better-auth", "drizzle", "adapter", "database", "registration", "neon"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - "phase-II-todo-full-stack-web-app/frontend/src/lib/auth.ts"
  - "phase-II-todo-full-stack-web-app/backend/auth/better-auth-config.ts"
  - "phase-II-todo-full-stack-web-app/frontend/src/lib/ba-schema.ts"
tests:
  - "phase-II-todo-full-stack-web-app/frontend/test-fix.js"
---

## Prompt

Fix the Better Auth registration issue where registration returns HTTP 200 success with session tokens, but user records are not persisting to the Neon PostgreSQL database. The user registration appears to succeed but no user record appears in the database. Database connectivity is confirmed and manual inserts work, so the database itself is functioning correctly.

## Response snapshot

Fixed Better Auth adapter configuration by removing the incorrect provider: "pg" specification when using Neon HTTP driver. The issue was a fundamental mismatch between using Neon HTTP driver but specifying PG provider, which caused silent failures in database operations. Changed the adapter configuration from drizzleAdapter(db, {provider: "pg"}) to drizzleAdapter(db) and ensured proper schema mapping was provided to the drizzle instance.

## Outcome

- ✅ Impact: Fixed drizzle adapter provider mismatch that was causing silent database operation failures
- 🧪 Tests: Created test-fix.js to verify the registration functionality now persists users to database
- 📁 Files: Updated auth.ts in both frontend and backend with proper adapter config, enhanced ba-schema.ts with proper table definitions
- 🔁 Next prompts: Verify registration works in production environment, test complete auth flow
- 🧠 Reflection: The issue was a fundamental mismatch between using Neon HTTP driver but specifying PG provider, which caused silent failures in database operations

## Evaluation notes (flywheel)

- Failure modes observed: Better Auth with Neon HTTP driver requires proper schema mapping and correct adapter configuration, avoid using provider: "pg" with Neon HTTP driver
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Deploy to production and verify registration persists users to database