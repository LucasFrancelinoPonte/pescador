from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import pandas as pd
from flask import current_app

from ..models import User
from .sheet_service import load_users as load_users_from_google_sheets


REQUIRED_COLUMNS = ("email", "senha", "nome", "perfil")


def _users_xlsx_path() -> Path:
    return Path(current_app.config["USERS_XLSX_PATH"]).expanduser().resolve()


def _normalize_dataframe(frame: pd.DataFrame) -> pd.DataFrame:
    normalized = frame.copy()
    normalized.columns = [str(column).strip().lower() for column in normalized.columns]
    missing_columns = [column for column in REQUIRED_COLUMNS if column not in normalized.columns]
    if missing_columns:
        missing = ", ".join(missing_columns)
        raise ValueError(f"Planilha de usuários inválida. Colunas ausentes: {missing}.")

    return normalized[list(REQUIRED_COLUMNS)].fillna("")


@lru_cache(maxsize=1)
def load_users_from_excel() -> tuple[User, ...]:
    path = _users_xlsx_path()
    if not path.exists():
        raise FileNotFoundError(
            f"Planilha de usuários não encontrada em: {path}. Configure USERS_XLSX_PATH corretamente."
        )

    frame = pd.read_excel(path)
    rows = _normalize_dataframe(frame)

    users = []
    for record in rows.to_dict(orient="records"):
        email = str(record["email"]).strip().lower()
        password = str(record["senha"])
        name = str(record["nome"])
        perfil = str(record["perfil"])
        if not email or not password:
            continue
        users.append(User(email=email, password=password, name=name, perfil=perfil))

    return tuple(users)


def load_users() -> tuple[User, ...]:
    if current_app.config.get("GOOGLE_SHEETS_ENABLED", False):
        try:
            google_users = load_users_from_google_sheets()
            if google_users:
                return google_users
        except Exception as exc:
            current_app.logger.warning("Google Sheets users load failed, falling back to Excel: %s", exc)

    return load_users_from_excel()


def get_user_by_email(email: str) -> User | None:
    normalized_email = email.strip().lower()
    return next((user for user in load_users() if user.email == normalized_email), None)


def get_user_by_id(user_id: str) -> User | None:
    return next((user for user in load_users() if user.id == user_id), None)


def authenticate_user(email: str, password: str) -> User | None:
    user = get_user_by_email(email)
    if user is None or not user.check_password(password):
        return None
    return user


def clear_user_cache() -> None:
    load_users_from_excel.cache_clear()
    load_users_from_google_sheets.cache_clear()