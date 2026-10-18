from types import SimpleNamespace

from backend.data.official_vsit_data import OFFICIAL_KNOWLEDGE_DATA
from backend.services.classifier import classify_question, search_knowledge


def test_common_typos_and_shorthand_reach_the_right_intent():
    rows = [SimpleNamespace(**item) for item in OFFICIAL_KNOWLEDGE_DATA]
    assert search_knowledge("bsc it reqs??", rows).question == "What are the B.Sc. IT admission requirements?"
    assert search_knowledge("placemnt start wen", rows).question == "When do campus placements begin at VSIT?"
    assert classify_question("hey u good") == "GREETING"
