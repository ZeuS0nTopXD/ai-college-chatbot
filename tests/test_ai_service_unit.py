from backend.services import ai_service


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
