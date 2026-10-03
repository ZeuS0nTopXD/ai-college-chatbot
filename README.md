# VSIT Student Assistant

AI-powered college information chatbot for Vidyalankar School of Information
Technology (VSIT). Answers questions about timetables, results, and general
college information (admissions, courses, facilities, placements, etc.), and
falls back to a local LLM (via [Ollama](https://ollama.com)) for open-ended
academic/career/general questions.

## Architecture

- **Backend**: FastAPI + SQLAlchemy + MySQL
- **AI**: Local LLM via Ollama (`llama3.2:3b` by default) — no external API
  key required, runs entirely on your machine
- **Frontend**: Static HTML/CSS/JS chat widget

```
backend/
  main.py              FastAPI app, CORS, router registration
  database/            SQLAlchemy engine/session setup
  models/               ORM models: Timetable, KnowledgeBase, Result
  schemas/              Pydantic request/response schemas
  routes/               /chat, /knowledge, /timetable, /result endpoints
  services/
    classifier.py        Classifies a question into a category + does
                          scored knowledge-base matching
    timetable_service.py Parses timetable questions (course/division/day/
                          subject/teacher/intent)
    result_service.py    Parses result questions (semester/batch/course)
    ai_service.py        Calls the local Ollama LLM, with graceful
                          fallback messages if it's unreachable
  data/                 Seed data (timetable, results, VSIT knowledge)
  scripts/               Seeder scripts to load data/ into MySQL
frontend/
  index.html, style.css, script.js   Chat UI
```

## Setup

1. **Install MySQL** and create a database, e.g. `vsit_student_assistant`.

2. **Install [Ollama](https://ollama.com)** and pull the model:
   ```
   ollama pull llama3.2:3b
   ```
   Ollama must be running (`ollama serve`, or it runs automatically after
   install) for ACADEMIC/CAREER/GENERAL questions and for VSIT/NGO answers
   not already in the knowledge base.

3. **Configure environment**: copy `.env.example` to `.env` and fill in your
   MySQL credentials:
   ```
   cp .env.example .env
   ```

4. **Create a virtual environment and install dependencies**:
   ```
   python -m venv venv
   venv\Scripts\activate        # Windows
   source venv/bin/activate     # macOS/Linux
   pip install -r requirements.txt
   ```

5. **Seed the database** (tables are created automatically on first run of
   `main.py`, then populate them):
   ```
   python -m backend.scripts.seed_timetable
   python -m backend.scripts.seed_knowledge
   python -m backend.seed_result
   ```

6. **Run the API**:
   ```
   uvicorn backend.main:app --reload --port 8000
   ```
   Visit `http://127.0.0.1:8000` — you should see
   `{"message": "VSIT Student Assistant API is running"}`.
   Interactive API docs: `http://127.0.0.1:8000/docs`.

7. **Run the frontend**: open `frontend/index.html` with a live server on
   port 5500 (e.g. the VS Code "Live Server" extension), or update
   `CORS_ORIGINS` in `.env` to match whatever origin you serve it from.

## API overview

- `POST /chat` — main chatbot endpoint. Body: `{"message": "..."}`
- `GET /timetable/{course}/{division}/{day}` — raw timetable lookup
- `GET /result/{course}` — all results for a course
- `GET /result/{course}/{semester}` — result for a specific semester
- `POST /knowledge` — add a knowledge-base entry (category/topic/question/answer)

## Current scope

Implemented: timetable Q&A (day/subject/teacher/room queries), result
lookup, VSIT/NGO knowledge-base Q&A, and general/academic/career Q&A via a
local LLM, with a web chat frontend.

Not yet implemented (see project vision doc): PDF/RAG ingestion of official
notices and circulars, multi-language support (Hindi/Marathi), voice
assistant, WhatsApp integration, campus navigation, and a placement/resume
assistant. These are larger efforts each requiring their own design
decisions (e.g. which translation/speech APIs, which vector store for RAG,
WhatsApp Business API setup) — see the project's next steps.
