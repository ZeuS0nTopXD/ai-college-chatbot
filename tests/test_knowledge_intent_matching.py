from types import SimpleNamespace

from backend.data.official_vsit_data import OFFICIAL_KNOWLEDGE_DATA
from backend.services.classifier import search_knowledge
from backend.services.official_link_service import answer_official_source_question


def test_high_signal_questions_select_the_matching_verified_entry():
    rows = [SimpleNamespace(**item) for item in OFFICIAL_KNOWLEDGE_DATA]
    assert search_knowledge("when do campus placements begin?", rows).question == (
        "When do campus placements begin at VSIT?"
    )
    assert search_knowledge("where is the library?", rows).question == "Where is the VSIT library?"
    assert search_knowledge("where is the library and when is it open?", rows).question == (
        "What are the VSIT library timings?"
    )
    assert search_knowledge("how do I apply for a transcript from VSIT?", rows).question == (
        "How do I apply for a transcript from VSIT?"
    )
    assert search_knowledge("What are the BSC IT admission requirements?", rows).question == (
        "What are the B.Sc. IT admission requirements?"
    )
    assert search_knowledge("what marks do I need for information technology?", rows).question == (
        "What are the B.Sc. IT admission requirements?"
    )


def test_library_resource_questions_have_verified_hours_even_without_database_rows():
    answer = answer_official_source_question("Where is the library and when is it open?")

    assert answer["resource_url"] == "https://vsit.edu.in/library/"
    assert "Monday to Saturday" in answer["bot_response"]
    assert "X Block library" in answer["bot_response"]
