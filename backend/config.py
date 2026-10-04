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
    app_env: str = "development"

    def __post_init__(self) -> None:
        for field_name in ("admin_password", "token_secret"):
            if not getattr(self, field_name).strip():
                raise ValueError(f"{field_name} must not be empty")

    @classmethod
    def from_env(cls) -> "Settings":
        app_env = os.getenv("APP_ENV", "development").strip().lower()
        admin_password = os.getenv("ADMIN_PASSWORD", "change-me")
        token_secret = os.getenv(
            "TOKEN_SECRET",
            "development-secret-change-me-before-deploying",
        )
        if app_env in {"production", "staging"}:
            if admin_password in {"", "change-me"} or len(admin_password) < 12:
                raise ValueError("ADMIN_PASSWORD must be at least 12 characters in production")
            if token_secret in {"", "development-secret-change-me-before-deploying"} or len(token_secret) < 32:
                raise ValueError("TOKEN_SECRET must be at least 32 characters in production")
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
            admin_password=admin_password,
            token_secret=token_secret,
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
            app_env=app_env,
        )
