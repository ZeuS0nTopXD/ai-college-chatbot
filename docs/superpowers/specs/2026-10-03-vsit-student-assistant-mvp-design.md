# VSIT Student Assistant MVP Design

## Purpose

Build a polished, deployable college-project MVP for Vidyalankar School of Information Technology (VSIT), Mumbai. The application must be easy to run on a laptop, credible in a project demonstration, and structured well enough for a small cloud deployment without adding production-scale complexity.

## Scope

The MVP includes:

- Existing timetable, faculty, office, result, and knowledge-base question answering.
- An academic and examination information module.
- Local document ingestion and retrieval with source citations.
- A password-protected administration panel.
- A redesigned responsive student interface.
- Browser-based voice input and answer playback.
- Automated backend tests, health checks, Docker packaging, and deployment documentation.

Student accounts, role hierarchies, WhatsApp integration, campus navigation, cloud speech services, and a hosted vector database are outside this release.

## Architecture

FastAPI remains the application backend. The existing oversized chat route will be reduced by moving academic, retrieval, authentication, and response behavior into focused services and routers with explicit interfaces.

SQLAlchemy remains the persistence layer. SQLite is the default database so a new user can start the application without installing a database server. The existing `DATABASE_URL` setting continues to support MySQL or PostgreSQL-compatible deployments.

The static frontend remains dependency-light and is served by FastAPI for a single deployable application. It will provide student chat, academic browsing, resources, and a separate admin workspace.

## Functional Design

### Student Assistant

The chat router classifies a question and dispatches it to timetable, faculty, office, result, academic, document retrieval, knowledge-base, or optional Ollama handling. Deterministic college data has priority over generated answers. When verified information is missing, the response says so clearly and directs the student to an official source or concerned office.

Existing timetable, faculty, office, result, and knowledge behavior remains available. Integration work may fix defects that prevent these flows from operating through their current public endpoints.

### Academic and Examination Module

Academic events contain:

- Title and description.
- Event type such as examination, deadline, holiday, notice, or academic activity.
- Optional course and semester filters.
- Start and end date/time.
- Optional location and external resource link.
- Published state.

Students can browse published upcoming events and ask natural-language questions about examinations, deadlines, calendars, and notices. Unpublished events are only visible in the admin workspace.

### Document Knowledge and Retrieval

An administrator can upload PDF and plain-text documents with a title and category. The server validates the file extension and size, stores the original file in an application data directory, extracts text, and splits it into page-aware passages.

Retrieval uses a lightweight local index suitable for a student project. It ranks passages by normalized term relevance and only uses results above a defined confidence threshold. Answers include document title and page number when available. The system does not invent an answer when no reliable passage exists.

Document processing status and errors are visible to the administrator. Deleting a document also removes its stored passages and file.

### Administration

The administration area uses one password configured through the environment. A successful login returns a short-lived signed bearer token. Every administrative mutation requires that token; public read endpoints expose only published or active information.

The admin workspace supports create, read, update, and delete operations for:

- Academic events.
- Knowledge-base entries.
- Faculty entries.
- Office entries.
- Uploaded documents.

Secrets and password values are never returned by the API or committed to the repository.

### Frontend and Voice

The frontend uses a VSIT-inspired responsive layout with navigation for Assistant, Academics, Resources, and Admin. The assistant view includes conversation history for the current browser session, quick prompts, source citations, loading feedback, and useful connection errors.

Voice input uses the browser Speech Recognition API where available. Answer playback uses the browser Speech Synthesis API. Unsupported browsers keep all text features and show voice controls as unavailable.

The interface meets basic accessibility expectations: keyboard operation, labelled controls, visible focus states, sufficient contrast, status announcements, and mobile layouts.

## Data Flow

1. The student submits a typed or transcribed question.
2. The API validates and classifies the request.
3. A deterministic domain service is queried first.
4. If the question refers to college documents, the retrieval service ranks stored passages and returns cited context.
5. Optional Ollama generation may phrase a response from supplied context, but the application must still return a useful extractive answer when Ollama is unavailable.
6. The frontend renders the response, metadata, and citations and may read the answer aloud.

Administrative writes follow login, token verification, validation, database update, and a structured success or error response.

## Error Handling and Data Integrity

- Requests with empty messages or invalid fields receive clear validation errors.
- Unsupported, empty, corrupt, or oversized documents are rejected without partial database records.
- Missing optional Ollama service does not break deterministic college features.
- Database failures produce safe API errors without exposing credentials or stack traces.
- Admin routes reject missing, expired, or invalid tokens.
- Destructive admin actions target explicit record identifiers and return not-found responses for absent records.
- Official facts are not fabricated. Seeded examples that are not verified VSIT facts are labelled as sample data.

## Configuration and Deployment

Configuration is provided through environment variables documented in `.env.example`. Required or supported settings include the database URL, admin password, token signing secret, upload limit, document storage path, allowed origins, and optional Ollama endpoint/model.

The repository includes a Dockerfile and compose configuration for a single-container deployment with persistent application data. The README documents direct local setup and a generic cloud deployment process suitable for Render, Railway, or a small VPS. A health endpoint reports application readiness without exposing secrets.

## Testing and Acceptance Criteria

Automated tests use an isolated temporary SQLite database and cover:

- Classification and routing of representative student questions.
- Academic event creation, publication rules, filtering, and chat answers.
- Admin login plus rejection of invalid or missing credentials.
- CRUD operations for all admin-managed data types.
- PDF/text upload validation, extraction, retrieval, citation, and deletion.
- Critical timetable, faculty, office, result, and knowledge flows.
- Graceful operation when Ollama is unavailable.

Completion requires the full test suite to pass, the application to import and start successfully, the frontend assets to load through FastAPI, and a documented local or Docker smoke-test path.

## Delivery Order

Work proceeds in vertical slices so each stage leaves the project usable:

1. Portable configuration, SQLite support, application factory, and test foundation.
2. Academic/exam data, APIs, chat integration, and tests.
3. Admin authentication and management APIs.
4. Document ingestion, retrieval, citations, and tests.
5. Responsive frontend, admin workspace, and voice controls.
6. Regression fixes, complete verification, Docker packaging, and deployment documentation.
