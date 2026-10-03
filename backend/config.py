import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    database_url: str
    admin_password: str
    token_secret: str
    token_ttl_minutes: int
    max_upload_bytes: int
    document_storage_path: Path
    cors_origins: tuple[str, ...]
    ollama_url: str
    ollama_model: str

    @classmethod
    def from_env(cls) -> "Settings":
        origins = tuple(
            origin.strip()
            for origin in os.getenv(
                "CORS_ORIGINS",
                "http://127.0.0.1:8000,http://localhost:8000",
            ).split(",")
            if origin.strip()
        )
        return cls(
            database_url=os.getenv(
                "DATABASE_URL",
                "sqlite:///./data/vsit_student_assistant.db",
            ),
            admin_password=os.getenv("ADMIN_PASSWORD", "change-me"),
            token_secret=os.getenv("TOKEN_SECRET", "development-secret-change-me"),
            token_ttl_minutes=int(os.getenv("TOKEN_TTL_MINUTES", "60")),
            max_upload_bytes=int(os.getenv("MAX_UPLOAD_BYTES", str(10 * 1024 * 1024))),
            document_storage_path=Path(
                os.getenv("DOCUMENT_STORAGE_PATH", "./data/documents")
            ),
            cors_origins=origins,
            ollama_url=os.getenv(
                "OLLAMA_URL",
                "http://localhost:11434/api/generate",
            ),
            ollama_model=os.getenv("OLLAMA_MODEL", "llama3.2:3b"),
        )
