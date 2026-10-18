# Student Accounts and Feedback Design

## Goal

Add student registration/login and a feedback workflow to the existing VSIT assistant without changing the current guest chat or administrator content-management flow.

## Scope

The student-facing site will provide:

- Registration with name, email, and password.
- Student login, logout, and a small signed-in account state.
- A feedback form with a 1–5 rating, message, and optional page/context value.
- Clear success/error states and a signed-in requirement for submitting feedback.

The existing administrator page will provide:

- The existing password-based administrator login and all current management tabs.
- A dedicated feedback tab that lists submissions, shows student metadata and timestamps, marks feedback as reviewed, and deletes feedback.

The existing assistant remains available to guests. Student authentication is only required for account and feedback actions.

## Architecture

Use the existing FastAPI, SQLAlchemy, Pydantic, JWT, and static HTML/JavaScript structure. Add a `StudentUser` model and a `Feedback` model, import both before `Base.metadata.create_all`, and add separate student auth and feedback routes. Student tokens use the existing signing secret with a `student` subject/role claim; administrator tokens retain the current `admin` subject and API contract.

Student passwords are stored as one-way hashes using the project's available password hashing dependency. Email addresses are normalized to lowercase and unique. Feedback records reference the student user, store a bounded rating/message/context, default to `new`, and are returned newest first. Admin feedback endpoints reuse `require_admin` and never expose password hashes.

## API contract

### Student authentication

- `POST /api/auth/register` — `{name, email, password}` → `{access_token, token_type, user}`; rejects duplicate email and invalid input.
- `POST /api/auth/student-login` — `{email, password}` → the same response; rejects unknown or invalid credentials.
- `GET /api/auth/student-me` — bearer student token → the public user object.
- Existing `POST /api/auth/login` and `GET /api/auth/me` remain administrator-only and backward compatible.

### Feedback

- `POST /api/feedback` — bearer student token and `{rating, message, context?}` → created feedback.
- `GET /api/admin/feedback` — bearer admin token → newest-first feedback list.
- `PATCH /api/admin/feedback/{id}` — `{status}` where status is `new` or `reviewed`.
- `DELETE /api/admin/feedback/{id}` — removes a feedback record.

## Frontend behavior

The student navigation gets `Sign in`/`Register` controls and a feedback area that switches to the login prompt when no student token exists. Student tokens live in `sessionStorage`; logout clears them. The admin page gets a Feedback tab and uses the existing `adminFetch` authorization helper. All text is rendered with `textContent`/DOM APIs rather than injecting untrusted feedback content as HTML.

## Validation and security

- Name: 2–100 characters after trimming.
- Email: valid email format, normalized lowercase, maximum 254 characters.
- Password: minimum 8 characters, maximum 128 characters.
- Feedback rating: integer 1–5.
- Feedback message: 5–2000 characters after trimming.
- Context: optional, maximum 80 characters.
- Student endpoints reject administrator tokens and vice versa.
- Duplicate registration returns a conflict without revealing password data.
- Login responses and admin listings never include password hashes.

## Testing

Backend tests will cover registration/login/me, duplicate registration, invalid credentials, role separation, feedback creation, validation, admin listing/update/delete, and unauthorized access. Frontend tests will assert that the student controls/forms and admin feedback tab are present and wired to the documented endpoints. Existing authentication and admin CRUD tests must continue to pass.

## Out of scope

Password reset email, social login, email verification, per-student chat history, and public anonymous feedback are deferred until a later request.
