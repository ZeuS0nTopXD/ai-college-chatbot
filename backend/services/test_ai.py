from backend.services.ai_service import get_ai_response


response = get_ai_response(
    "How can I prepare effectively for my final semester exams?",
    "ACADEMIC"
)

print("\nAI RESPONSE:\n")
print(response)