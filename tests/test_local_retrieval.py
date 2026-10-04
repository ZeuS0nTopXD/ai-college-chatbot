from backend.services.local_retrieval import rank_candidates


def test_rank_candidates_prefers_verified_category_and_shared_terms():
    candidates = [
        {"category": "OFFICE", "question": "Where is the student section?", "answer": "Ground floor."},
        {"category": "FACULTY", "question": "Who is the head of computing?", "answer": "Dr. Asif."},
    ]

    results = rank_candidates("where can I go for student documents", candidates, "OFFICE")

    assert results
    assert results[0]["answer"] == "Ground floor."
    assert results[0]["score"] >= 0.35


def test_rank_candidates_rejects_unrelated_low_confidence_matches():
    candidates = [{"category": "OFFICE", "question": "Where is the library?", "answer": "First floor."}]

    assert rank_candidates("tell me about sports teams", candidates, "OFFICE") == []
