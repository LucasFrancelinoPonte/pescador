from __future__ import annotations

from flask import Blueprint, render_template

from ..utils.auth import login_required


export_bp = Blueprint("export_bp", __name__)


@export_bp.route("/export", methods=["GET", "POST"])
@login_required
def export_data():
    # Exportação desativada temporariamente para manter o foco no formulário principal.
    return render_template(
        "shared/disabled.html",
        title="Exportação",
        message="A exportação de Excel foi ocultada nesta fase e será reativada depois.",
    )