from __future__ import annotations

from flask import Blueprint, render_template

from ..utils.auth import login_required


import_bp = Blueprint("import_bp", __name__)


@import_bp.route("/importar-planilha", methods=["GET", "POST"])
@login_required
def upload():
    # Importação desativada temporariamente para manter o MVP concentrado no formulário.
    return render_template(
        "shared/disabled.html",
        title="Importação",
        message="A importação de Excel foi ocultada nesta fase e será reativada depois.",
    )