from __future__ import annotations

import random
from decimal import Decimal
from pathlib import Path
from typing import Any

import pandas as pd
from flask import current_app

from ..extensions import db
from ..models.socioeconomic_submission import SocioeconomicSubmission


def _ensure_mock_dir() -> Path:
    mock_dir = Path(current_app.config.get("MOCK_DATA_DIR"))
    mock_dir.mkdir(parents=True, exist_ok=True)
    return mock_dir


def _generate_users_xlsx(path: Path) -> None:
    # Mocked users for demo; DO NOT use in production
    records = [
        {"nome": "Administrador", "email": "admin@example.com", "senha": "admin123", "perfil": "admin"},
        {"nome": "Digitador Demo", "email": "digitador@example.com", "senha": "dig123", "perfil": "digitador"},
        {"nome": "Pesquisador Demo", "email": "pesquisador@example.com", "senha": "pesq123", "perfil": "pesquisador"},
    ]
    df = pd.DataFrame(records)
    df.to_excel(path, index=False, engine="openpyxl")


def _random_cpf() -> str:
    a = random.randint(100, 999)
    b = random.randint(100, 999)
    c = random.randint(100, 999)
    d = random.randint(10, 99)
    return f"{a:03d}.{b:03d}.{c:03d}-{d:02d}"


def _generate_fishermen_xlsx(path: Path, count: int = 30) -> None:
    # Lightweight lists to create varied Brazilian names and data (Paraíba municipalities)
    first_names = [
        "João", "Maria", "José", "Antônio", "Francisco", "Carlos", "Paulo", "Lucas", "Luiz", "Mariana",
        "Patrícia", "Fernanda", "Raimundo", "Ricardo", "Silvana", "Sérgio", "Ana", "Beatriz", "Roberto", "Cícero",
    ]
    last_names = ["Silva", "Santos", "Fernandes", "Oliveira", "Souza", "Pereira", "Lima", "Rodrigues", "Almeida", "Costa"]
    municipios = [
        "João Pessoa", "Campina Grande", "Bayeux", "Cabedelo", "Patos", "Sousa", "Guarabira", "Mamanguape",
        "Cajazeiras", "Areia", "Solânea", "Itabaiana", "Cuité", "Pombal", "Conde",
    ]
    categorias = ["Artesanal", "Industrial", "Recreativa", "Pequena Escala"]
    especies = ["Camarão", "Tambaqui", "Peixe-Boi", "Pescada", "Atum", "Robalo", "Sardinha", "Polvo"]
    embarcacoes = ["Canoa", "Barco de madeira", "Embarcação de alumínio", "Rede de arrasto", "Sem embarcação"]
    combustiveis = [Decimal("50.00"), Decimal("120.50"), Decimal("300.00"), Decimal("0.00")]

    records: list[dict[str, Any]] = []
    for i in range(count):
        nome = f"{random.choice(first_names)} {random.choice(last_names)}"
        cpf = _random_cpf()
        municipio = random.choice(municipios)
        atividade = random.choice(categorias)
        especie = random.choice(especies)
        embarcacao_possui = random.choice([True, False])
        nome_emb = random.choice(embarcacoes) if embarcacao_possui else ""
        renda = round(random.uniform(200.0, 3500.0), 2)
        combustivel = random.choice(combustiveis)

        record = {
            "created_by_email": "admin@example.com",
            "created_by_name": "Administrador",
            "nome": nome,
            "cpf": cpf,
            "data_nascimento": f"{random.randint(1,28):02d}/{random.randint(1,12):02d}/{random.randint(1950,1998)}",
            "telefone": f"(83) 9{random.randint(8000,9999)}-{random.randint(1000,9999)}",
            "municipio": municipio,
            "comunidade": f"Comunidade {random.choice(['A', 'B', 'C', 'D'])}",
            "localidade": f"Localidade {random.randint(1,15)}",
            "sexo": random.choice(["Masculino", "Feminino"]),
            "renda_mensal": renda,
            "atividade_principal": atividade,
            "local_pesca": f"Zona {random.choice(['Litorânea', 'Estuarina', 'Costeria', 'Ribeirinha'])}",
            "especie_principal": especie,
            "tripulantes": random.randint(0, 4),
            "dias_pesca_mes": random.randint(2, 20),
            "combustivel": float(combustivel),
            "gelo": round(random.uniform(0, 100), 2),
            "iscas": round(random.uniform(0, 80), 2),
            "manutencao": round(random.uniform(0, 200), 2),
            "outras_despesas": round(random.uniform(0, 150), 2),
            "embarcacao_possui": embarcacao_possui,
            "nome_embarcacao": nome_emb if embarcacao_possui else "",
            "tipo_embarcacao": random.choice(["Fibra", "Madeira", "Alumínio"]) if embarcacao_possui else "",
            "comprimento": round(random.uniform(2.5, 12.0), 2) if embarcacao_possui else None,
            "motor_hp": random.choice([15, 25, 40, 60, None]) if embarcacao_possui else None,
            "matricula": f"PB-{random.randint(1000,9999)}" if embarcacao_possui else "",
            "tipo_combustivel": random.choice(["Diesel", "Gasolina", "Álcool"]) if embarcacao_possui else "",
            "observacoes": "Registro gerado automaticamente (mock).",
        }
        records.append(record)

    df = pd.DataFrame(records)
    df.to_excel(path, index=False, engine="openpyxl")


