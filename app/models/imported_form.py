from __future__ import annotations

from datetime import datetime

from ..extensions import db


class ImportedForm(db.Model):
    __tablename__ = "imported_forms"

    id = db.Column(db.Integer, primary_key=True)
    source_filename = db.Column(db.String(255), nullable=False)
    row_number = db.Column(db.Integer, nullable=False)
    data_json = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"ImportedForm(id={self.id!r}, row_number={self.row_number!r})"