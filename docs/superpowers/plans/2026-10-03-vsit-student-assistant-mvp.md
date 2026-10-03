# VSIT Student Assistant MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver a polished, locally runnable and cloud-ready VSIT student assistant with academics, cited document search, protected administration, voice controls, tests, and deployment packaging.

**Architecture:** Keep FastAPI and SQLAlchemy, introduce an application factory and focused domain routers/services, and use SQLite by default through the existing configurable database URL. Serve the dependency-light frontend from FastAPI and use local page-aware document passages with deterministic relevance scoring so core features do not depend on Ollama.

**Tech Stack:** Python 3.10+, FastAPI, SQLAlchemy 2, Pydantic 2, PyJWT, pypdf, pytest, FastAPI TestClient, HTML5, CSS, vanilla JavaScript, Web Speech APIs, Docker.

**Spec:** `docs/superpowers/specs/2026-10-03-vsit-student-assistant-mvp-design.md`

## Global Constraints

- Default to SQLite while continuing to accept `DATABASE_URL` for MySQL or PostgreSQL-compatible deployments.
- Preserve public timetable, faculty, office, result, knowledge, and `POST /chat` behavior.
- Deterministic college data and cited passages take priority over generated answers.
- Ollama remains optional; its absence must not break college-information features.
- Use one environment-configured admin password and short-lived signed bearer tokens; never expose or commit secrets.
- Accept only PDF and plain-text uploads within the configured size limit; remove files and passages together.
- Clearly label unverified seeded facts as sample data and never fabricate official VSIT information.
- Keep the frontend dependency-light, responsive, keyboard-operable, and usable when Web Speech APIs are absent.

## Review Focus

- Empty, whitespace-only, or extremely long chat input returns a bounded validation response; covered in Task 2 chat tests.
- Academic events crossing date boundaries or missing optional filters remain queryable; covered in Task 2 service tests.
- Expired, malformed, and incorrectly signed admin tokens all receive HTTP 401; covered in Task 3 authentication tests.
- Corrupt PDF, empty text, unsupported extension, and over-limit uploads leave no database or file residue; covered in Task 5 upload tests.
- Document searches containing punctuation, mixed case, or no overlapping terms return stable cited results or an explicit no-match response; covered in Task 5 retrieval tests.

---

### Task 1: Portable Application and Test Foundation

**Files:**
- Create: `backend/config.py`
- Create: `backend/app.py`
- Create: `backend/dependencies.py`
- Create: `tests/conftest.py`
- Create: `tests/test_app.py`
- Modify: `backend/database/database.py`
- Modify: `backend/main.py`
- Modify: `requirements.txt`
- Modify: `.env.example`

**Interfaces:**
- Produces: `Settings.from_env() -> Settings`, `create_app(settings: Settings | None = None) -> FastAPI`, and `get_db() -> Generator[Session, None, None]`.
- Produces: `GET /health` returning `{"status": "ok"}` and frontend assets served from `/` and `/static`.

- [ ] **Step 1: Write failing application-foundation tests**

Add `test_health_endpoint_reports_ready`, `test_root_serves_frontend`, and `test_test_database_is_isolated`. Assert HTTP 200, the exact health payload, HTML content at `/`, and that the fixture database uses a temporary SQLite file.

- [ ] **Step 2: Verify the foundation tests fail for missing factory and health route**

Run: `py -m pytest tests/test_app.py -v`
Expected: FAIL because `backend.app.create_app` does not exist.

- [ ] **Step 3: Implement configuration, database initialization, application factory, shared database dependency, and static serving**

`Settings` owns `database_url`, `admin_password`, `token_secret`, `token_ttl_minutes`, `max_upload_bytes`, `document_storage_path`, `cors_origins`, `ollama_url`, and `ollama_model`. Configure SQLite with `check_same_thread=False`; keep other SQLAlchemy URLs unchanged. `backend/main.py` only exposes `app = create_app()`.

- [ ] **Step 4: Add runtime and test dependencies**

Add compatible pins for `pytest`, `httpx`, `PyJWT`, `pypdf`, and `python-multipart`, and document every setting in `.env.example` with safe development defaults.

- [ ] **Step 5: Run foundation tests and the existing import smoke check**

Run: `py -m pytest tests/test_app.py -v`
Expected: PASS.

Run: `py -c "from backend.main import app; print(app.title)"`
Expected: prints `VSIT Student Assistant API` and exits 0.

- [ ] **Step 6: Commit the foundation**

Run: `git add backend requirements.txt .env.example tests && git commit -m "refactor: add portable app foundation"`

### Task 2: Academic and Examination Module

