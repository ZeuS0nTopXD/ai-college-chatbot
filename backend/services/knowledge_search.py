# ============================================================
# DEPRECATED
# ============================================================
#
# This module previously contained a weaker duplicate of the
# knowledge-base matching logic. The real, better-scored
# implementation now lives in backend/services/classifier.py
# (it accounts for topic match, exact question match, word
# overlap, and important-term weighting instead of simple
# substring counting).
#
# backend/routes/chat.py now imports `search_knowledge`
# directly from classifier.py. This file is kept only so any
# external/old import of `backend.services.knowledge_search`
# does not break, and simply re-exports the real function.
# ============================================================

from backend.services.classifier import search_knowledge  # noqa: F401
