# Independent Local Intelligence Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Make the VSIT assistant answer broad student questions locally without Ollama or hosted AI services, using verified data and natural-language retrieval.

**Architecture:** Add a local query understanding layer that normalizes input, expands aliases, extracts entities, scores verified records, and renders category-specific answers. Preserve existing structured faculty, office, timetable, academic, result, and document paths, adding confidence thresholds and short-lived session context around them.

**Tech Stack:** FastAPI, Pydantic, SQLAlchemy/PostgreSQL, Python standard-library text processing, pytest, browser smoke tests.

**Spec:** `docs/superpowers/specs/2026-10-04-independent-local-intelligence-design.md`

## Global Constraints

- Runtime must not require Ollama, an AI API key, or an external model.
- Answers must remain grounded in verified VSIT data.
- Unsupported or ambiguous questions must clarify or report unavailable data.
- Sample records must not be exposed as official answers.
- Existing API response fields and deployed frontend behavior must remain compatible.

## Review Focus

- Misspelled and abbreviated department or course names must still resolve to the correct entity.
- Follow-up questions must not leak entities between unrelated conversations or users.
- A plausible but low-confidence document match must not override a structured verified record.
- Empty database tables must return safe responses rather than 500 errors.
- Long, punctuation-heavy, or multilingual input must remain bounded and normalized.

### Task 1: Query vocabulary and normalization

**Files:**
- Create: `backend/services/query_understanding.py`
- Modify: `backend/services/classifier.py`
- Test: `tests/test_query_understanding.py`

**Interfaces:**
- Produces `normalize_query(text: str) -> str` and `expand_query(text: str) -> set[str]`.
- Produces alias maps for departments, courses, offices, subjects, and common student terms.

- [ ] Write failing tests for smart punctuation, spelling aliases, abbreviations, and whitespace.
- [ ] Run the focused tests and verify they fail for the missing aliases.
- [ ] Implement the normalization and alias expansion helpers without external packages.
- [ ] Route classifier normalization through the shared helper.
- [ ] Run focused tests and then the full suite.
- [ ] Commit `feat: add local query vocabulary`.

### Task 2: Local retrieval and confidence scoring

**Files:**
- Create: `backend/services/local_retrieval.py`
- Modify: `backend/services/knowledge_search.py`
- Test: `tests/test_local_retrieval.py`

**Interfaces:**
- Produces `rank_candidates(query: str, candidates: list[dict], category: str | None = None) -> list[dict]`.
- Each result includes a score and match reasons; category filters are applied before ranking.

- [ ] Write failing tests for paraphrases, token overlap, aliases, category boundaries, and low-confidence rejection.
- [ ] Verify the tests fail before implementation.
- [ ] Implement weighted token, phrase, alias, and exact-entity scoring with a configurable minimum confidence.
- [ ] Use structured records as a higher-priority candidate source than free-text documents.
- [ ] Verify focused and full test suites.
- [ ] Commit `feat: add verified local retrieval`.

### Task 3: Conversation context

**Files:**
- Create: `backend/services/conversation_context.py`
- Modify: `backend/routes/chat.py`
- Test: `tests/test_conversation_context.py`

**Interfaces:**
- `ConversationContextStore.get(session_id: str) -> dict | None`
- `ConversationContextStore.put(session_id: str, context: dict) -> None`
- `ConversationContextStore.clear(session_id: str) -> None`

- [ ] Write failing tests for a timetable follow-up, expiration, clear behavior, and separate sessions.
- [ ] Verify the tests fail before implementation.
- [ ] Implement bounded in-memory context with TTL and a maximum entity payload.
- [ ] Add an optional session identifier to chat requests while preserving current clients.
- [ ] Use context only when the current query lacks an entity and the intent is compatible.
- [ ] Verify focused and full test suites.
- [ ] Commit `feat: add bounded conversation context`.

### Task 4: Deterministic fallback and answer rendering

**Files:**
- Create: `backend/services/local_answering.py`
- Modify: `backend/routes/chat.py`, `backend/services/ai_service.py`
- Test: `tests/test_local_answering.py`, `tests/test_existing_features.py`

- [ ] Write failing tests for verified answers, clarification prompts, unsupported questions, and optional-AI-disabled behavior.
- [ ] Verify the tests fail before implementation.
- [ ] Implement category-specific templates with source labels and safe unavailable responses.
- [ ] Make local answering the default path; retain AI code only as an explicitly disabled optional adapter.
- [ ] Verify no production path requires Ollama and run the full suite.
- [ ] Commit `feat: make local answering independent of ollama`.

### Task 5: Data coverage and admin verification

**Files:**
- Modify: `backend/scripts/seed_official_vsit.py`, `backend/data/vsit_sources/`, `backend/routes/knowledge.py`
- Test: `tests/test_official_data.py`, `tests/test_admin.py`

- [ ] Write failing tests ensuring sample rows are excluded and verified records retain source metadata.
- [ ] Verify the tests fail before implementation.
- [ ] Extend the seed and admin paths to store source labels, verification status, and update timestamps.
- [ ] Keep empty or unavailable official pages from becoming fabricated records.
- [ ] Run full tests and inspect seeded counts locally.
- [ ] Commit `feat: harden verified data management`.

### Task 6: Production verification

**Files:**
- Modify: `README.md`, `.env.example`
- Test: live Render smoke checks

- [ ] Document runtime independence, supported domains, and the safe fallback behavior.
- [ ] Run pytest with a workspace-local temporary directory, compile checks, and `git diff --check`.
- [ ] Push in small commits and wait for Render deployment success.
- [ ] Test greetings, paraphrased faculty questions, follow-ups, unknown questions, health, academics, resources, and mobile chat behavior on the live URL.
- [ ] Commit `docs: document local intelligence deployment` if documentation changes remain.
