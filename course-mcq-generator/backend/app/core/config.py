import os
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Course MCQ Generator"

    # CORS Settings
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173"
    ]

    # Google Gemini API Settings
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    GEMINI_MODEL: str = "gemini-2.5-pro"
    GEMINI_EMBEDDING_MODEL: str = "models/gemini-embedding-001"

    # File Settings
    COURSE_PDF_DIR: str = "coursePdf"
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB

    # Vector Database Settings
    FAISS_INDEX_PATH: str = "faiss_index.bin"
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()