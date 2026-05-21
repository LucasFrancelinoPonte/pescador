from __future__ import annotations

import json
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd
from flask import current_app
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from ..extensions import db
from ..models import ImportedForm


ALLOWED_EXTENSIONS = {"xlsx"}


@dataclass(slots=True)
class ImportResult:
    imported_count: int = 0
    errors: list[str] = field(default_factory=list)
    filename: str | None = None


def is_allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def save_temporary_upload(upload: FileStorage) -> Path:
    temp_handle = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
    temp_handle.close()

    safe_name = secure_filename(upload.filename or "uploaded.xlsx")
    upload.save(temp_handle.name)

    return Path(temp_handle.name)


def _required_columns() -> tuple[str, ...]:
    return tuple(current_app.config.get("IMPORT_REQUIRED_COLUMNS", ()))


def _normalize_columns(frame: pd.DataFrame) -> pd.DataFrame:
    normalized = frame.copy()
    normalized.columns = [str(column).strip().lower() for column in normalized.columns]
    return normalized


def _missing_columns(columns: pd.Index | list[str] | tuple[str, ...]) -> list[str]:
    normalized_columns = {str(column).strip().lower() for column in columns}
    return [column for column in _required_columns() if column not in normalized_columns]


def import_spreadsheet(upload: FileStorage) -> ImportResult:
    result = ImportResult()

    if not upload or not upload.filename:
        result.errors.append("Nenhum arquivo foi enviado.")
        return result

    if not is_allowed_file(upload.filename):
        result.errors.append("Envie apenas arquivos .xlsx.")
        return result

    temp_path = save_temporary_upload(upload)
    result.filename = secure_filename(upload.filename)

    try:
        frame = pd.read_excel(temp_path)
        if frame.empty:
            result.errors.append("A planilha enviada está vazia.")
            return result

        normalized = _normalize_columns(frame)
        missing_columns = _missing_columns(normalized.columns)
        if missing_columns:
            formatted = ", ".join(missing_columns)
            result.errors.append(f"Colunas obrigatórias ausentes: {formatted}.")
            return result

        records_to_save: list[ImportedForm] = []
        for index, row in normalized.iterrows():
            row_number = index + 2
            row_data = row.where(pd.notna(row), "").to_dict()
            row_data = {key: str(value).strip() for key, value in row_data.items()}

            missing_values = [column for column in _required_columns() if not row_data.get(column)]
            if missing_values:
                result.errors.append(
                    f"Linha {row_number}: campos obrigatórios vazios: {', '.join(missing_values)}."
                )
                continue

            records_to_save.append(
                ImportedForm(
                    source_filename=result.filename,
                    row_number=row_number,
                    data_json=json.dumps(row_data, ensure_ascii=False),
                )
            )

        if records_to_save:
            db.session.add_all(records_to_save)
            db.session.commit()

        result.imported_count = len(records_to_save)
        return result
    except Exception as exc:
        db.session.rollback()
        result.errors.append(f"Falha ao processar a planilha: {exc}")
        return result
    finally:
        temp_path.unlink(missing_ok=True)