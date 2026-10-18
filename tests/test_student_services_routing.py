from backend.services.classifier import classify_question


def test_certificate_procedure_is_student_support_not_office():
    assert classify_question("How do I get a bonafide certificate from VSIT?") == "STUDENT_SUPPORT"
    assert classify_question("How do I apply for a transcript from VSIT?") == "STUDENT_SUPPORT"
    assert classify_question("What should I do if I lose my ID card?") == "STUDENT_SUPPORT"


def test_explicit_student_section_contact_stays_office():
    assert classify_question("What is the Student Section contact for bonafide certificates?") == "OFFICE"
