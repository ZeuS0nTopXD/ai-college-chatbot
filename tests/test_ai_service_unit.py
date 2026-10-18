from backend.services import ai_service
import requests


def test_grounded_response_uses_ollama_wording(monkeypatch):
    monkeypatch.setattr(ai_service, "_call_ollama", lambda _prompt: "A natural, concise explanation.")
    assert ai_service.get_grounded_response(
        "What is VSIT?", "VSIT", "VSIT is Vidyalankar School of Information Technology."
    ) == "A natural, concise explanation."


def test_grounded_response_falls_back_to_verified_text(monkeypatch):
    verified = "The official answer is available from the college."
    monkeypatch.setattr(
        ai_service,
        "_call_ollama",
        lambda _prompt: "The AI engine is temporarily unavailable. Please try again.",
    )
    assert ai_service.get_grounded_response("What is VSIT?", "VSIT", verified) == verified


def test_connection_failure_does_not_expose_ai_internals(monkeypatch):
    def fail(*_args, **_kwargs):
        raise requests.exceptions.ConnectionError()

    monkeypatch.setattr(ai_service.requests, "post", fail)
    response = ai_service._call_ollama("hello")
    assert "optional ai assistant" not in response.lower()
    assert "ollama" not in response.lower()


def test_contextual_prompt_uses_retrieved_context_as_evidence(monkeypatch):
    captured = {}

    def capture(prompt):
        captured["prompt"] = prompt
        return "grounded answer"

    monkeypatch.setattr(ai_service, "_call_ollama", capture)
    assert ai_service.get_contextual_ai_response(
        "when is the exam form due?",
        "GENERAL",
        "Source type: uploaded college document\nDocument excerpt: Due 12 September.",
    ) == "grounded answer"
    assert "Retrieved source context" in captured["prompt"]
    assert "Due 12 September" in captured["prompt"]
    assert "Treat the retrieved context as evidence" in captured["prompt"]
