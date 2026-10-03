import os

import requests
from dotenv import load_dotenv

load_dotenv()

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")

MODEL_NAME = os.getenv("OLLAMA_MODEL", "llama3.2:3b")


# -----------------------------------------
# SHARED OLLAMA CALL
#
# Centralizes the HTTP call so every caller
# gets the same timeout + error handling,
# instead of crashing the /chat endpoint
# with an unhandled 500 error whenever
# Ollama is not running or times out.
# -----------------------------------------

def _call_ollama(prompt):

    data = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }

    try:

        response = requests.post(
            OLLAMA_URL,
            json=data,
            timeout=60
        )

        response.raise_for_status()

        result = response.json()

        return result.get("response", "").strip() or (
            "I couldn't generate a response for that. "
            "Please try rephrasing your question."
        )

    except requests.exceptions.ConnectionError:

        return (
            "I'm unable to reach the AI engine right now "
            "(it looks like the local AI service is not running). "
            "Please try again in a moment, or contact the "
            "concerned department for urgent queries."
        )

    except requests.exceptions.Timeout:

        return (
            "The AI engine took too long to respond. "
            "Please try again with a shorter or simpler question."
        )

    except requests.exceptions.RequestException:

        return (
            "Something went wrong while generating a response. "
            "Please try again."
        )


# -----------------------------------------
# NORMAL AI RESPONSE
# Used for:
# ACADEMIC
# CAREER
# GENERAL
# -----------------------------------------

def get_ai_response(user_message, category):

    prompt = f"""
You are an AI-powered College Student Assistance Chatbot.

The student's question belongs to the category: {category}.

Provide a helpful, accurate, clear and student-friendly answer.

Keep the answer concise but informative.

Student Question:
{user_message}
"""

    return _call_ollama(prompt)


# -----------------------------------------
# CONTEXTUAL AI RESPONSE
# Used for:
# VSIT
# NGO
#
# This function combines:
# Student Question + Database Information + AI
# -----------------------------------------

def get_contextual_ai_response(
    user_message,
    category,
    knowledge_context
):

    organization_name = ""

    if category == "VSIT":
        organization_name = """
VSIT refers specifically to Vidyalankar School of Information Technology
in Mumbai.

Never expand VSIT as any other institution.
Never invent a different full form for VSIT.
"""

    elif category == "NGO":
        organization_name = """
The NGO information provided below may be sample information
until official NGO data is added.
"""

    prompt = f"""
You are an AI-powered College Student Assistance Chatbot.

{organization_name}

The student's question belongs to the category: {category}.

Use the information provided below as the main source
for answering the student's question.

Student Question:
{user_message}

Available Information:
{knowledge_context}

IMPORTANT RULES:

1. Use the provided information as the main source.
2. Do not invent facts that are not present in the information.
3. Never invent or incorrectly expand the name VSIT.
4. If the information is incomplete, clearly tell the student.
5. Do not claim sample information is official.
6. Do not invent fees, dates, attendance percentages,
   contact details, policies, or website links.
7. Keep the answer concise and student-friendly.
8. Provide only the answer to the student.

Now provide the best possible answer.
"""

    return _call_ollama(prompt)


def get_missing_info_response(user_message, category):

    organization_name = ""

    if category == "VSIT":
        organization_name = """
VSIT refers specifically to Vidyalankar School of Information Technology
in Mumbai.

Never expand VSIT as any other institution.
Do not invent or guess the full form of VSIT.
"""

    elif category == "NGO":
        organization_name = """
The NGO information in this project may be sample information
until official NGO data is added.
"""

    prompt = f"""
You are an AI-powered College Student Assistance Chatbot.

{organization_name}

The student's question belongs to the category: {category}.

However, no relevant or verified information was found
in the chatbot's knowledge base.

Student Question:
{user_message}

IMPORTANT RULES:

1. Do not invent facts.
2. Do not guess official information.
3. Never invent or expand the name VSIT incorrectly.
4. Do not provide fake dates, percentages, fees, contact details,
   schedules, policies, or website links.
5. Clearly tell the student that this information is currently
   not available in the chatbot's knowledge base.
6. If the question is about VSIT, refer to it as:
   "Vidyalankar School of Information Technology (VSIT)"
   or simply "VSIT".
7. Suggest checking the official college source or contacting
   the concerned department.
8. Keep the answer concise, helpful, and student-friendly.
9. Do not use placeholder links such as:
   "[official VSIT website]".

Provide only the answer to the student.
"""

    return _call_ollama(prompt)