# Student Productivity and Admin Overview Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add optional student course/division context, local assistant productivity controls, and an authenticated admin overview dashboard.

**Architecture:** Reuse the existing FastAPI routes, SQLAlchemy models, static HTML/CSS/JavaScript frontend, and JWT admin dependency. Student context and transcript utilities are browser-local; the admin overview is a read-only aggregate endpoint over existing tables.

**Tech Stack:** Python 3.12, FastAPI, SQLAlchemy, pytest, HTML/CSS/vanilla JavaScript.

**Spec:** `docs/superpowers/specs/2026-10-27-student-productivity-admin-overview-design.md`

## Global Constraints

- Existing `/chat` request and response contracts remain backward compatible.
- Student context fields are optional and guest use remains supported.
- No new dependencies or paid services.
- Admin overview data must use the existing `require_admin` dependency.

## Review Focus

- Empty course/division values must not be sent as misleading filters; covered by chat payload tests.
- Local storage containing malformed JSON must not break the student page; covered by frontend behavior tests and guarded parsing.
- Transcript export must use visible text safely; covered by a utility-level test.
- Admin overview must reject missing/invalid tokens; covered by API tests.
- Empty feedback/content tables must return zero counts and an empty recent list; covered by API tests.

---

### Task 1: Add the admin overview API

**Files:**
- Modify: `backend/routes/admin.py`
- Test: `tests/test_admin.py`

**Interfaces:**
- Produces `GET /api/admin/overview` returning `{counts: {...}, feedback: {total, pending, reviewed, recent: [...]}}`.

- [ ] **Step 1: Write the failing tests** for authenticated overview counts, recent feedback, and unauthenticated rejection.
- [ ] **Step 2: Run `python -m pytest tests/test_admin.py -q` and confirm the new tests fail.**
- [ ] **Step 3: Implement the aggregate query in `backend/routes/admin.py`** using the existing models and `require_admin` router dependency.
- [ ] **Step 4: Run the focused admin tests and confirm they pass.**
- [ ] **Step 5: Run the full test suite.**

### Task 2: Add student context and productivity controls

**Files:**
- Modify: `frontend/index.html`
- Modify: `frontend/script.js`
- Modify: `frontend/style.css`
- Test: `tests/test_frontend.py`
- Test: `tests/test_frontend_accounts.py`

**Interfaces:**
- Student page adds `#student-context-form`, `#quick-prompts`, `#recent-questions`, `#clear-chat`, and `#download-transcript`.
- Chat requests include optional `course` and `division` values.

- [ ] **Step 1: Write failing HTML contract tests** for context controls, quick prompts, recent questions, clear, and transcript controls.
- [ ] **Step 2: Run the focused frontend tests and confirm they fail.**
- [ ] **Step 3: Add the controls to `frontend/index.html`** using existing button/input styles and accessible labels.
- [ ] **Step 4: Update `frontend/script.js`** to persist context, include non-empty values in `POST /chat`, record reusable recent prompts, clear only the transcript, and download visible messages as text.
- [ ] **Step 5: Add responsive styles in `frontend/style.css`** without changing the current theme.
- [ ] **Step 6: Run the frontend tests and full suite.**

### Task 3: Add the admin dashboard panel

**Files:**
- Modify: `frontend/admin.html`
- Modify: `frontend/admin.js`
- Modify: `frontend/style.css`
- Test: `tests/test_frontend_accounts.py`

**Interfaces:**
- Admin page adds a `dashboard` tab that calls `GET /api/admin/overview` and renders count cards plus recent feedback.

- [ ] **Step 1: Write the failing frontend contract test** for the dashboard tab and overview fetch hook.
- [ ] **Step 2: Run the focused test and confirm it fails.**
- [ ] **Step 3: Add dashboard markup and navigation** to `frontend/admin.html`.
- [ ] **Step 4: Implement `loadOverview()` and safe rendering** in `frontend/admin.js`.
- [ ] **Step 5: Add compact dashboard card styles** and verify mobile layout.
- [ ] **Step 6: Run the complete test suite and compile check.**

### Task 4: Final verification

- [ ] Run `python -m pytest -q`.
- [ ] Run `python -m compileall backend`.
- [ ] Inspect the final diff for accidental changes and confirm no secrets or generated data are included.
