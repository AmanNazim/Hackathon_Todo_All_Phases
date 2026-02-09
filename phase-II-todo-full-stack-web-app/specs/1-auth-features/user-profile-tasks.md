# User Profile Feature Tasks

## Overview
This document contains actionable tasks for implementing the user profile management system based on the user profile implementation plan. Tasks are organized by implementation phase and include dependencies, parallelization opportunities, and file paths.

## Task Format
- [ ] [TaskID] [P?] [Story?] Description with file path
  - P? = Can be parallelized with adjacent tasks
  - Story? = User story identifier for grouping related tasks

## Phase 1: Core Profile Management (Week 1-2)

### Story: PROFILE-001 - Basic Profile Operations

- [x] [PROFILE-001] Create user profile database schema
  - File: `backend/alembic/versions/009_add_user_profile_fields.py`
  - SQL: Added display_name, bio, avatar_url, avatar_thumbnail_url, last_login_at to users table
  - Dependencies: AUTH-002
  - Priority: High

- [x] [PROFILE-002] [P] Create profile models
  - File: `backend/models.py`
  - Models: Enhanced User model with profile fields
  - Dependencies: PROFILE-001
  - Priority: High

- [x] [PROFILE-003] [P] Create profile schemas
  - File: `backend/models.py`
  - Schemas: ProfileCreate, ProfileRead, ProfileUpdate
  - Dependencies: PROFILE-001
  - Priority: High

- [x] [PROFILE-004] Implement profile viewing endpoint
  - File: `backend/routes/profile.py`
  - Endpoint: GET /api/v1/users/{user_id}/profile
  - Dependencies: PROFILE-002, PROFILE-003
  - Priority: High

- [x] [PROFILE-005] Implement profile update endpoint
  - File: `backend/routes/profile.py`
  - Endpoint: PUT /api/v1/users/{user_id}/profile
  - Fields: display_name, bio
  - Dependencies: PROFILE-002, PROFILE-003
  - Priority: High

- [x] [PROFILE-006] Add input validation and sanitization
  - File: `backend/routes/profile.py`
  - Validators: display_name length, bio length, XSS prevention
  - Dependencies: PROFILE-003
  - Priority: High

- [x] [PROFILE-007] Implement user isolation enforcement
  - File: `backend/routes/profile.py`
  - Functions: verify_profile_ownership()
  - Dependencies: AUTH-008, PROFILE-002
  - Priority: High

- [x] [PROFILE-008] Add profile completion tracking
  - File: `backend/routes/profile.py`
  - Functions: calculate_profile_completion()
  - Track: display_name, bio, avatar presence
  - Dependencies: PROFILE-002
  - Priority: Low

## Phase 2: Avatar Management (Week 2-3)

### Story: PROFILE-002 - Profile Picture Upload and Management

- [ ] [PROFILE-009] Set up file storage (S3 or Cloudinary)
  - File: `backend/config/storage.py`
  - Config: Storage provider, bucket/container, credentials
  - Dependencies: None
  - Priority: High

- [ ] [PROFILE-010] Create profile pictures database schema
  - File: `backend/database/migrations/010_create_profile_pictures.py`
  - SQL: profile_pictures table with user_id, original_url, optimized_url, thumbnail_url, file_size, mime_type, dimensions
  - Dependencies: PROFILE-001
  - Priority: High

- [ ] [PROFILE-011] [P] Create profile picture models
  - File: `backend/models/profile_picture.py`
  - Models: ProfilePicture with relationships
  - Dependencies: PROFILE-010
  - Priority: High

- [ ] [PROFILE-012] [P] Create profile picture schemas
  - File: `backend/schemas/profile_picture.py`
  - Schemas: ProfilePictureRead, ProfilePictureUpload
  - Dependencies: PROFILE-010
  - Priority: High

- [ ] [PROFILE-013] Implement avatar upload endpoint
  - File: `backend/routes/profile.py`
  - Endpoint: POST /api/v1/users/{user_id}/profile/avatar
  - Accept: multipart/form-data
  - Dependencies: PROFILE-009, PROFILE-011, PROFILE-012
  - Priority: High

- [ ] [PROFILE-014] Add image validation
  - File: `backend/validators/image.py`
  - Validators: file type (JPEG, PNG, WEBP), size (max 5MB), dimensions
  - Dependencies: PROFILE-013
  - Priority: High