**Files:**
- Create: `backend/models/academic.py`
- Create: `backend/schemas/academic.py`
- Create: `backend/services/academic_service.py`
- Create: `backend/routes/academic.py`
- Create: `tests/test_academic.py`
- Modify: `backend/app.py`
- Modify: `backend/routes/chat.py`

**Interfaces:**
- Consumes: `get_db()` and `create_app()` from Task 1.
- Produces: `AcademicEvent` fields `id`, `title`, `description`, `event_type`, `course`, `semester`, `starts_at`, `ends_at`, `location`, `resource_url`, `is_published`, `created_at`.
- Produces: `list_published_events(db, event_type=None, course=None, semester=None, from_date=None) -> list[AcademicEvent]` and `answer_academic_question(db, message: str) -> dict | None`.
- Produces: `GET /api/academics` with event type, course, semester, and date filters.

- [ ] **Step 1: Write failing academic model, API, and query tests**

Add tests named `test_public_academics_hide_drafts`, `test_public_academics_filter_course_and_semester`, `test_academic_question_returns_nearest_matching_event`, `test_academic_event_may_omit_course_and_semester`, and `test_empty_or_oversized_chat_message_is_bounded`. Assert unpublished rows are absent, optional filters are case-insensitive, the nearest future matching exam is returned with its date, institution-wide events remain visible, empty input receives the existing prompt, and input over 4,000 characters receives HTTP 422.

- [ ] **Step 2: Verify academic tests fail because the module is absent**

Run: `py -m pytest tests/test_academic.py -v`
Expected: FAIL importing `AcademicEvent`.

- [ ] **Step 3: Implement the academic model, schemas, service, public router, and chat handler**

Use timezone-naive ISO datetimes consistently. Route academic questions to `answer_academic_question` before optional AI fallback and include `event_id` and `resource_url` in chat metadata when present.

- [ ] **Step 4: Run academic and regression tests**

Run: `py -m pytest tests/test_academic.py tests/test_app.py -v`
Expected: PASS.

- [ ] **Step 5: Commit the academic slice**

Run: `git add backend tests && git commit -m "feat: add academic and exam information"`

### Task 3: Admin Authentication

**Files:**
- Create: `backend/security.py`
- Create: `backend/schemas/auth.py`
- Create: `backend/routes/auth.py`
- Create: `tests/test_auth.py`
- Modify: `backend/app.py`

**Interfaces:**
- Consumes: admin password, signing secret, and TTL from `Settings`.
- Produces: `create_access_token(settings: Settings, now: datetime | None = None) -> str`, `require_admin(credentials=Depends(HTTPBearer)) -> None`, and `POST /api/auth/login`.

- [ ] **Step 1: Write failing authentication tests**

Add `test_valid_password_returns_bearer_token`, `test_wrong_password_is_rejected`, `test_missing_token_is_rejected`, `test_expired_token_is_rejected`, `test_malformed_token_is_rejected`, and `test_wrong_signature_is_rejected`. Assert success returns `token_type == "bearer"`; every rejection returns HTTP 401 without echoing credentials.

- [ ] **Step 2: Verify authentication tests fail because the route is absent**

Run: `py -m pytest tests/test_auth.py -v`
Expected: FAIL with HTTP 404 or missing import.

- [ ] **Step 3: Implement constant-time password comparison and HS256 JWT verification**

Tokens contain only `sub="admin"`, `iat`, and `exp`. Refuse to start with an empty production signing secret; the documented development secret remains clearly marked for local use.

- [ ] **Step 4: Run authentication tests**

Run: `py -m pytest tests/test_auth.py -v`
Expected: PASS.

- [ ] **Step 5: Commit authentication**

Run: `git add backend tests && git commit -m "feat: protect administration with token auth"`

### Task 4: Admin Management APIs

**Files:**
- Create: `backend/schemas/admin.py`
- Create: `backend/routes/admin.py`
- Create: `tests/test_admin.py`
- Modify: `backend/schemas/academic.py`
- Modify: `backend/schemas/knowledge.py`
- Modify: `backend/app.py`

**Interfaces:**
- Consumes: `require_admin`, SQLAlchemy models, and shared `get_db()`.
- Produces: `/api/admin/academics`, `/api/admin/knowledge`, `/api/admin/faculty`, and `/api/admin/offices` list/create/update/delete routes.
- Produces: normalized Pydantic create/update/read schemas that never return secret fields.

- [ ] **Step 1: Write failing protected CRUD tests**

For each resource, add a parametrized test proving unauthenticated writes return 401 and authenticated create/read/update/delete completes with HTTP 201/200/200/204. Add `test_deleting_unknown_admin_record_returns_404` and schema validation tests for blank required names.

