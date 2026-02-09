# Testing Instructions

## Quick Start Testing

Follow these steps to test the integrated Todo application locally.

---

## Step 1: Start the Application

### Using Docker (Easiest)

```bash
# Navigate to project directory
cd phase-II-todo-full-stack-web-app

# Start all services
docker-compose up -d

# Wait 30 seconds for services to initialize

# Check status
docker-compose ps

# All services should show "Up" status
```

### Using Manual Scripts

```bash
# Navigate to project directory
cd phase-II-todo-full-stack-web-app

# Make scripts executable (first time only)
chmod +x start.sh stop.sh

# Start the application
./start.sh

# Wait for services to start (about 30 seconds)
```

---

## Step 2: Verify Services Are Running

### Check Backend

```bash
# Test health endpoint
curl http://localhost:8000/health

# Expected response: {"status": "healthy"}
```

### Check Frontend

Open your browser and navigate to:
- http://localhost:3000

You should see the Todo application landing page.

### Check API Documentation

Open your browser and navigate to:
- http://localhost:8000/docs

You should see the Swagger UI with all API endpoints.

---

## Step 3: Test User Registration

### Via Frontend (Recommended)

1. Open http://localhost:3000
2. Click "Sign Up" or "Register"
3. Fill in the form:
   - **Email**: test@example.com
   - **Password**: Test123!@#
   - **Name**: Test User
4. Click "Create Account"
5. You should be redirected to the dashboard

### Via API (Alternative)

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test123!@#",
    "name": "Test User"
  }'
```

Expected response:
```json
{
  "user": {
    "id": "...",
    "email": "test@example.com",
    "name": "Test User"
  },
  "token": "eyJ..."
}
```

---

## Step 4: Test User Login

### Via Frontend

1. If not already logged in, click "Login"
2. Enter credentials:
   - **Email**: test@example.com
   - **Password**: Test123!@#
3. Click "Sign In"
4. You should be redirected to the dashboard

### Via API

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test123!@#"
  }'
```

Save the token from the response for API testing.

---

## Step 5: Test Task Management

### Create a Task

**Via Frontend:**
1. Click "New Task" or "Add Task" button
2. Fill in the form:
   - **Title**: "My First Task"
   - **Description**: "Testing the application"
   - **Priority**: High
   - **Due Date**: Tomorrow
3. Click "Create"
4. Task should appear in the list

**Via API:**
```bash
# Replace TOKEN with your JWT token from login
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TOKEN" \
  -d '{
    "title": "My First Task",
    "description": "Testing the application",
    "priority": "high",
    "completed": false
  }'
```

### View Tasks

**Via Frontend:**
- Tasks should be visible on the dashboard
- Check that your task appears in the list

**Via API:**
```bash
curl -X GET http://localhost:8000/api/tasks \
  -H "Authorization: Bearer TOKEN"
```

### Update a Task

**Via Frontend:**
1. Click on a task to open it
2. Click "Edit" button
3. Modify the title or description
4. Click "Save"
5. Changes should be reflected immediately

**Via API:**
```bash
# Replace TASK_ID with actual task ID
curl -X PUT http://localhost:8000/api/tasks/TASK_ID \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TOKEN" \
  -d '{
    "title": "Updated Task Title",
    "description": "Updated description"
  }'
```

### Mark Task as Complete

**Via Frontend:**
1. Click the checkbox next to a task
2. Task should show as completed (strikethrough or different style)

**Via API:**
```bash
curl -X PATCH http://localhost:8000/api/tasks/TASK_ID/status \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TOKEN" \
  -d '{
    "completed": true
  }'
```

### Delete a Task

**Via Frontend:**
1. Click the delete button (trash icon) on a task
2. Confirm deletion if prompted
3. Task should disappear from the list

**Via API:**
```bash
curl -X DELETE http://localhost:8000/api/tasks/TASK_ID \
  -H "Authorization: Bearer TOKEN"
```

---

## Step 6: Test Filters and Sorting

### Via Frontend

1. **Filter by Status**:
   - Click "Status" dropdown
   - Select "Completed" or "In Progress"
   - Only matching tasks should display

2. **Filter by Priority**:
   - Click "Priority" dropdown
   - Select a priority level
   - Only matching tasks should display

3. **Sort Tasks**:
   - Click "Sort" dropdown
   - Select sort option (Date, Priority, Title)
   - Tasks should reorder accordingly

4. **Clear Filters**:
   - Click "Clear Filters" button
   - All tasks should display again

---

## Step 7: Test Responsive Design

### Desktop View
1. Open application in full-screen browser
2. Verify layout looks good
3. Check that all elements are accessible

### Tablet View
1. Resize browser to tablet width (768px)
2. Verify layout adapts
3. Check navigation menu