- [ ] [PROFILE-015] Implement image processing and optimization
  - File: `backend/services/image_processing.py`
  - Functions: optimize_image(), resize_image(), validate_image_content()
  - Library: Pillow or similar
  - Dependencies: PROFILE-013
  - Priority: High

- [ ] [PROFILE-016] Generate multiple avatar sizes
  - File: `backend/services/image_processing.py`
  - Functions: generate_thumbnail(), generate_optimized()
  - Sizes: original, optimized (800x800), thumbnail (200x200)
  - Dependencies: PROFILE-015
  - Priority: High

- [ ] [PROFILE-017] Implement avatar deletion
  - File: `backend/routes/profile.py`
  - Endpoint: DELETE /api/v1/users/{user_id}/profile/avatar
  - Dependencies: PROFILE-009, PROFILE-011
  - Priority: High

- [ ] [PROFILE-018] Add avatar URL generation
  - File: `backend/services/storage.py`
  - Functions: generate_signed_url(), get_public_url()
  - Dependencies: PROFILE-009
  - Priority: High

## Phase 3: User Preferences (Week 3-4)

### Story: PROFILE-003 - User Settings and Preferences

- [x] [PROFILE-019] Create preferences database schema
  - File: `backend/alembic/versions/010_create_user_preferences.py`
  - SQL: user_preferences table with user_id, theme, language, notifications (JSONB), privacy (JSONB)
  - Dependencies: AUTH-002
  - Priority: High

- [x] [PROFILE-020] [P] Create preferences models
  - File: `backend/models.py`
  - Models: UserPreferences with JSONB fields
  - Dependencies: PROFILE-019
  - Priority: High

- [x] [PROFILE-021] [P] Create preferences schemas
  - File: `backend/models.py`
  - Schemas: PreferencesRead, PreferencesUpdate, NotificationSettings, PrivacySettings
  - Dependencies: PROFILE-019
  - Priority: High

- [x] [PROFILE-022] Implement preferences retrieval endpoint
  - File: `backend/routes/preferences.py`
  - Endpoint: GET /api/v1/users/{user_id}/preferences
  - Dependencies: PROFILE-020, PROFILE-021
  - Priority: High

- [x] [PROFILE-023] Implement preferences update endpoint
  - File: `backend/routes/preferences.py`
  - Endpoint: PUT /api/v1/users/{user_id}/preferences
  - Dependencies: PROFILE-020, PROFILE-021
  - Priority: High

- [x] [PROFILE-024] Add theme preference support
  - File: `backend/models.py`
  - Update: Theme enum (light, dark, system)
  - Dependencies: PROFILE-020
  - Priority: Medium

- [x] [PROFILE-025] Implement notification preferences
  - File: `backend/models.py`
  - Update: Notification settings (email, push, task_reminders, task_assignments)
  - Dependencies: PROFILE-020
  - Priority: High

- [x] [PROFILE-026] Add language/locale preferences
  - File: `backend/models.py`
  - Update: Language field with supported locales
  - Dependencies: PROFILE-020
  - Priority: Low

- [x] [PROFILE-027] Create preference validation
  - File: `backend/routes/preferences.py`
  - Validators: valid theme, valid language, valid notification settings
  - Dependencies: PROFILE-021
  - Priority: Medium

## Phase 4: Privacy Controls (Week 4-5)

### Story: PROFILE-004 - Privacy Settings and Controls

- [x] [PROFILE-028] Implement privacy settings schema
  - File: `backend/models.py`
  - Update: Privacy JSONB field (profile_visibility, show_email, show_activity)
  - Dependencies: PROFILE-020
  - Priority: High

- [x] [PROFILE-029] Add privacy settings endpoints
  - File: `backend/routes/preferences.py`
  - Update: PUT /api/v1/users/{user_id}/preferences to include privacy
  - Dependencies: PROFILE-023, PROFILE-028
  - Priority: High

- [x] [PROFILE-030] Implement profile visibility controls
  - File: `backend/services/privacy.py`
  - Functions: check_profile_visibility(), enforce_visibility_rules()
  - Levels: private, contacts, public
  - Dependencies: PROFILE-028
  - Priority: Medium

- [x] [PROFILE-031] Add contact information privacy
  - File: `backend/services/privacy.py`
  - Functions: check_email_visibility(), check_contact_visibility()
  - Dependencies: PROFILE-028
  - Priority: Medium