- [ ] **Step 2: Verify admin API tests fail because routes are absent**

Run: `py -m pytest tests/test_admin.py -v`
Expected: FAIL with HTTP 404.

- [ ] **Step 3: Implement protected CRUD routers and schemas**

Use explicit model-to-schema mapping, partial update schemas, deterministic list ordering by primary key, and transaction rollback on commit errors.

- [ ] **Step 4: Run admin, auth, and academic tests**

Run: `py -m pytest tests/test_admin.py tests/test_auth.py tests/test_academic.py -v`
Expected: PASS.

- [ ] **Step 5: Commit admin management**

Run: `git add backend tests && git commit -m "feat: add admin management APIs"`

### Task 5: Document Ingestion and Cited Retrieval

**Files:**
- Create: `backend/models/document.py`
- Create: `backend/schemas/document.py`
- Create: `backend/services/document_service.py`
- Create: `backend/routes/documents.py`
- Create: `tests/fixtures/vsit_notice.txt`
- Create: `tests/test_documents.py`
- Modify: `backend/app.py`
- Modify: `backend/routes/chat.py`
- Modify: `.gitignore`

**Interfaces:**
- Consumes: `require_admin`, `Settings.document_storage_path`, `Settings.max_upload_bytes`, and shared database dependency.
- Produces: `Document` and cascade-owned `DocumentChunk` models.
- Produces: `extract_document(filename: str, content: bytes) -> list[ExtractedPage]`, `chunk_pages(pages: list[ExtractedPage], max_chars: int = 1200, overlap_chars: int = 150) -> list[ChunkInput]`, and `search_documents(db, query: str, limit: int = 4, min_score: float = 0.12) -> list[SearchHit]`.
- Produces: protected `POST/GET/DELETE /api/admin/documents`, public `GET /api/documents`, and `POST /api/documents/search`.

- [ ] **Step 1: Write failing extraction and retrieval tests**

Add `test_text_upload_creates_page_aware_chunks`, `test_search_returns_title_page_and_relevant_excerpt`, `test_search_normalizes_case_and_punctuation`, `test_search_without_overlap_returns_no_hits`, and `test_deleting_document_removes_chunks_and_file`.

- [ ] **Step 2: Write failing validation and cleanup tests**

Add `test_rejects_unsupported_extension_without_residue`, `test_rejects_oversized_upload_without_residue`, `test_rejects_empty_text_without_residue`, and `test_rejects_corrupt_pdf_without_residue`. Assert HTTP 400 or 413 as appropriate and zero document rows/files after each failure.

- [ ] **Step 3: Verify document tests fail because the module is absent**

Run: `py -m pytest tests/test_documents.py -v`
Expected: FAIL importing `backend.services.document_service`.

- [ ] **Step 4: Implement validated storage, extraction, chunking, scoring, APIs, and chat retrieval**

Normalize Unicode word tokens, remove a small fixed stop-word set, rank by weighted query-term coverage plus term frequency, and break ties by document ID/page/chunk index. Chat responses quote only short relevant excerpts and return a `sources` array with document ID, title, page, and score.

- [ ] **Step 5: Run document and chat-related tests**

Run: `py -m pytest tests/test_documents.py tests/test_academic.py tests/test_app.py -v`
Expected: PASS.

- [ ] **Step 6: Commit document retrieval**

Run: `git add backend tests .gitignore && git commit -m "feat: add cited college document search"`

### Task 6: Existing Feature Regression Coverage and Fixes

**Files:**
- Create: `tests/test_existing_features.py`
- Modify: `backend/routes/timetable.py`
- Modify: `backend/routes/chat.py`
- Modify as failures require: `backend/services/timetable_service.py`, `backend/services/faculty_service.py`, `backend/services/office_service.py`, `backend/services/result_service.py`

**Interfaces:**
- Consumes: existing public endpoints and chat response contract.
- Produces: stable public behavior for timetable, faculty, office, result, and knowledge requests under SQLite.

- [ ] **Step 1: Write regression tests for each existing flow**

Add `test_timetable_endpoint_uses_current_model_fields`, `test_chat_answers_teacher_from_timetable`, `test_chat_answers_office_location`, `test_chat_returns_result_link`, `test_chat_returns_matching_knowledge`, and `test_chat_works_when_ollama_is_unavailable`.

- [ ] **Step 2: Run regressions and record the expected failures**

Run: `py -m pytest tests/test_existing_features.py -v`
Expected: at least the timetable endpoint test fails if it still reads obsolete model attributes; each failure must identify a real behavior mismatch before code changes.

