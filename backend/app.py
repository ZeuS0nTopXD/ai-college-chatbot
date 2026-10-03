from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.config import Settings
from backend.database.database import Base, configure_database


PROJECT_ROOT = Path(__file__).resolve().parents[1]
FRONTEND_DIR = PROJECT_ROOT / "frontend"


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings.from_env()
    engine = configure_database(settings.database_url)

    from backend.models.faculty import Faculty  # noqa: F401
    from backend.models.academic import AcademicEvent  # noqa: F401
    from backend.models.knowledge import KnowledgeBase  # noqa: F401
    from backend.models.office import Office  # noqa: F401
    from backend.models.result import Result  # noqa: F401
    from backend.models.timetable import Timetable  # noqa: F401

    Base.metadata.create_all(bind=engine)

    from backend.routes import academic, chat, knowledge, result, timetable

    app = FastAPI(
        title="VSIT Student Assistant API",
        description="AI-powered student assistance chatbot for VSIT",
        version="2.0.0",
    )
    app.state.settings = settings
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.cors_origins),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(chat.router)
    app.include_router(knowledge.router)
    app.include_router(timetable.router)
    app.include_router(result.router)
    app.include_router(academic.router)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    app.mount(
        "/",
        StaticFiles(directory=FRONTEND_DIR, html=True),
        name="frontend",
    )
    return app