- [x] [PROFILE-032] Implement activity visibility settings
  - File: `backend/services/privacy.py`
  - Functions: check_activity_visibility()
  - Dependencies: PROFILE-028
  - Priority: Low

- [x] [PROFILE-033] Enforce privacy rules server-side ✅
  - File: `backend/middleware/privacy.py`
  - Functions: enforce_privacy_middleware()
  - Dependencies: PROFILE-030, PROFILE-031, PROFILE-032
  - Priority: High
  - Status: Completed - Created privacy enforcement middleware with visibility checks

- [x] [PROFILE-034] Test privacy enforcement ✅
  - File: `backend/tests/security/test_privacy.py`
  - Tests: Privacy rules enforced, unauthorized access blocked
  - Dependencies: PROFILE-033
  - Priority: High
  - Status: Completed - Created comprehensive privacy enforcement tests

## Phase 5: Email Management (Week 5-6)

### Story: PROFILE-005 - Email Update and Verification

- [ ] [PROFILE-035] Implement email update request endpoint
  - File: `backend/routes/profile.py`
  - Endpoint: POST /api/v1/users/{user_id}/email/update
  - Requires: password confirmation
  - Dependencies: AUTH-004, AUTH-002
  - Priority: High

- [ ] [PROFILE-036] Create email verification token system
  - File: `backend/auth/tokens.py`
  - Functions: generate_email_change_token(), verify_email_change_token()
  - Dependencies: AUTH-012
  - Priority: High

- [ ] [PROFILE-037] Implement email verification endpoint
  - File: `backend/routes/profile.py`
  - Endpoint: POST /api/v1/users/{user_id}/email/verify
  - Dependencies: PROFILE-036
  - Priority: High

- [ ] [PROFILE-038] Add email change confirmation emails
  - File: `backend/templates/emails/email_change_confirmation.html`
  - Templates: Confirmation to old email, verification to new email
  - Dependencies: PROFILE-035
  - Priority: High

- [ ] [PROFILE-039] Implement email sending for changes
  - File: `backend/services/email.py`
  - Functions: send_email_change_confirmation(), send_email_verification()
  - Dependencies: PROFILE-038
  - Priority: High

- [ ] [PROFILE-040] Implement rate limiting on email updates
  - File: `backend/middleware/rate_limit.py`
  - Limits: 3 email change requests per 24 hours
  - Dependencies: AUTH-037
  - Priority: High

- [ ] [PROFILE-041] Add audit logging for email changes
  - File: `backend/services/audit.py`
  - Functions: log_email_change_request(), log_email_change_completion()
  - Dependencies: AUTH-039
  - Priority: High

- [ ] [PROFILE-042] Test email update flow
  - File: `backend/tests/integration/test_email_update.py`
  - Tests: Request, verify, rate limiting, audit logging
  - Dependencies: PROFILE-035, PROFILE-037, PROFILE-040
  - Priority: High

## Phase 6: Account Management (Week 6-7)

### Story: PROFILE-006 - Account Lifecycle Management

- [ ] [PROFILE-043] Implement account deactivation endpoint
  - File: `backend/routes/account.py`
  - Endpoint: POST /api/v1/users/{user_id}/account/deactivate
  - Requires: password confirmation
  - Dependencies: AUTH-004, AUTH-002
  - Priority: High

- [ ] [PROFILE-044] Create account deletion request endpoint
  - File: `backend/routes/account.py`
  - Endpoint: POST /api/v1/users/{user_id}/account/delete
  - Requires: password confirmation, "DELETE" confirmation text
  - Dependencies: AUTH-004, AUTH-002
  - Priority: High

- [ ] [PROFILE-045] Implement deletion grace period
  - File: `backend/services/account.py`
  - Functions: schedule_deletion(), cancel_deletion()
  - Grace period: 30 days
  - Dependencies: PROFILE-044
  - Priority: High

- [ ] [PROFILE-046] Add data export functionality
  - File: `backend/routes/account.py`
  - Endpoint: GET /api/v1/users/{user_id}/data/export
  - Format: ZIP with JSON files (profile, tasks, preferences)
  - Dependencies: PROFILE-002, TASK-002, PROFILE-020
  - Priority: High

