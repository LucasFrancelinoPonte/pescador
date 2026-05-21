from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

import pandas as pd
from flask import current_app

from ..models import User


GOOGLE_SHEETS_SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]


@dataclass(slots=True)
class GoogleSheetsConfig:
    enabled: bool
    service_account_file: Path
    spreadsheet_id: str
    users_worksheet: str
    submissions_worksheet: str
    export_worksheet: str
    cache_dir: Path
    sync_on_startup: bool


def _config() -> GoogleSheetsConfig:
    return GoogleSheetsConfig(
        enabled=bool(current_app.config.get("GOOGLE_SHEETS_ENABLED", False)),
        service_account_file=Path(current_app.config.get("GOOGLE_SERVICE_ACCOUNT_FILE", "service-account.json")).expanduser(),
        spreadsheet_id=str(current_app.config.get("GOOGLE_SHEETS_SPREADSHEET_ID", "")).strip(),
        users_worksheet=str(current_app.config.get("GOOGLE_SHEETS_USERS_WORKSHEET", "Usuarios")).strip(),
        submissions_worksheet=str(current_app.config.get("GOOGLE_SHEETS_SUBMISSIONS_WORKSHEET", "Formularios")).strip(),
        export_worksheet=str(current_app.config.get("GOOGLE_SHEETS_EXPORT_WORKSHEET", "Exportacao")).strip(),
        cache_dir=Path(current_app.config.get("GOOGLE_SHEETS_CACHE_DIR", "cache/google_sheets")).expanduser(),
        sync_on_startup=bool(current_app.config.get("GOOGLE_SHEETS_SYNC_ON_STARTUP", True)),
    )


def _ensure_cache_dir() -> Path:
    cache_dir = _config().cache_dir
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def _cache_file(name: str) -> Path:
    safe_name = "".join(character if character.isalnum() or character in {"-", "_"} else "_" for character in name.lower())
    return _ensure_cache_dir() / f"{safe_name}.json"


def _read_cache(name: str) -> list[dict[str, Any]]:
    path = _cache_file(name)
    if not path.exists():
        return []

    try:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
            return data if isinstance(data, list) else []
    except json.JSONDecodeError:
        current_app.logger.warning("Invalid JSON cache file detected: %s", path)
        return []


def _write_cache(name: str, records: list[dict[str, Any]]) -> None:
    path = _cache_file(name)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(records, handle, ensure_ascii=False, indent=2, default=str)


def _client() -> Any:
    import gspread
    from google.oauth2.service_account import Credentials

    config = _config()
    if not config.service_account_file.exists():
        raise FileNotFoundError(f"Google service account file not found: {config.service_account_file}")

    credentials = Credentials.from_service_account_file(
        str(config.service_account_file),
        scopes=GOOGLE_SHEETS_SCOPES,
    )
    return gspread.authorize(credentials)


def _spreadsheet():
    config = _config()
    if not config.spreadsheet_id:
        raise ValueError("GOOGLE_SHEETS_SPREADSHEET_ID is not configured.")
    return _client().open_by_key(config.spreadsheet_id)


def _get_or_create_worksheet(title: str, rows: int = 1000, cols: int = 30):
    from gspread.exceptions import WorksheetNotFound

    spreadsheet = _spreadsheet()
    try:
        return spreadsheet.worksheet(title)
    except WorksheetNotFound:
        return spreadsheet.add_worksheet(title=title, rows=str(rows), cols=str(cols))


def _worksheet_records(title: str) -> list[dict[str, Any]]:
    try:
        worksheet = _spreadsheet().worksheet(title)
        return worksheet.get_all_records()
    except Exception as exc:
        current_app.logger.warning("Google Sheets read failed for worksheet '%s': %s", title, exc)
        return _read_cache(title)


@lru_cache(maxsize=1)
def load_users() -> tuple[User, ...]:
    config = _config()
    records = _worksheet_records(config.users_worksheet) if config.enabled else _read_cache(config.users_worksheet)
    if config.enabled and records:
        _write_cache(config.users_worksheet, records)

    users: list[User] = []
    for record in records:
        email = str(record.get("email", "")).strip().lower()
        password = str(record.get("senha", ""))
        name = str(record.get("nome", "")).strip()
        perfil = str(record.get("perfil", "")).strip()
        if email and password:
            users.append(User(email=email, password=password, name=name, perfil=perfil))
    return tuple(users)


def refresh_users_cache() -> tuple[User, ...]:
    load_users.cache_clear()
    return load_users()


def sync_startup_cache() -> None:
    config = _config()
    if not config.enabled or not config.sync_on_startup:
        return

    try:
        refresh_users_cache()
    except Exception as exc:
        current_app.logger.warning("Startup Google Sheets sync failed: %s", exc)


def append_submission_record(record: dict[str, Any]) -> None:
    config = _config()
    records = _read_cache(config.submissions_worksheet)
    records.append(record)
    _write_cache(config.submissions_worksheet, records)

    if not config.enabled:
        return

    try:
        worksheet = _get_or_create_worksheet(config.submissions_worksheet)
        existing_values = worksheet.get_all_values()
        if not existing_values:
            worksheet.append_row(list(record.keys()), value_input_option="USER_ENTERED")
        worksheet.append_row([str(value) for value in record.values()], value_input_option="USER_ENTERED")
    except Exception as exc:
        current_app.logger.warning("Google Sheets append failed for submissions: %s", exc)


def sync_dataframe_to_sheet(frame: pd.DataFrame, worksheet_title: str | None = None) -> None:
    config = _config()
    title = worksheet_title or config.export_worksheet
    records = frame.fillna("").to_dict(orient="records")
    _write_cache(title, records)

    if not config.enabled:
        return

    try:
        worksheet = _get_or_create_worksheet(title)
        values = [list(frame.columns)] + frame.fillna("").astype(str).values.tolist()
        worksheet.clear()
        worksheet.resize(rows=max(len(values), 1), cols=max(len(frame.columns), 1))
        worksheet.update(values, "A1")
    except Exception as exc:
        current_app.logger.warning("Google Sheets export sync failed for '%s': %s", title, exc)