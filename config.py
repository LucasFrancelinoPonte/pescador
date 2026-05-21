from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", os.getenv("SESSION_SECRET", "dev-secret-key-change-me"))
    SESSION_SECRET = os.getenv("SESSION_SECRET", SECRET_KEY)
    WTF_CSRF_SECRET_KEY = os.getenv("WTF_CSRF_SECRET_KEY", SESSION_SECRET)
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{(BASE_DIR / 'app.db').as_posix()}",
    )
    USERS_XLSX_PATH = os.getenv(
        "USERS_XLSX_PATH",
        str(BASE_DIR / "mock_data" / "users.xlsx"),
    )
    IMPORT_REQUIRED_COLUMNS = tuple(
        column.strip().lower()
        for column in os.getenv("IMPORT_REQUIRED_COLUMNS", "nome,cpf").split(",")
        if column.strip()
    )
    SQL_CONSOLE_TABLE_NAME = os.getenv("SQL_CONSOLE_TABLE_NAME", "socioeconomic_submissions")
    LOG_FILE = os.getenv("LOG_FILE", str(BASE_DIR / "logs" / "app.log"))
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    VERCEL = os.getenv("VERCEL", "false").lower() == "true"
    ENABLE_DATABASE = os.getenv("ENABLE_DATABASE", "false").lower() == "true"
    ENABLE_STARTUP_TASKS = os.getenv("ENABLE_STARTUP_TASKS", "false").lower() == "true"
    DASHBOARD_PAGE_SIZE = int(os.getenv("DASHBOARD_PAGE_SIZE", "8"))
    DEFAULT_PAGE_SIZE = int(os.getenv("DEFAULT_PAGE_SIZE", "10"))
    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "true" if VERCEL else "false").lower() == "true"
    SESSION_COOKIE_SAMESITE = os.getenv("SESSION_COOKIE_SAMESITE", "Lax")
    WTF_CSRF_TIME_LIMIT = int(os.getenv("WTF_CSRF_TIME_LIMIT", "3600"))
    GOOGLE_SHEETS_ENABLED = os.getenv("GOOGLE_SHEETS_ENABLED", "false").lower() == "true"
    GOOGLE_SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE", str(BASE_DIR / "service-account.json"))
    GOOGLE_SHEETS_SPREADSHEET_ID = os.getenv("GOOGLE_SHEETS_SPREADSHEET_ID", "")
    GOOGLE_SHEETS_USERS_WORKSHEET = os.getenv("GOOGLE_SHEETS_USERS_WORKSHEET", "Usuarios")
    GOOGLE_SHEETS_SUBMISSIONS_WORKSHEET = os.getenv("GOOGLE_SHEETS_SUBMISSIONS_WORKSHEET", "Formularios")
    GOOGLE_SHEETS_EXPORT_WORKSHEET = os.getenv("GOOGLE_SHEETS_EXPORT_WORKSHEET", "Exportacao")
    GOOGLE_SHEETS_CACHE_DIR = os.getenv("GOOGLE_SHEETS_CACHE_DIR", str(BASE_DIR / "cache" / "google_sheets"))
    GOOGLE_SHEETS_SYNC_ON_STARTUP = os.getenv("GOOGLE_SHEETS_SYNC_ON_STARTUP", "true").lower() == "true"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    # Seed mock data on startup (set to "false" to disable)
    SEED_ON_STARTUP = os.getenv("SEED_ON_STARTUP", "true").lower() == "true"
    # Path to mock data folder
    MOCK_DATA_DIR = os.getenv("MOCK_DATA_DIR", str(BASE_DIR / "mock_data"))