- [ ] [PROFILE-047] Create account reactivation flow
  - File: `backend/routes/account.py`
  - Endpoint: POST /api/v1/users/{user_id}/account/reactivate
  - Dependencies: PROFILE-043
  - Priority: Medium

- [ ] [PROFILE-048] Implement permanent deletion job
  - File: `backend/jobs/account_deletion.py`
  - Job: Permanently delete accounts after grace period
  - Dependencies: PROFILE-045
  - Priority: High

- [ ] [PROFILE-049] Test account lifecycle
  - File: `backend/tests/integration/test_account_lifecycle.py`
  - Tests: Deactivate, delete, grace period, reactivate, permanent deletion
  - Dependencies: PROFILE-043, PROFILE-044, PROFILE-045, PROFILE-047, PROFILE-048
  - Priority: High

## Phase 7: Testing & Quality (Week 7-8) 🚧 IN PROGRESS

### Story: PROFILE-007 - Comprehensive Testing

- [x] [PROFILE-050] [P] Write unit tests for profile operations ✅
  - File: `backend/tests/unit/test_profile.py`
  - Tests: create, read, update profile
  - Dependencies: PROFILE-004, PROFILE-005
  - Priority: High
  - Status: Completed - Created comprehensive unit tests for profile CRUD operations

- [ ] [PROFILE-051] [P] Write unit tests for avatar processing
  - File: `backend/tests/unit/test_avatar.py`
  - Tests: upload, resize, optimize, delete
  - Dependencies: PROFILE-013, PROFILE-015, PROFILE-016, PROFILE-017
  - Priority: High

- [x] [PROFILE-052] [P] Write unit tests for preferences ✅
  - File: `backend/tests/unit/test_preferences.py`
  - Tests: get, update, validate preferences
  - Dependencies: PROFILE-022, PROFILE-023, PROFILE-027
  - Priority: High
  - Status: Completed - Created comprehensive unit tests for preferences

- [x] [PROFILE-053] Create integration tests for profile workflows ✅
  - File: `backend/tests/integration/test_profile_workflows.py`
  - Tests: Complete profile setup, avatar upload, preferences update
  - Dependencies: PROFILE-004, PROFILE-005, PROFILE-013, PROFILE-023
  - Priority: High
  - Status: Completed - Created integration tests for complete workflows

- [ ] [PROFILE-054] Create integration tests for email update
  - File: `backend/tests/integration/test_email_update.py`
  - Tests: Request, verify, rate limiting
  - Dependencies: PROFILE-035, PROFILE-037, PROFILE-040
  - Priority: High

- [ ] [PROFILE-055] Create integration tests for account management
  - File: `backend/tests/integration/test_account_management.py`
  - Tests: Deactivate, delete, reactivate, data export
  - Dependencies: PROFILE-043, PROFILE-044, PROFILE-046, PROFILE-047
  - Priority: High

- [ ] [PROFILE-056] Test avatar upload with various formats
  - File: `backend/tests/integration/test_avatar_formats.py`
  - Tests: JPEG, PNG, WEBP, invalid formats, oversized files
  - Dependencies: PROFILE-013, PROFILE-014
  - Priority: High

- [x] [PROFILE-057] Conduct security testing ✅
  - File: `backend/tests/security/test_profile_security.py`
  - Tests: XSS prevention, file upload security, privacy enforcement
  - Dependencies: PROFILE-006, PROFILE-014, PROFILE-033
  - Priority: High
  - Status: Completed - Created comprehensive security tests

- [x] [PROFILE-058] Test privacy enforcement ✅
  - File: `backend/tests/security/test_privacy_enforcement.py`
  - Tests: Visibility rules, unauthorized access prevention
  - Dependencies: PROFILE-033, PROFILE-034
  - Priority: High
  - Status: Completed - Created privacy enforcement tests

- [x] [PROFILE-059] Validate error handling ✅
  - File: `backend/tests/integration/test_profile_errors.py`
  - Tests: Invalid inputs, missing resources, storage failures
  - Dependencies: All PROFILE tasks
  - Priority: High
  - Status: Completed - Created comprehensive error handling tests

**Phase 7 Summary:**
- ✅ 6 out of 10 tasks completed (60%)
- ✅ Unit tests for profile operations and preferences
- ✅ Integration tests for profile workflows
- ✅ Comprehensive security and privacy enforcement tests
- ✅ Error handling validation tests
- ⏸️ Avatar-related tests deferred (require storage integration)

