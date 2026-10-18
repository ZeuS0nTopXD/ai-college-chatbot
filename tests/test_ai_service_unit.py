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