- [ ] **Step 3: Apply minimal fixes for the demonstrated failures**

Keep the existing response fields, use current model attributes, and replace broad exception swallowing only where a test exposes a user-visible failure.

- [ ] **Step 4: Run the complete backend suite**

Run: `py -m pytest -v`
Expected: PASS with zero failures.

- [ ] **Step 5: Commit regression fixes**

Run: `git add backend tests && git commit -m "fix: stabilize existing student assistant flows"`

### Task 7: Responsive Frontend, Admin Workspace, and Voice

**Files:**
- Modify: `frontend/index.html`
- Modify: `frontend/style.css`
- Modify: `frontend/script.js`
- Create: `frontend/admin.html`
- Create: `frontend/admin.js`
- Create: `tests/test_frontend.py`

**Interfaces:**
- Consumes: `/chat`, `/api/academics`, `/api/documents`, `/api/auth/login`, and protected admin APIs.
- Produces: accessible Assistant, Academics, Resources, and Admin views; `sendMessage(message)`, `loadAcademicEvents(filters)`, `startVoiceInput()`, `speakAnswer(text)`, and admin CRUD/upload actions.

- [ ] **Step 1: Write failing frontend contract tests**

Add tests asserting the student page contains named navigation, labelled chat controls, an `aria-live` status region, voice controls, no hard-coded absolute API origin, and links to academics/resources. Assert the admin page includes login, event editor, data-management sections, and document upload controls.

- [ ] **Step 2: Verify frontend contract tests fail against the current page**

Run: `py -m pytest tests/test_frontend.py -v`
Expected: FAIL for missing navigation, accessibility, voice, and admin elements.

- [ ] **Step 3: Implement the responsive student shell and API integration**

Use relative API URLs, semantic landmarks, safe DOM text insertion, session-local conversation rendering, filters, source cards, loading states, and responsive CSS with visible keyboard focus.

- [ ] **Step 4: Implement progressive voice controls**

Hide or disable recognition controls when neither `SpeechRecognition` nor `webkitSpeechRecognition` exists. Use `speechSynthesis` only after an explicit user action and expose a stop control.

- [ ] **Step 5: Implement the protected admin workspace**

Store the bearer token in `sessionStorage`, clear it on 401/logout, and support list/create/edit/delete for academics, knowledge, faculty, and offices plus document upload/delete.

- [ ] **Step 6: Run frontend contracts and full tests**

Run: `py -m pytest tests/test_frontend.py -v`
Expected: PASS.

Run: `py -m pytest -v`
Expected: PASS.

- [ ] **Step 7: Commit the frontend**

Run: `git add frontend tests && git commit -m "feat: redesign student and admin experience"`

### Task 8: Packaging, Documentation, and Final Verification

**Files:**
- Create: `Dockerfile`
- Create: `docker-compose.yml`
- Create: `.dockerignore`
- Modify: `README.md`
- Modify: `.env.example`
- Modify: `backend/app.py`
- Modify: `tests/test_app.py`

**Interfaces:**
- Consumes: completed application and configuration.
- Produces: container listening on `$PORT` with persistent `/app/data`, documented direct/Docker setup, seed guidance, feature examples, and health-check instructions.

- [ ] **Step 1: Extend the smoke test for packaged runtime assumptions**

Assert `/health`, `/`, `/admin`, and one static asset return 200 from a clean temporary database and storage directory.

- [ ] **Step 2: Verify the new smoke expectation fails before packaging routes are complete**

Run: `py -m pytest tests/test_app.py -v`
Expected: FAIL for any missing admin/static route.

- [ ] **Step 3: Add container files and rewrite setup/deployment documentation**

Use a non-root runtime user, create the data directory with correct ownership, start with `uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}`, persist the SQLite database and documents, and document direct Windows setup plus Docker and generic Render/Railway/VPS deployment.

- [ ] **Step 4: Run fresh full verification**

Run: `py -m pytest -v`
Expected: PASS with zero failures.

Run: `py -m compileall backend`
Expected: exit 0.

Run: `docker compose config`
Expected: exit 0 when Docker is available; otherwise report Docker verification as unavailable rather than passing.

Run: `git diff --check`
Expected: no output and exit 0.

- [ ] **Step 5: Review the implementation against every specification section**

Confirm academics, cited retrieval, protected CRUD, responsive/voice behavior, error handling, configuration, deployment, and regression coverage are each represented by code and a passing test. Record any environment-only limitation in the README and final report.

- [ ] **Step 6: Commit packaging and documentation**

Run: `git add Dockerfile docker-compose.yml .dockerignore README.md .env.example backend tests && git commit -m "docs: package and document VSIT assistant MVP"`