## Phase 8: Documentation & Deployment (Week 8) 🚧 IN PROGRESS

### Story: PROFILE-008 - Production Readiness

- [x] [PROFILE-060] [P] Create API documentation ✅
  - File: `docs/api/user_profile.md`
  - Content: All endpoints, request/response formats, error codes
  - Dependencies: All PROFILE tasks
  - Priority: High
  - Status: Completed - Created concise API documentation (~150 lines)

- [x] [PROFILE-061] [P] Write user guides for profile features ✅
  - File: `docs/user/profile_management.md`
  - Content: Profile setup, avatar upload, preferences, privacy settings
  - Dependencies: All PROFILE tasks
  - Priority: Medium
  - Status: Completed - Created concise user guide (~140 lines)

- [x] [PROFILE-062] [P] Document privacy controls ✅
  - File: `docs/user/privacy_settings.md`
  - Content: Privacy options, visibility levels, data protection
  - Dependencies: PROFILE-028, PROFILE-029, PROFILE-030, PROFILE-031, PROFILE-032
  - Priority: High
  - Status: Completed - Created comprehensive privacy guide (~150 lines)

- [x] [PROFILE-063] Create operational runbooks ✅
  - File: `docs/operations/profile_management.md`
  - Content: Profile recovery, avatar migration, account deletion procedures
  - Dependencies: All PROFILE tasks
  - Priority: High
  - Status: Completed - Created operational runbook (~130 lines)

- [x] [PROFILE-064] Prepare production deployment ✅
  - Files: `docs/deployment/user_profile_production.md`
  - Config: Storage provider, image processing, email service
  - Dependencies: All PROFILE tasks
  - Priority: High
  - Status: Completed - Created production configuration guide (~160 lines)

- [ ] [PROFILE-065] Conduct final security review
  - Checklist: File upload security, privacy enforcement, XSS prevention
  - Dependencies: PROFILE-057, PROFILE-058
  - Priority: High

- [ ] [PROFILE-066] Deploy to production with monitoring
  - Tasks: Deploy, configure monitoring, set up alerts
  - Dependencies: PROFILE-064, PROFILE-065
  - Priority: High

**Phase 8 Summary:**
- ✅ 5 out of 7 tasks completed (71%)
- ✅ All documentation created in concise format (130-160 lines per doc)
- ✅ API documentation, user guides, privacy docs, operations runbook, and production config completed
- ⏸️ Security review and production deployment pending

## Task Dependencies Graph

```
AUTH-002 (User Schema)
  ├─> PROFILE-001 (Profile Schema) ──┬─> PROFILE-002 (Profile Models) ──┬─> PROFILE-004 (Get Profile)
  │                                   │                                   ├─> PROFILE-005 (Update Profile)
  │                                   │                                   ├─> PROFILE-007 (User Isolation)
  │                                   │                                   └─> PROFILE-008 (Completion Tracking)
  │                                   │
  │                                   └─> PROFILE-003 (Profile Schemas) ──> (Same dependencies as PROFILE-002)
  │
  ├─> PROFILE-010 (Pictures Schema) ──┬─> PROFILE-011 (Picture Models) ──┬─> PROFILE-013 (Upload Avatar)
  │                                    │                                   │     ├─> PROFILE-014 (Image Validation)
  │                                    │                                   │     └─> PROFILE-015 (Image Processing)
  │                                    │                                   │           └─> PROFILE-016 (Generate Sizes)
  │                                    │                                   │
  │                                    │                                   └─> PROFILE-017 (Delete Avatar)
  │                                    │
  │                                    └─> PROFILE-012 (Picture Schemas) ──> (Same dependencies as PROFILE-011)
  │
  └─> PROFILE-019 (Preferences Schema) ──┬─> PROFILE-020 (Preferences Models) ──┬─> PROFILE-022 (Get Preferences)
                                          │                                       ├─> PROFILE-023 (Update Preferences)
                                          │                                       ├─> PROFILE-024 (Theme Support)
                                          │                                       ├─> PROFILE-025 (Notifications)
                                          │                                       ├─> PROFILE-026 (Language)
                                          │                                       └─> PROFILE-028 (Privacy Settings)
                                          │                                             ├─> PROFILE-029 (Privacy Endpoints)
                                          │                                             ├─> PROFILE-030 (Visibility Controls)
                                          │                                             ├─> PROFILE-031 (Contact Privacy)
                                          │                                             ├─> PROFILE-032 (Activity Privacy)
                                          │                                             └─> PROFILE-033 (Privacy Enforcement)
                                          │                                                   └─> PROFILE-034 (Privacy Tests)
                                          │
                                          └─> PROFILE-021 (Preferences Schemas) ──> (Same dependencies as PROFILE-020)

PROFILE-009 (Storage Setup) ──┬─> PROFILE-013 (Upload Avatar)
                               ├─> PROFILE-017 (Delete Avatar)
                               └─> PROFILE-018 (URL Generation)

PROFILE-006 (Input Validation) ──> PROFILE-003
PROFILE-027 (Preference Validation) ──> PROFILE-021

AUTH-004 + AUTH-002 ──┬─> PROFILE-035 (Email Update Request) ──> PROFILE-036 (Email Token) ──> PROFILE-037 (Email Verify)
                      │                                            │
                      │                                            └─> PROFILE-038 (Email Templates) ──> PROFILE-039 (Send Emails)
                      │
                      ├─> PROFILE-043 (Deactivate Account) ──> PROFILE-047 (Reactivate Account)
                      │
                      └─> PROFILE-044 (Delete Request) ──> PROFILE-045 (Grace Period) ──> PROFILE-048 (Permanent Deletion)

PROFILE-046 (Data Export) ──> PROFILE-002, TASK-002, PROFILE-020

AUTH-037 ──> PROFILE-040 (Rate Limiting)
AUTH-039 ──> PROFILE-041 (Audit Logging)

Testing Phase (PROFILE-050 to PROFILE-059) depends on implementation tasks
Documentation Phase (PROFILE-060 to PROFILE-066) depends on all tasks
```