def seed_database_from_xlsx(fishermen_path: Path) -> dict[str, int]:
    frame = pd.read_excel(fishermen_path)
    created = 0
    skipped = 0
    for record in frame.to_dict(orient="records"):
        cpf = str(record.get("cpf", "")).strip()
        if not cpf:
            continue
        exists = db.session.query(SocioeconomicSubmission).filter_by(cpf=cpf).first()
        if exists:
            skipped += 1
            continue

        submission = SocioeconomicSubmission(
            created_by_email=record.get("created_by_email", "admin@example.com"),
            created_by_name=record.get("created_by_name", "Administrador"),
            nome=record.get("nome", ""),
            cpf=cpf,
            data_nascimento=record.get("data_nascimento", ""),
            telefone=record.get("telefone", ""),
            municipio=record.get("municipio", ""),
            comunidade=record.get("comunidade", ""),
            localidade=record.get("localidade", ""),
            sexo=record.get("sexo", ""),
            renda_mensal=record.get("renda_mensal"),
            atividade_principal=record.get("atividade_principal", ""),
            local_pesca=record.get("local_pesca", ""),
            especie_principal=record.get("especie_principal", ""),
            tripulantes=int(record.get("tripulantes") or 0),
            dias_pesca_mes=int(record.get("dias_pesca_mes") or 0),
            combustivel=record.get("combustivel") or 0,
            gelo=record.get("gelo") or 0,
            iscas=record.get("iscas") or 0,
            manutencao=record.get("manutencao") or 0,
            outras_despesas=record.get("outras_despesas") or 0,
            embarcacao_possui=bool(record.get("embarcacao_possui")),
            nome_embarcacao=record.get("nome_embarcacao"),
            tipo_embarcacao=record.get("tipo_embarcacao"),
            comprimento=record.get("comprimento"),
            motor_hp=record.get("motor_hp"),
            matricula=record.get("matricula"),
            tipo_combustivel=record.get("tipo_combustivel"),
            observacoes=record.get("observacoes"),
        )
        db.session.add(submission)
        created += 1

    db.session.commit()
    return {"created": created, "skipped": skipped}


def ensure_seed_data(app) -> None:
    """Create mock files and populate the SQLite DB. Idempotent: will not duplicate by CPF."""
    with app.app_context():
        mock_dir = _ensure_mock_dir()
        users_xlsx = mock_dir / "users.xlsx"
        fishermen_xlsx = mock_dir / "fishermen_mock_data.xlsx"

        if not users_xlsx.exists():
            _generate_users_xlsx(users_xlsx)
            current_app.logger.info("Created mock users: %s", users_xlsx)

        if not fishermen_xlsx.exists():
            _generate_fishermen_xlsx(fishermen_xlsx, count=30)
            current_app.logger.info("Created mock fishermen data: %s", fishermen_xlsx)

        # Ensure database tables exist
        db.create_all()

        result = seed_database_from_xlsx(fishermen_xlsx)
        current_app.logger.info("Seeded database: created=%s skipped=%s", result.get("created"), result.get("skipped"))
