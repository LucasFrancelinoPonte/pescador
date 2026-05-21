from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from tempfile import NamedTemporaryFile

import pandas as pd
from flask import current_app

from ..extensions import db


FORBIDDEN_PATTERNS = (
    r"\bdrop\b",
    r"\bdelete\b",
    r"\bupdate\b",
    r"\balter\b",
    r"\binsert\b",
)


@dataclass(slots=True)
class SQLConsoleResult:
    query: str
    dataframe: pd.DataFrame | None = None
    row_count: int = 0
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    filename: str | None = None
    file_path: Path | None = None


def _strip_sql_comments(query: str) -> str:
    without_block_comments = re.sub(r"/\*.*?\*/", " ", query, flags=re.S)
    without_line_comments = re.sub(r"--.*?$", " ", without_block_comments, flags=re.M)
    return without_line_comments.strip()


def validate_select_query(query: str) -> list[str]:
    cleaned = _strip_sql_comments(query)
    errors: list[str] = []

    if not cleaned:
        return ["Digite uma consulta SQL."]

    if ";" in cleaned.rstrip(";"):
        errors.append("Não são permitidas múltiplas instruções SQL.")

    if not re.match(r"^select\b", cleaned, flags=re.I):
        errors.append("Somente consultas SELECT são permitidas.")

    for pattern in FORBIDDEN_PATTERNS:
        if re.search(pattern, cleaned, flags=re.I):
            errors.append("A consulta contém comandos bloqueados (DROP, DELETE, UPDATE, ALTER ou INSERT).")
            break

    return errors


def execute_sql_query(query: str) -> SQLConsoleResult:
    validation_errors = validate_select_query(query)
    result = SQLConsoleResult(query=query)
    if validation_errors:
        result.errors.extend(validation_errors)
        return result

    try:
        with db.engine.connect() as connection:
            frame = pd.read_sql_query(query, connection)

        result.dataframe = frame
        result.row_count = len(frame)
        result.warnings.append(f"{result.row_count} linha(s) retornada(s).")
        return result
    except Exception as exc:
        result.errors.append(f"Falha ao executar a consulta: {exc}")
        return result


def dataframe_to_excel(frame: pd.DataFrame) -> Path:
    temp_file = NamedTemporaryFile(delete=False, suffix=".xlsx")
    temp_path = Path(temp_file.name)
    temp_file.close()
    frame.to_excel(temp_path, index=False, engine="openpyxl")
    return temp_path


def export_query_result(frame: pd.DataFrame) -> tuple[str, Path]:
    timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
    filename = f"sql_console_{timestamp}.xlsx"
    return filename, dataframe_to_excel(frame)


def get_examples() -> list[str]:
    table = current_app.config.get("SQL_CONSOLE_TABLE_NAME", "socioeconomic_submissions")
    return [
        f"SELECT * FROM {table} LIMIT 20",
        f"SELECT municipio, COUNT(*) AS total FROM {table} GROUP BY municipio ORDER BY total DESC",
        f"SELECT sexo, AVG(COALESCE(combustivel, 0)) AS media_combustivel FROM {table} GROUP BY sexo",
        f"SELECT municipio, AVG(COALESCE(renda_mensal, 0)) AS renda_media FROM {table} GROUP BY municipio ORDER BY renda_media DESC LIMIT 20",
        f"SELECT atividade_principal, COUNT(*) AS total_por_atividade FROM {table} GROUP BY atividade_principal ORDER BY total_por_atividade DESC",
        f"SELECT especie_principal, AVG(COALESCE(dias_pesca_mes,0)) AS media_dias_pesca FROM {table} GROUP BY especie_principal ORDER BY media_dias_pesca DESC",
        f"SELECT localidade, COUNT(*) AS total FROM {table} GROUP BY localidade ORDER BY total DESC LIMIT 10",
        f"SELECT created_at, nome, cpf, municipio FROM {table} ORDER BY created_at DESC LIMIT 50",
    ]