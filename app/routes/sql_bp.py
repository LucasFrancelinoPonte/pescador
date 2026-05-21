from __future__ import annotations

from flask import Blueprint, render_template

from ..utils.auth import login_required


sql_bp = Blueprint("sql_bp", __name__)


@sql_bp.route("/sql-console", methods=["GET", "POST"])
@login_required
def sql_console():
    # Console SQL desativado temporariamente para reduzir distrações na validação do MVP.
    return render_template(
        "shared/disabled.html",
        title="SQL Console",
        message="A consulta SQL foi ocultada nesta fase e será reativada depois.",
    )