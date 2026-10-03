import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import declarative_base, scoped_session, sessionmaker


Base = declarative_base()
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False))
engine = None


def configure_database(database_url: str):
    global engine

    url = make_url(database_url)
    connect_args = {}
    if url.get_backend_name() == "sqlite":
        connect_args["check_same_thread"] = False
        if url.database and url.database != ":memory:":
            Path(url.database).expanduser().resolve().parent.mkdir(
                parents=True,
                exist_ok=True,
            )

    SessionLocal.remove()
    if engine is not None:
        engine.dispose()
    engine = create_engine(database_url, connect_args=connect_args)
    SessionLocal.configure(bind=engine)
    return engine


configure_database(
    os.getenv("DATABASE_URL", "sqlite:///./data/vsit_student_assistant.db")
)
