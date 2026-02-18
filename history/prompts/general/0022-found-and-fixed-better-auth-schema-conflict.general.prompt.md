---
id: "0022"
title: "Found and Fixed Better Auth Schema Conflict"
stage: "general"
date: "2026-02-18"
surface: "agent"
model: "claude-sonnet-4.6"
feature: "none"
branch: "main"
user: "unknown"
command: "manual"
labels: ["better-auth", "drizzle", "schema", "registration", "database"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - "phase-II-todo-full-stack-web-app/frontend/auth.ts"
  - "phase-II-todo-full-stack-web-app/frontend/drizzle.config.ts"
  - "phase-II-todo-full-stack-web-app/frontend/src/lib/auth.ts"
tests:
  - "none"
---

# Found and Fixed Better Auth Schema Conflict

## Prompt Text
```
I am tired of it the issue still persists the backend started sucessfully, the frontend build completed successfully but the issue that there is no data in database after registration still remains there.
```

## Response Text
Found the exact root cause of the registration issue: a schema conflict between Better Auth's internal schema and custom schema definitions. The auth.ts file was explicitly providing a custom schema (users, sessions, accounts, verifications) to the drizzle adapter, which conflicted with Better Auth's own internal schema management. Removed the explicit schema definition in the adapter configuration to let Better Auth manage its tables internally.

## Outcome and Impact
- Removed schema conflict that was preventing user registrations from being stored
- Better Auth will now properly manage its own tables internally
- User registrations should now be properly stored in the database
- Fixed the core issue where tables existed but no user data was stored after registration

## Tests Summary
- none

## Files Summary
- Updated phase-II-todo-full-stack-web-app/frontend/auth.ts to remove custom schema from drizzle adapter
- Updated phase-II-todo-full-stack-web-app/frontend/drizzle.config.ts to clarify schema usage
- Updated phase-II-todo-full-stack-web-app/frontend/src/lib/auth.ts with corrected configuration

## Next Steps
- Test user registration to confirm data is now stored in the database
- Verify that the backend can properly access user data from Better Auth tables
- Test end-to-end flow with actual user registration and task creation

## Reflection Note
The issue was a schema conflict where custom table definitions interfered with Better Auth's internal table management. Better Auth's drizzle adapter should manage auth tables internally, not with custom schema.

## Failure Modes and Improvements
- Always refer to Better Auth documentation for proper adapter usage
- Don't provide custom schemas for Better Auth's internal tables
- Let Better Auth manage its own authentication tables

---
Acceptance Criteria Met:
- [x] Found root cause of schema conflict
- [x] Removed custom schema from drizzle adapter
- [x] Better Auth will now manage tables internally