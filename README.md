# VSIT Student Assistant

A deployable student-support MVP for Vidyalankar School of Information Technology (VSIT), Mumbai. It combines deterministic college information, academic events, searchable college documents, a protected admin workspace, and optional local AI assistance.

## Included features

- Timetable questions by course, division, day, subject, teacher, room, and session type.
- Faculty and office queries, including HOD, subjects, locations, timings, and contacts.
- Academic and examination events with course, semester, publication, date, and link filters.
- Result links and structured VSIT knowledge entries.
- PDF/TXT uploads with local page-aware search and source citations.
- Password-protected admin CRUD for academics, knowledge, faculty, offices, and documents.
- Responsive student dashboard and administration workspace.
- Browser speech-to-text and answer playback when the browser supports Web Speech APIs.
- SQLite by default, with configurable SQLAlchemy database URLs.
- Optional Ollama responses for general, academic, and career questions when deterministic information is unavailable.
- Automated tests, health check, Docker packaging, and persistent document storage.

## Quick start on Windows

Requirements: Python 3.10 or newer. Ollama is optional.

```powershell
py -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn backend.main:app --reload --port 8000
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000). The administration workspace is at [http://127.0.0.1:8000/admin](http://127.0.0.1:8000/admin), and API documentation is at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

The default `.env.example` values are intended only for local development. Set strong `ADMIN_PASSWORD` and `TOKEN_SECRET` values before sharing or deploying the app.

## Configuration

| Variable | Purpose | Local default |
| --- | --- | --- |
| `APP_ENV` | Runtime environment; production/staging enforce deployment secrets | `development` |
| `DATABASE_URL` | SQLAlchemy database URL | `sqlite:///./data/vsit_student_assistant.db` |
| `ADMIN_PASSWORD` | Password for the admin workspace | `change-me` |
| `TOKEN_SECRET` | Secret used to sign admin access tokens | Development-only value |
| `TOKEN_TTL_MINUTES` | Admin session duration | `60` |
| `MAX_UPLOAD_BYTES` | Maximum PDF/TXT upload size | `10485760` (10 MiB) |
| `DOCUMENT_STORAGE_PATH` | Stored document directory | `./data/documents` |
| `CORS_ORIGINS` | Comma-separated allowed browser origins | Local port 8000 origins |
| `OLLAMA_URL` | Optional Ollama generation endpoint | `http://localhost:11434/api/generate` |
| `OLLAMA_MODEL` | Optional local model | `llama3.2:3b` |

MySQL remains supported, for example:

```env
DATABASE_URL=mysql+pymysql://user:password@127.0.0.1:3306/vsit_student_assistant
```

## Add college information

Start the application, visit `/admin`, and sign in with `ADMIN_PASSWORD`. The workspace can manage:

- Academic events and examination dates.
- Knowledge questions and verified answers.
- Faculty members and subject information.
- College offices and procedures.
- PDF or UTF-8 text notices for document search.

Only published academic events appear to students. Uploaded documents are split into page-aware passages and searched locally. When no passage meets the relevance threshold, the assistant returns no document match instead of inventing an answer.

Refresh the local database with records verified against the official VSIT website:

```powershell
python -m backend.scripts.seed_official_vsit
```

The refresh loads official VSIT contact, programme, Computing department, and faculty records. The public site does not publish a current timetable or individual student result records, so those tables are cleared and the assistant reports that verified data is unavailable for those questions.

## Optional Ollama setup

The core college features run without Ollama. For general and career questions, install Ollama separately and run:

```powershell
ollama pull llama3.2:3b
```

If Ollama is unavailable, the API returns a clear fallback response while timetable, academic, office, faculty, result, knowledge, and document features continue working.

## Run the tests

```powershell
python -m pytest -q
python -m compileall backend
```

The tests use isolated temporary SQLite databases and do not modify local application data.

## Docker

Set deployment secrets in the current shell or in a local `.env` file, then build and run:

```powershell
$env:ADMIN_PASSWORD = "replace-with-a-strong-password"
$env:TOKEN_SECRET = "replace-with-a-long-random-signing-secret"
docker compose up --build
```

Open [http://localhost:8000](http://localhost:8000). The named `vsit_data` volume preserves the SQLite database and uploaded documents across container restarts.

## Small cloud deployment

Render, Railway, and a small VPS can run the included Dockerfile. Configure these items in the platform dashboard:

1. Set `APP_ENV=production`, `ADMIN_PASSWORD` to a strong password of at least 12 characters, and a random `TOKEN_SECRET` of at least 32 characters. The app refuses the development defaults in production.
2. Set `DATABASE_URL=sqlite:////app/data/vsit_student_assistant.db` for a single persistent instance, or use the provider's managed database URL.
3. Set `DOCUMENT_STORAGE_PATH=/app/data/documents`.
4. Attach a persistent disk at `/app/data` when using SQLite and local document storage.
5. Set `CORS_ORIGINS` to the deployed HTTPS origin.
6. Configure the health check path as `/health`.

SQLite plus local files are appropriate for one project instance. Multiple replicas require a shared SQL database and shared object storage, which are outside this MVP.

### Render deployment

The repository includes `render.yaml` for a free Render Web Service deployment. In Render, choose **New > Blueprint**, connect this repository, and apply the blueprint. Set the two prompted values:

1. `ADMIN_PASSWORD`: a strong administrator password of at least 12 characters.
2. `CORS_ORIGINS`: the final HTTPS origin, such as `https://vsit-student-assistant.onrender.com`.

The free service stores SQLite data and uploaded documents on ephemeral container storage, so those files can be reset when Render redeploys or restarts the service. For durable records later, switch to managed PostgreSQL and object storage. After the first deploy, verify `/health`, sign in at `/admin`, and run the official VSIT data refresh before adding any approved notices or academic records.

## API overview

- `POST /chat` — answer a student question.
- `GET /api/academics` — list published academic events.
- `GET /api/documents` — list searchable college documents.
- `POST /api/documents/search` — retrieve cited document passages.
- `POST /api/auth/login` — create an administrator session.
- `/api/admin/*` — protected management routes.
- `GET /health` — deployment health check.

FastAPI exposes the complete interactive schema at `/docs`.
