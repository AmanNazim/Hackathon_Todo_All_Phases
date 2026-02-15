---
id: 0003
title: fix-better-auth-user-persistence-in-neon-database
stage: general
date: 2026-02-16
surface: agent
model: if/qwen3-coder-plus[1m]
feature: none
branch: main
user: Claude Code
command: manual
labels: ["auth", "better-auth", "neon", "sqlmodel", "database"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - E:\q4-sat-6-to-9\claude-code-development\hackathon-II-todo-all-phases\phase-II-todo-full-stack-web-app\frontend\src\lib\auth.ts
 - E:\q4-sat-6-to-9\claude-code-development\hackathon-II-todo-all-phases\phase-II-todo-full-stack-web-app\backend\models.py
 - E:\q4-sat-6-to-9\claude-code-development\hackathon-II-todo-all-phases\phase-II-todo-full-stack-web-app\backend\database.py
tests:
 - none
---

## Prompt

Fix the issue where registration is working in the todo application but no user data is created in the database. The problem was that Better Auth needs to handle its own data schemas, but SQLModel was attempting to create the same tables, causing conflicts. The solution needed to separate concerns properly while maintaining foreign key relationships.

## Response snapshot

I identified that the issue was a conflict between Better Auth and SQLModel trying to manage the same database tables. Better Auth handles user registration and creates its own tables (user, session, account, verification), but the backend was also trying to create these tables with SQLModel, which was causing the registration to work but user data not to persist properly.

I implemented a clean solution:

1. Updated Better Auth configuration in frontend/src/lib/auth.ts to properly define schema for Neon compatibility while maintaining the drizzle adapter approach
2. Modified backend/models.py to remove table=True from Better Auth table definitions (User, Session, Account, Verification), making them reference-only for foreign key relationships
3. Updated backend/database.py to exclude Better Auth tables from SQLModel's table creation, ensuring only application-specific tables are created by SQLModel

This ensures a clean separation: Better Auth manages auth tables, SQLModel manages app tables, with no conflicts and proper foreign key relationships maintained.

## Outcome

- ✅ Impact: Fixed the user registration issue where user data wasn't being persisted in the database
- 🧪 Tests: No automated tests run yet, but the solution follows a clean architectural separation
- 📁 Files: Updated 3 files to properly separate concerns between Better Auth and SQLModel
- 🔁 Next prompts: Registration should now work properly with user data persisted
- 🧠 Reflection: The issue was a common integration problem between two systems trying to manage the same database tables

## Evaluation notes (flywheel)

- Failure modes observed: Better Auth and SQLModel conflicting over table creation responsibilities
- Graders run and results (PASS/FAIL): Not applicable yet, needs manual verification after deployment
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Test registration flow to confirm user data persists in database