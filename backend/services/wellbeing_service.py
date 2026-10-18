"""Safe, lightweight support for common student wellbeing questions."""

import re

_CRISIS_PATTERNS = (r"\bkill myself\b", r"\bsuicid(?:e|al)\b", r"\bself[- ]?harm\b", r"\bhurt myself\b", r"\bend my life\b", r"\bnot want to live\b")
_WELLBEING_PATTERNS = (r"\bstress(?:ed|ful)?\b", r"\banxious\b|\banxiety\b", r"\boverwhelm(?:ed|ing)?\b", r"\bpanic(?: attack)?\b", r"\bburn(?:ed|out)\b|\bburnout\b", r"\bdepress(?:ed|ion)\b", r"\blonely\b|\bloneliness\b", r"\bcan'?t cope\b|\bcannot cope\b", r"\bexam pressure\b|\bstudy pressure\b", r"\bfeeling (?:sad|low|down)\b")

def _matches(message: str, patterns: tuple[str, ...]) -> bool:
    text = re.sub(r"\s+", " ", (message or "").strip().lower())
    return any(re.search(pattern, text) for pattern in patterns)

def is_wellbeing_crisis(message: str) -> bool:
    return _matches(message, _CRISIS_PATTERNS)

def is_wellbeing_question(message: str) -> bool:
    return is_wellbeing_crisis(message) or _matches(message, _WELLBEING_PATTERNS)

def wellbeing_response(message: str, crisis: bool | None = None) -> str:
    if crisis is None:
        crisis = is_wellbeing_crisis(message)
    if crisis:
        return ("I’m really sorry you’re going through this. If you might act on these thoughts or you’re in immediate danger, contact local emergency services now, go to the nearest emergency department, and tell a trusted person who can stay with you. Please don’t face this alone. I can also help you find a VSIT support route.")
    return ("I’m sorry this feels difficult. Try pausing for a minute, taking a few slow breaths, drinking some water, and choosing one small next step instead of solving everything at once. You deserve support—consider telling a trusted friend, faculty member, or VSIT office. If you feel unsafe or might hurt yourself, contact local emergency services and someone you trust right now.")
