import re
import unicodedata


ALIASES = {
    "it": "information technology",
    "ty it": "tyit",
    "tyit": "tyit",
    "hod": "head of department",
    "h o d": "head of department",
    "who runs": "head of department",
    "who leads": "head of department",
    "in charge of": "head of department",
    "principal office": "principal",
    "exam cell": "examination cell",
    "student desk": "student section",
}

TYPO_CORRECTIONS = {
    "wht": "what",
    "computng": "computing",
    "computin": "computing",
    "facult": "faculty",
    "timetablee": "timetable",
    "admisson": "admission",
    "placemnt": "placement",
}


def normalize_query(text: str) -> str:
    normalized = unicodedata.normalize("NFKC", str(text or "")).lower()
    normalized = "".join(
        " " if unicodedata.category(char).startswith("P") else char
        for char in normalized
    )
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return " ".join(TYPO_CORRECTIONS.get(token, token) for token in normalized.split())


def expand_query(text: str) -> set[str]:
    normalized = normalize_query(text)
    expanded = {normalized}
    for source, target in ALIASES.items():
        if source in normalized:
            expanded.add(normalized.replace(source, target))
            expanded.add(target)
    return expanded
