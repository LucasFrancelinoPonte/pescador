from __future__ import annotations

from flask_wtf import FlaskForm
from wtforms import BooleanField, DecimalField, IntegerField, SelectField, StringField, TextAreaField
from wtforms.validators import DataRequired, Length, NumberRange, Optional


class SocioeconomicForm(FlaskForm):
    nome = StringField("Nome completo", validators=[DataRequired(), Length(min=3, max=150)])
    cpf = StringField("CPF", validators=[DataRequired(), Length(min=11, max=14)])
    sexo = SelectField(
        "Sexo",
        choices=[
            ("", "Selecione"),
            ("feminino", "Feminino"),
            ("masculino", "Masculino"),
            ("outro", "Outro"),
        ],
        validators=[DataRequired()],
    )
    data_nascimento = StringField("Data de nascimento", validators=[DataRequired(), Length(max=10)])
    telefone = StringField("Telefone", validators=[DataRequired(), Length(min=8, max=20)])
    municipio = StringField("Município", validators=[DataRequired(), Length(min=2, max=120)])
    comunidade = StringField("Comunidade", validators=[DataRequired(), Length(min=2, max=120)])
    localidade = StringField("Localidade", validators=[DataRequired(), Length(min=2, max=120)])
    renda_mensal = DecimalField("Renda mensal (R$)", places=2, validators=[Optional(), NumberRange(min=0)])

    atividade_principal = SelectField(
        "Atividade principal",
        choices=[
            ("pesca_artesanal", "Pesca artesanal"),
            ("pesca_marinha", "Pesca marinha"),
            ("pesca_agua_doce", "Pesca em água doce"),
            ("marisqueira", "Mariscagem"),
            ("outro", "Outro"),
        ],
        validators=[DataRequired()],
    )
    local_pesca = StringField("Local de pesca", validators=[DataRequired(), Length(min=2, max=150)])
    especie_principal = StringField("Espécie principal", validators=[DataRequired(), Length(min=2, max=150)])
    tripulantes = IntegerField("Quantidade de tripulantes", validators=[DataRequired(), NumberRange(min=0, max=50)])
    dias_pesca_mes = IntegerField("Dias de pesca por mês", validators=[DataRequired(), NumberRange(min=0, max=31)])

    combustivel = DecimalField("Gasto com combustível (R$)", places=2, validators=[DataRequired(), NumberRange(min=0)])
    gelo = DecimalField("Gasto com gelo (R$)", places=2, validators=[DataRequired(), NumberRange(min=0)])
    iscas = DecimalField("Gasto com iscas (R$)", places=2, validators=[DataRequired(), NumberRange(min=0)])
    manutencao = DecimalField("Manutenção (R$)", places=2, validators=[DataRequired(), NumberRange(min=0)])
    outras_despesas = DecimalField("Outras despesas (R$)", places=2, validators=[Optional(), NumberRange(min=0)])

    embarcacao_possui = BooleanField("Possui embarcação")
    nome_embarcacao = StringField("Nome da embarcação", validators=[Optional(), Length(max=150)])
    tipo_embarcacao = SelectField(
        "Tipo de embarcação",
        choices=[
            ("canoa", "Canoa"),
            ("barco", "Barco"),
            ("jangada", "Jangada"),
            ("voadeira", "Voadeira"),
            ("outro", "Outro"),
        ],
        validators=[Optional()],
    )
    comprimento = DecimalField("Comprimento (m)", places=2, validators=[Optional(), NumberRange(min=0)])
    motor_hp = IntegerField("Potência do motor (HP)", validators=[Optional(), NumberRange(min=0)])
    matricula = StringField("Matrícula/registro", validators=[Optional(), Length(max=60)])
    tipo_combustivel = SelectField(
        "Tipo de combustível",
        choices=[
            ("gasolina", "Gasolina"),
            ("diesel", "Diesel"),
            ("etanol", "Etanol"),
            ("outro", "Outro"),
        ],
        validators=[Optional()],
    )

    observacoes = TextAreaField("Observações", validators=[Optional(), Length(max=2000)])