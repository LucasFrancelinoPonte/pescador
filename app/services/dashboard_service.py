from __future__ import annotations

from dataclasses import dataclass

from flask import current_app

from ..repositories import PaginationResult, SocioeconomicSubmissionRepository


@dataclass(slots=True)
class DashboardData:
    total_forms: int
    average_income: float
    by_municipio: list[dict[str, object]]
    by_pesca_category: list[dict[str, object]]
    by_sexo: list[dict[str, object]]
    recent_submissions: PaginationResult


def get_dashboard_data(page: int = 1) -> DashboardData:
    per_page = int(current_app.config.get("DASHBOARD_PAGE_SIZE", 8))
    total_forms = SocioeconomicSubmissionRepository.count_total()
    average_income = SocioeconomicSubmissionRepository.average_income()

    by_municipio = [
        {"label": municipio or "Sem município", "value": count}
        for municipio, count in SocioeconomicSubmissionRepository.grouped_count("municipio")
    ]

    by_pesca_category = [
        {"label": categoria or "Sem categoria", "value": count}
        for categoria, count in SocioeconomicSubmissionRepository.grouped_count("atividade_principal")
    ]

    by_sexo = [
        {"label": sexo or "Não informado", "value": count}
        for sexo, count in SocioeconomicSubmissionRepository.grouped_count("sexo")
    ]

    recent_submissions = SocioeconomicSubmissionRepository.recent(page=page, per_page=per_page)

    return DashboardData(
        total_forms=total_forms,
        average_income=average_income,
        by_municipio=by_municipio,
        by_pesca_category=by_pesca_category,
        by_sexo=by_sexo,
        recent_submissions=recent_submissions,
    )