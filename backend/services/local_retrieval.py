import re

from backend.services.query_understanding import expand_query, normalize_query


STOP_WORDS = {"a", "an", "the", "is", "are", "of", "for", "to", "me", "my", "can", "you", "tell"}


def _tokens(value: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-z0-9]+", normalize_query(value))
        if token not in STOP_WORDS and len(token) > 1
    }


def rank_candidates(query: str, candidates: list[dict], category: str | None = None) -> list[dict]:
    query_forms = expand_query(query)
    query_tokens = set().union(*(_tokens(form) for form in query_forms)) if query_forms else set()
    ranked = []
    for candidate in candidates:
        if category and normalize_query(candidate.get("category", "")) != normalize_query(category):
            continue
        text = " ".join(str(candidate.get(key, "")) for key in ("topic", "question", "answer", "title"))
        candidate_tokens = _tokens(text)
        if not candidate_tokens or not query_tokens:
            continue
        overlap = len(query_tokens & candidate_tokens) / max(len(query_tokens), 1)
        phrase_bonus = max((0.15 for form in query_forms if normalize_query(form) and normalize_query(form) in normalize_query(text)), default=0)
        score = min(1.0, overlap * 0.85 + phrase_bonus)
        if score >= 0.35:
            ranked.append({**candidate, "score": round(score, 3), "match_reasons": sorted(query_tokens & candidate_tokens)})
    return sorted(ranked, key=lambda item: item["score"], reverse=True)
