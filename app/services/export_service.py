from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from tempfile import NamedTemporaryFile

import pandas as pd
from flask import current_app
from sqlalchemy import and_, select

from ..extensions import db
from ..repositories import SocioeconomicSubmissionRepository
from ..models import SocioeconomicSubmission
from .sheet_service import sync_dataframe_to_sheet


@dataclass(slots=True)
class ExportFilters:
    municipio: str = ""
    localidade: str = ""
    sexo: str = ""
    data_inicio: str = ""
    data_fim: str = ""


@dataclass(slots=True)
class ExportResult:
    filename: str
    file_path: Path | None
    records_count: int = 0
    errors: list[str] | None = None


EXPORT_COLUMN_MAP = {
    "created_at": "Data de cadastro",
    "created_by_name": "Usuário",
    "created_by_email": "E-mail do usuário",
    "nome": "Nome",
    "cpf": "CPF",
    "sexo": "Sexo",
    "data_nascimento": "Data de nascimento",
    "telefone": "Telefone",
    "municipio": "Município",
    "comunidade": "Comunidade",
    "localidade": "Localidade",
    "atividade_principal": "Atividade principal",
    "local_pesca": "Local de pesca",
    "especie_principal": "Espécie principal",
    "tripulantes": "Tripulantes",
    "dias_pesca_mes": "Dias de pesca/mês",
    "combustivel": "Combustível (R$)",
    "gelo": "Gelo (R$)",
    "iscas": "Iscas (R$)",
    "manutencao": "Manutenção (R$)",
    "outras_despesas": "Outras despesas (R$)",
    "embarcacao_possui": "Possui embarcação",
    "nome_embarcacao": "Nome da embarcação",
    "tipo_embarcacao": "Tipo de embarcação",
    "comprimento": "Comprimento (m)",
    "motor_hp": "Motor (HP)",
    "matricula": "Matrícula",
    "tipo_combustivel": "Tipo de combustível",
    "observacoes": "Observações",
}


def parse_filters(data: dict[str, str]) -> ExportFilters:
    return ExportFilters(
        municipio=data.get("municipio", "").strip(),
        localidade=data.get("localidade", "").strip(),
        sexo=data.get("sexo", "").strip(),
        data_inicio=data.get("data_inicio", "").strip(),
        data_fim=data.get("data_fim", "").strip(),
    )


def _build_conditions(filters: ExportFilters):
    conditions = []
    if filters.municipio:
        conditions.append(SocioeconomicSubmission.municipio.ilike(f"%{filters.municipio}%"))
    if filters.localidade:
        conditions.append(SocioeconomicSubmission.localidade.ilike(f"%{filters.localidade}%"))
    if filters.sexo and filters.sexo != "todos":
        conditions.append(SocioeconomicSubmission.sexo == filters.sexo)
    if filters.data_inicio:
        conditions.append(SocioeconomicSubmission.created_at >= datetime.fromisoformat(filters.data_inicio))
    if filters.data_fim:
        conditions.append(SocioeconomicSubmission.created_at <= datetime.fromisoformat(filters.data_fim))
    return conditions


def _base_query(filters: ExportFilters):
    query = select(
        SocioeconomicSubmission.created_at,
        SocioeconomicSubmission.created_by_name,
        SocioeconomicSubmission.created_by_email,
        SocioeconomicSubmission.nome,
        SocioeconomicSubmission.cpf,
        SocioeconomicSubmission.sexo,
        SocioeconomicSubmission.data_nascimento,
        SocioeconomicSubmission.telefone,
        SocioeconomicSubmission.municipio,
        SocioeconomicSubmission.comunidade,
        SocioeconomicSubmission.localidade,
        SocioeconomicSubmission.atividade_principal,
        SocioeconomicSubmission.local_pesca,
        SocioeconomicSubmission.especie_principal,
        SocioeconomicSubmission.tripulantes,
        SocioeconomicSubmission.dias_pesca_mes,
        SocioeconomicSubmission.combustivel,
        SocioeconomicSubmission.gelo,
        SocioeconomicSubmission.iscas,
        SocioeconomicSubmission.manutencao,
        SocioeconomicSubmission.outras_despesas,
        SocioeconomicSubmission.embarcacao_possui,
        SocioeconomicSubmission.nome_embarcacao,
        SocioeconomicSubmission.tipo_embarcacao,
        SocioeconomicSubmission.comprimento,
        SocioeconomicSubmission.motor_hp,
        SocioeconomicSubmission.matricula,
        SocioeconomicSubmission.tipo_combustivel,
        SocioeconomicSubmission.observacoes,
    ).order_by(SocioeconomicSubmission.created_at.desc())

    conditions = _build_conditions(filters)
    if conditions:
        query = query.where(and_(*conditions))
    return query


def load_export_frame(filters: ExportFilters) -> pd.DataFrame:
    query = _base_query(filters)
    with db.engine.connect() as connection:
        frame = pd.read_sql_query(query, connection)

    if not frame.empty:
        frame = frame.rename(columns=EXPORT_COLUMN_MAP)
    return frame


def build_filename() -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"export_formularios_{timestamp}.xlsx"


def export_to_excel(frame: pd.DataFrame) -> Path:
    temp_file = NamedTemporaryFile(delete=False, suffix=".xlsx")
    temp_path = Path(temp_file.name)
    temp_file.close()
    frame.to_excel(temp_path, index=False, engine="openpyxl")
    return temp_path


def export_submissions(filters: ExportFilters) -> ExportResult:
    filename = build_filename()
    frame = load_export_frame(filters)

    if frame.empty:
        return ExportResult(
            filename=filename,
            file_path=None,
            records_count=0,
            errors=["Nenhum registro encontrado para os filtros informados."],
        )

    file_path = export_to_excel(frame)
    sync_dataframe_to_sheet(frame)
    return ExportResult(
        filename=filename,
        file_path=file_path,
        records_count=len(frame),
        errors=[],
    )