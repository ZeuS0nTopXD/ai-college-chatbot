import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.database.database import engine, Base

load_dotenv()

# ============================================================
# IMPORT ALL DATABASE MODELS
# ============================================================
# These imports are required so SQLAlchemy knows about all
# database tables before create_all() is executed.

from backend.models.timetable import Timetable
from backend.models.knowledge import KnowledgeBase
from backend.models.result import Result
from backend.models.faculty import Faculty
from backend.models.office import Office


# ============================================================
# CREATE DATABASE TABLES
# ============================================================
# This will create the tables if they do not already exist.
#
# Expected tables:
#   - timetable
#   - knowledge_base
#   - results
#
# Existing data will NOT be deleted by create_all().

Base.metadata.create_all(bind=engine)


# ============================================================
# IMPORT ROUTERS
# ============================================================

from backend.routes import chat
from backend.routes import knowledge
from backend.routes import timetable
from backend.routes import result


# ============================================================
# CREATE FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="VSIT Student Assistant API",
    description="AI-powered student assistance chatbot for VSIT",
    version="1.0.0"
)


# ============================================================
# CORS CONFIGURATION
# ============================================================
# This allows your frontend running on port 5500
# to communicate with FastAPI running on port 8000.
# Configurable via CORS_ORIGINS in .env (comma-separated).

cors_origins = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        "http://127.0.0.1:5500,http://localhost:5500"
    ).split(",")
]
app.add_middleware(
    CORSMiddleware,

    allow_origins=cors_origins,

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)


# ============================================================
# INCLUDE ROUTES
# ============================================================

app.include_router(chat.router)
app.include_router(knowledge.router)
app.include_router(timetable.router)
app.include_router(result.router)


# ============================================================
# HOME / API STATUS
# ============================================================

@app.get("/")
def home():
    return {
        "message": "VSIT Student Assistant API is running"
    }