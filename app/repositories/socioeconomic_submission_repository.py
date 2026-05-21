from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import func, select

from ..extensions import db
from ..models import SocioeconomicSubmission


@dataclass(slots=True)
class PaginationResult:
    items: list[SocioeconomicSubmission]
    page: int
    per_page: int
    total: int

    @property
    def pages(self) -> int:
        if self.per_page <= 0:
            return 0
        return (self.total + self.per_page - 1) // self.per_page


class SocioeconomicSubmissionRepository:
    @staticmethod
    def count_total() -> int:
        return db.session.query(func.count(SocioeconomicSubmission.id)).scalar() or 0

    @staticmethod
    def average_income() -> float:
        return float(db.session.query(func.avg(SocioeconomicSubmission.renda_mensal)).scalar() or 0)

    @staticmethod
    def grouped_count(column_name: str) -> list[tuple[str, int]]:
        column = getattr(SocioeconomicSubmission, column_name)
        rows = (
            db.session.query(column, func.count(SocioeconomicSubmission.id))
            .group_by(column)
            .order_by(func.count(SocioeconomicSubmission.id).desc())
            .all()
        )
        return [(str(label or ""), int(count or 0)) for label, count in rows]

    @staticmethod
    def recent(page: int = 1, per_page: int = 10) -> PaginationResult:
        statement = select(SocioeconomicSubmission).order_by(SocioeconomicSubmission.created_at.desc())
        pagination = db.paginate(statement, page=page, per_page=per_page, error_out=False)
        return PaginationResult(
            items=list(pagination.items),
            page=pagination.page,
            per_page=pagination.per_page,
            total=pagination.total,
        )

    @staticmethod
    def create(submission: SocioeconomicSubmission) -> SocioeconomicSubmission:
        db.session.add(submission)
        db.session.commit()
        return submission

    @staticmethod
    def list_for_export() -> list[SocioeconomicSubmission]:
        return db.session.execute(
            select(SocioeconomicSubmission).order_by(SocioeconomicSubmission.created_at.desc())
        ).scalars().all()