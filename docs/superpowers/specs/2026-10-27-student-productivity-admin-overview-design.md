# Student Productivity and Admin Overview

## Intent

Make the VSIT assistant more useful in daily student workflows while giving administrators a quick view of content health. Students should be able to provide their course/division once, ask from useful starting points, recover recent questions, and keep a transcript. Administrators should see live counts for the content they maintain and feedback that needs attention.

## Goals

- Send an optional student course and division with every chat request so timetable and faculty answers can be scoped correctly.
- Add quick prompt chips, recent-question recall, clear-chat, and transcript download to the assistant view.
- Add an authenticated admin overview endpoint and dashboard panel for resource counts and feedback status.
- Keep the existing visual language, APIs, database, and free deployment model.

## Non-goals

- No new frontend framework, paid service, or external analytics platform.
- No server-side storage of full chat transcripts.
- No change to the existing Ollama/RAG retrieval policy.

## Constraints

- Student context is optional and must remain usable for guest visitors.
- Recent questions and transcript export are local-browser features and must not contain secrets.
- Admin overview data is protected by the existing admin JWT dependency.
- Existing endpoints and response shapes remain backward compatible.

## Approach

The student page will add a compact context bar beside the assistant controls. `script.js` will persist those values in local storage and include them in the current `POST /chat` payload. Quick prompts and recent questions will use the same submit path, so they exercise the real assistant. A download action will serialize the visible conversation into a plain-text file.

The backend will expose `GET /api/admin/overview`, aggregating counts from the existing academic, knowledge, faculty, office, document, student, and feedback tables plus the number of feedback items that are not reviewed. The admin page will render this as a dashboard tab and keep the existing CRUD tabs unchanged.

## Acceptance criteria

- A student selecting `B.Sc. Information Technology` and division `B` sends both values with a chat request; clearing the fields removes them.
- Refreshing the student page preserves course/division and recent questions; clearing the chat does not clear the profile context.
- Quick prompts add a real user message and assistant response; recent prompts can be reused.
- Download transcript produces a text file with the visible conversation.
- An authenticated admin can load overview counts; unauthenticated requests receive 401.
- Existing tests remain green.
