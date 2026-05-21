from __future__ import annotations

from flask import Blueprint, render_template

from ..utils.auth import login_required


dashboard_bp = Blueprint("dashboard_bp", __name__)


@dashboard_bp.route("/dashboard")
@login_required
def dashboard():
    # Módulo desativado temporariamente durante a validação visual do MVP.
    return render_template(
        "shared/disabled.html",
        title="Dashboard",
        message="O dashboard foi ocultado nesta fase e será reativado depois da validação do formulário principal.",
    )