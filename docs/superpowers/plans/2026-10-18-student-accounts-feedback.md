# Student Accounts and Feedback Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add secure student registration/login, student feedback submission, and an admin feedback review tab while preserving guest chat and existing administrator management.

**Architecture:** Add two SQLAlchemy models, role-aware JWT helpers, student auth routes, feedback routes, and admin feedback endpoints. Extend the existing static student and admin pages with forms and token-backed fetch helpers; keep the existing admin password token contract unchanged.

**Tech Stack:** FastAPI, SQLAlchemy 2, Pydantic 2, PyJWT, Python `hashlib.scrypt`, static HTML/CSS/JavaScript, pytest.

**Spec:** `docs/superpowers/specs/2026-10-18-student-accounts-feedback-design.md`

## Global Constraints

- Guest chat remains usable without a student account.
- Administrator login remains `POST /api/auth/login` with `{password}` and an admin bearer token.
- Student passwords are never stored or returned in plaintext.
- Feedback content is rendered with safe DOM APIs and never interpolated as HTML.
- New validation limits are exactly those in the approved spec.

## Review Focus

- A student token must not authorize administrator endpoints; cover with a role-separation test in `tests/test_student_auth.py`.
- An admin token must not create feedback; cover with a role-separation test in `tests/test_feedback.py`.
- Duplicate email registration must be a conflict after lowercase normalization; cover in `tests/test_student_auth.py`.
- Feedback list ordering and status transitions must be deterministic; cover in `tests/test_feedback.py`.
- Existing frontend/admin contracts must remain present; extend `tests/test_frontend.py` with endpoint/form assertions.

### Task 1: Student identity and token primitives

**Files:**
- Create: `backend/models/student.py`
- Create: `backend/schemas/student.py`
- Modify: `backend/security.py`
- Modify: `backend/app.py`
- Test: `tests/test_student_auth.py`

**Interfaces:**
- Produces `StudentUser` with `id`, `name`, `email`, `password_hash`, and `created_at`.
- Produces role-aware `create_student_access_token(settings, student_id)` and `require_student(request, credentials)`.
- Produces password helpers using `hashlib.scrypt` and constant-time verification.

- [ ] **Step 1: Write failing tests** for password hashing/verification, registration response shape, duplicate email, student login, student-me, and admin/student token separation.
- [ ] **Step 2: Run `pytest tests/test_student_auth.py -q`** and confirm failures are caused by missing student primitives/routes.
- [ ] **Step 3: Implement the model, schemas, password helpers, student token claim, and dependency; import the model before `Base.metadata.create_all`.
- [ ] **Step 4: Run the focused tests and confirm they pass.
- [ ] **Step 5: Commit** with `feat: add student identity and auth primitives`.

### Task 2: Student authentication routes

**Files:**
- Modify: `backend/routes/auth.py`
- Modify: `backend/schemas/auth.py`
- Test: `tests/test_student_auth.py`

**Interfaces:**
- `POST /api/auth/register`, `POST /api/auth/student-login`, and `GET /api/auth/student-me`.
- Registration/login return `TokenResponse` plus a public `user` object and never expose `password_hash`.

- [ ] **Step 1: Add route-level failing tests** for valid registration, invalid email/password, duplicate normalized email, wrong password, and student-me.
- [ ] **Step 2: Run the focused tests and confirm the expected route failures.
- [ ] **Step 3: Implement normalized email lookup, conflict handling, scrypt hashing, token creation, and public-user serialization.
- [ ] **Step 4: Run `pytest tests/test_student_auth.py -q` and confirm all student auth tests pass alongside existing `tests/test_auth.py`.
- [ ] **Step 5: Commit** with `feat: add student registration and login routes`.

### Task 3: Feedback persistence and API

**Files:**
- Create: `backend/models/feedback.py`
- Create: `backend/schemas/feedback.py`
- Create: `backend/routes/feedback.py`
- Modify: `backend/app.py`
- Modify: `backend/routes/admin.py`
- Test: `tests/test_feedback.py`

**Interfaces:**
- `POST /api/feedback` accepts `{rating, message, context?}` with a student bearer token.
- Admin routes provide `GET/PATCH/DELETE /api/admin/feedback[/{id}]` with `new|reviewed` statuses.
- Feedback reads include student name/email but never password data.

- [ ] **Step 1: Write failing tests** for authenticated creation, validation, unauthorized access, newest-first admin listing, status update, delete, and missing-record 404.
- [ ] **Step 2: Run `pytest tests/test_feedback.py -q` and confirm expected failures.
- [ ] **Step 3: Implement model, schemas, student route, admin CRUD, and route registration.
- [ ] **Step 4: Run feedback tests plus existing admin tests and confirm they pass.
- [ ] **Step 5: Commit** with `feat: add student feedback API`.

### Task 4: Student frontend account and feedback flow

**Files:**
- Modify: `frontend/index.html`
- Modify: `frontend/script.js`
- Modify: `frontend/style.css`
- Test: `tests/test_frontend.py`

**Interfaces:**
- Student UI stores `vsit-student-token`, shows sign-in/register controls, supports logout, and posts feedback to `/api/feedback`.
- Existing `Administrator login` link remains available and points to `/admin`.

- [ ] **Step 1: Extend frontend tests** to assert auth controls, feedback form fields, student endpoint strings, and admin link.
- [ ] **Step 2: Run frontend tests and confirm they fail before markup/script changes.
- [ ] **Step 3: Add accessible auth modal/panel, feedback panel, token-backed fetch helper, validation messages, and safe success/error rendering.
- [ ] **Step 4: Run frontend tests and inspect the served student HTML for all controls.
- [ ] **Step 5: Commit** with `feat: add student account and feedback UI`.

### Task 5: Admin feedback review UI

**Files:**
- Modify: `frontend/admin.html`
- Modify: `frontend/admin.js`
- Modify: `frontend/style.css`
- Test: `tests/test_frontend.py`

**Interfaces:**
- Admin navigation adds a `feedback` view and list container.
- Admin JS loads `/api/admin/feedback`, marks records reviewed, and deletes records via `adminFetch`.

- [ ] **Step 1: Extend frontend tests** for the Feedback tab, list container, and documented admin endpoint strings.
- [ ] **Step 2: Run the focused frontend tests and confirm the new assertions fail.
- [ ] **Step 3: Add feedback panel, safe DOM rendering, status action, delete action, and empty/loading/error states while preserving all current tabs.
- [ ] **Step 4: Run all frontend tests and inspect admin HTML for the new tab.
- [ ] **Step 5: Commit** with `feat: add admin feedback review panel`.

### Task 6: Full verification and deployment

**Files:**
- Modify only if verification exposes a regression.

- [ ] **Step 1: Run the focused backend and frontend tests with a writable pytest basetemp.
- [ ] **Step 2: Run the full test suite and fix any regressions with a failing test first.
- [ ] **Step 3: Start the app locally and verify health, registration, student login, feedback submission, admin login, and feedback listing through HTTP.
- [ ] **Step 4: Commit any verification fixes and push `HEAD:main`.
- [ ] **Step 5: Verify the deployed health endpoint and both student/admin pages after Render redeploys.
