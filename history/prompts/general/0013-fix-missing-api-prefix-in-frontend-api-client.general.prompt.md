---
id: 0013
title: Fix missing /api prefix in frontend API client
stage: green
date: 2026-05-16
surface: agent
model: claude-opus-4-7
feature: none
branch: main
user: AmanNazim
command: Fix 404 error on tasks page due to missing /api prefix
labels: ["frontend", "api", "fix", "routes"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - phase-II-todo-full-stack-web-app/frontend/src/lib/api.ts
  - phase-II-todo-full-stack-web-app/frontend/.env.production
tests:
  - None yet - needs testing in browser
---

## Prompt

Now I have changed the connection string and hugging face backend is running but the new error appeard in tasks page: Failed to load resource: the server responded with a status of 404 ()
GET https://aman778-todo-full-stack-web-app-backend.hf.space/v1/users/ih0BdtSiTMxriD9eNtRfc1jQqvvDyzMC/tasks 404 (Not Found).

## Response snapshot

Fixed the 404 error by ensuring the frontend API client always includes the /api prefix in the base URL. The backend expects routes like /api/v1/users/{user_id}/tasks but the frontend was calling /v1/users/{user_id}/tasks (missing /api).

## Outcome

- ✅ Impact: Fixed the 404 error by ensuring /api prefix is always included in API base URL.
- 🧪 Tests: Needs testing in browser to verify tasks page loads correctly.
- 📁 Files: Updated api.ts with getApiBaseUrl() function and .env.production with /api prefix.
- 🔁 Next prompts: Test the task page in the browser to verify the fix works.
- 🧠 Reflection: The issue was that the production API URL didn't include /api prefix, causing the frontend to call wrong endpoints.

## Evaluation notes (flywheel)

- Failure modes observed: Frontend calling /v1/users/... instead of /api/v1/users/...
- Graders run and results (PASS/FAIL): Not yet tested
- Prompt variant (if applicable): 
- Next experiment (smallest change to try): Test in browser to verify the fix works.