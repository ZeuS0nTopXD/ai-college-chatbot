# Independent Local Intelligence for VSIT Assistant

## Goal

Make the chatbot useful without Ollama, hosted AI APIs, or runtime model keys. Student questions should be understood through normalization, aliases, semantic retrieval, structured records, and short-term conversation context. Answers must remain grounded in verified VSIT data.

## Scope

The assistant will support natural-language questions about faculty, departments, offices, timetables, examinations, academic dates, results, admissions, courses, placements, fees, facilities, notices, and official contact information. It will handle paraphrases, common abbreviations, punctuation variation, spelling mistakes, and follow-up questions when the needed data exists.

Unsupported or ambiguous questions will return a clear data-unavailable or clarification response. The system will never invent dates, fees, names, policies, or links.

## Architecture

1. **Input normalization**: Unicode normalization, punctuation cleanup, typo aliases, course and department aliases, and language-safe whitespace handling.
2. **Intent and entity extraction**: deterministic patterns plus configurable synonym dictionaries for intents, departments, courses, days, offices, subjects, and academic terms.
3. **Retrieval**: weighted lexical and semantic-lite scoring over verified knowledge records and document chunks. Exact structured records outrank free-text matches.
4. **Conversation context**: store the last resolved intent and entities per session, allowing follow-ups such as “what about Monday?” without requiring the original subject again.
5. **Answer rendering**: category-specific templates with source labels and confidence thresholds. Low-confidence matches ask for clarification or report unavailable information.
6. **Runtime independence**: remove the production dependency on Ollama. The optional AI integration remains disabled by default and is never required for a successful answer.

## Data requirements

The official VSIT website and approved college documents remain the source of truth. Seed data will be separated from sample data, and sample records will not be exposed as official answers. The admin panel will support adding and updating verified records and documents.

## Validation and safety

Chat input will reject blank and oversized values. Retrieval will enforce confidence thresholds and category boundaries, preventing faculty questions from returning all faculty or unrelated documents. API responses will remain stable when the database is empty or optional services are unavailable.

## Testing and rollout

Add tests for paraphrases, typos, aliases, follow-up context, ambiguity, unsupported questions, source attribution, and empty datasets. Run the full test suite, compile checks, and live smoke tests against Render before release. Roll out in small commits so each retrieval change is reversible.
