import os
from functools import lru_cache

try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings


class Settings(BaseSettings):
    # 🔐 Security
    SECRET_KEY: str = "changeme"

    # 🗄️ Database
    DATABASE_URL: str = "sqlite:///./autoinsight.db"

    # 🤖 LLM CONFIG
    LLM_PROVIDER: str = "groq"
    LLM_MODEL: str = "llama-3.1-8b-instant"
    GROQ_API_KEY: str = ""

    OPENAI_API_KEY: str = ""
    LOCAL_LLM_URL: str = ""

    # 📧 Email
    EMAIL_FROM: str = "noreply@autoinsight.ai"
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASS: str = ""

    # 🌐 Frontend
    FRONTEND_URL: str = "http://localhost:5173"

    # 🔑 Auth
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7

    # 📂 Storage
    UPLOAD_DIR: str = "data/uploads"
    ANALYSIS_DIR: str = "data/analysis"
    REPORT_DIR: str = "data/reports"
    HISTORY_FILE: str = "data/query_history.json"

    # ✅ FIX HERE
    REDIS_URL: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings():
    return Settings()


settings = get_settings()


# 📁 Create required directories on startup
REQUIRED_DIRS = [
    "data",
    settings.UPLOAD_DIR,
    settings.ANALYSIS_DIR,
    settings.REPORT_DIR,
]

for directory in REQUIRED_DIRS:
    os.makedirs(directory, exist_ok=True)