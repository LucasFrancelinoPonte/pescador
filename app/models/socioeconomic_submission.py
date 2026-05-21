from __future__ import annotations

from datetime import datetime

from ..extensions import db


class SocioeconomicSubmission(db.Model):
    __tablename__ = "socioeconomic_submissions"

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    created_by_email = db.Column(db.String(180), nullable=False)
    created_by_name = db.Column(db.String(120), nullable=False)

    nome = db.Column(db.String(150), nullable=False)
    cpf = db.Column(db.String(14), nullable=False, index=True)
    data_nascimento = db.Column(db.String(10), nullable=False)
    telefone = db.Column(db.String(20), nullable=False)
    municipio = db.Column(db.String(120), nullable=False)
    comunidade = db.Column(db.String(120), nullable=False)
    localidade = db.Column(db.String(120), nullable=False, default="")
    sexo = db.Column(db.String(20), nullable=False, default="")
    renda_mensal = db.Column(db.Numeric(10, 2), nullable=True)

    atividade_principal = db.Column(db.String(50), nullable=False)
    local_pesca = db.Column(db.String(150), nullable=False)
    especie_principal = db.Column(db.String(150), nullable=False)
    tripulantes = db.Column(db.Integer, nullable=False)
    dias_pesca_mes = db.Column(db.Integer, nullable=False)

    combustivel = db.Column(db.Numeric(10, 2), nullable=False)
    gelo = db.Column(db.Numeric(10, 2), nullable=False)
    iscas = db.Column(db.Numeric(10, 2), nullable=False)
    manutencao = db.Column(db.Numeric(10, 2), nullable=False)
    outras_despesas = db.Column(db.Numeric(10, 2), nullable=True)

    embarcacao_possui = db.Column(db.Boolean, default=False, nullable=False)
    nome_embarcacao = db.Column(db.String(150), nullable=True)
    tipo_embarcacao = db.Column(db.String(50), nullable=True)
    comprimento = db.Column(db.Numeric(10, 2), nullable=True)
    motor_hp = db.Column(db.Integer, nullable=True)
    matricula = db.Column(db.String(60), nullable=True)
    tipo_combustivel = db.Column(db.String(50), nullable=True)

    observacoes = db.Column(db.Text, nullable=True)

    def __repr__(self) -> str:
        return f"SocioeconomicSubmission(id={self.id!r}, cpf={self.cpf!r})"