### Mobile View
1. Resize browser to mobile width (375px)
2. Verify layout is mobile-friendly
3. Check hamburger menu works
4. Test touch interactions

---

## Step 8: Test Dark Mode

1. Look for dark mode toggle (usually in header/settings)
2. Click to toggle dark mode
3. Verify all colors change appropriately
4. Check text is readable in both modes

---

## Step 9: Test User Isolation

### Create Second User

1. Logout from first account
2. Register a new user:
   - **Email**: test2@example.com
   - **Password**: Test123!@#
   - **Name**: Test User 2
3. Create some tasks for this user

### Verify Isolation

1. Login as first user (test@example.com)
2. Verify you only see your own tasks
3. Verify you cannot see test2's tasks
4. Login as second user (test2@example.com)
5. Verify you only see your own tasks

---

## Step 10: Test Error Handling

### Test Invalid Login

1. Try to login with wrong password
2. Verify error message displays
3. Verify you remain on login page

### Test Unauthorized Access

1. Logout
2. Try to access dashboard directly
3. Verify you're redirected to login

### Test Network Errors

1. Stop the backend: `docker-compose stop backend`
2. Try to create a task in frontend
3. Verify error message displays
4. Restart backend: `docker-compose start backend`

---

## Step 11: View Logs

### Docker Logs

```bash
# View all logs
docker-compose logs -f

# View backend logs only
docker-compose logs -f backend

# View frontend logs only
docker-compose logs -f frontend
```

### Manual Setup Logs

```bash
# Backend logs
tail -f logs/backend.log

# Frontend logs
tail -f logs/frontend.log
```

---

## Step 12: Stop the Application

### Docker

```bash
docker-compose down
```

### Manual

```bash
./stop.sh
```

---

## Testing Checklist

Use this checklist to track your testing progress:

### Setup
- [ ] Application starts without errors
- [ ] Backend responds on port 8000
- [ ] Frontend responds on port 3000
- [ ] Database connection works

### Authentication
- [ ] User registration works
- [ ] User login works
- [ ] JWT token is issued
- [ ] Protected routes require authentication
- [ ] Logout clears session

### Task Management
- [ ] Create task works
- [ ] View tasks works
- [ ] Update task works
- [ ] Delete task works
- [ ] Mark as complete works

### Filters and Sorting
- [ ] Status filter works
- [ ] Priority filter works
- [ ] Sort by date works
- [ ] Sort by priority works
- [ ] Clear filters works

### UI/UX
- [ ] Responsive design works
- [ ] Dark mode works
- [ ] Animations are smooth
- [ ] Loading states display
- [ ] Error messages show

### Security
- [ ] User isolation works
- [ ] Unauthorized access blocked
- [ ] Invalid credentials rejected
- [ ] CORS allows frontend requests

### Performance
- [ ] Page loads quickly
- [ ] API responses are fast
- [ ] No console errors
- [ ] No memory leaks

---

## Common Issues and Solutions

### Backend Won't Start

**Issue**: Database connection error
```
Solution:
1. Check PostgreSQL is running: pg_isready
2. Verify DATABASE_URL in backend/.env
3. Ensure database exists: psql -l | grep todo_db
```

**Issue**: Port 8000 already in use
```
Solution:
1. Find process: lsof -i :8000
2. Kill process or use different port
```

### Frontend Won't Start

**Issue**: Cannot connect to backend
```
Solution:
1. Verify backend is running: curl http://localhost:8000/health
2. Check NEXT_PUBLIC_API_URL in frontend/.env
3. Check browser console for CORS errors
```

**Issue**: Port 3000 already in use
```
Solution:
1. Use different port: PORT=3001 npm run dev
2. Or kill existing process
```

### Docker Issues

**Issue**: Containers won't start
```
Solution:
1. Check logs: docker-compose logs
2. Rebuild: docker-compose build --no-cache
3. Remove volumes: docker-compose down -v
```

---

## Success Criteria

Testing is successful when:

✅ All services start without errors
✅ User can register and login
✅ User can create, view, update, and delete tasks
✅ Filters and sorting work correctly
✅ Responsive design works on all screen sizes
✅ User isolation is enforced
✅ Error handling works properly
✅ No console errors or warnings

---

## Next Steps After Testing

1. **Report Issues**: Document any bugs or issues found
2. **Performance Review**: Note any slow operations
3. **UX Feedback**: Suggest improvements to user experience
4. **Security Review**: Verify all security features work
5. **Deployment Preparation**: Prepare for production deployment

---

**Happy Testing!** 🎉

If you encounter any issues, refer to:
- [LOCAL_TESTING_GUIDE.md](./LOCAL_TESTING_GUIDE.md)
- [INTEGRATION_SUMMARY.md](./INTEGRATION_SUMMARY.md)
- [INTEGRATION_COMPLETE.md](./INTEGRATION_COMPLETE.md)