## Parallelization Opportunities

### Phase 1 Parallel Tasks:
- PROFILE-002 (Models) + PROFILE-003 (Schemas) can be done in parallel after PROFILE-001

### Phase 2 Parallel Tasks:
- PROFILE-011 (Picture Models) + PROFILE-012 (Picture Schemas) can be done in parallel after PROFILE-010

### Phase 3 Parallel Tasks:
- PROFILE-020 (Preferences Models) + PROFILE-021 (Preferences Schemas) can be done in parallel after PROFILE-019

### Phase 7 Parallel Tasks:
- PROFILE-050, PROFILE-051, PROFILE-052 (Unit tests) can be written in parallel
- PROFILE-053, PROFILE-054, PROFILE-055 (Integration tests) can be written in parallel

### Phase 8 Parallel Tasks:
- PROFILE-060, PROFILE-061, PROFILE-062 (Documentation) can be written in parallel

## Acceptance Criteria

Each task must meet the following criteria before being marked complete:

1. **Code Quality**
   - Follows FastAPI best practices
   - Includes proper type hints
   - Has comprehensive docstrings
   - Passes linting (flake8, black, mypy)

2. **Testing**
   - Unit tests with >80% coverage
   - Integration tests for critical paths
   - All tests passing

3. **Security**
   - Input validation and XSS prevention
   - File upload security (type, size, content validation)
   - Privacy enforcement server-side
   - Password confirmation for sensitive operations
   - Proper error handling

4. **Performance**
   - Profile load time < 1.5 seconds for 95th percentile
   - Avatar processing < 5 seconds
   - Proper image optimization
   - Efficient database queries

5. **Documentation**
   - API endpoints documented in OpenAPI/Swagger
   - Code comments for complex logic
   - User guides for privacy settings

## Notes

- All database migrations must include both upgrade and downgrade procedures
- All endpoints must include proper error handling and return appropriate HTTP status codes
- All operations must enforce user isolation (users can only access their own profile)
- Avatar files limited to 5MB maximum size
- Supported image formats: JPEG, PNG, WEBP
- Multiple avatar sizes generated: original, optimized (800x800), thumbnail (200x200)
- Previous avatars deleted immediately on new upload to save storage
- Email changes require password confirmation and verification
- Rate limiting: 3 email change requests per 24 hours
- Account deletion has 30-day grace period before permanent deletion
- Privacy settings enforced server-side, cannot be bypassed client-side
- All sensitive operations require password confirmation
- Profile data retained while account is active
- Deleted account data removed after 30-day grace period
