from __future__ import annotations

from flask import Blueprint, render_template

from ..utils.auth import login_required


form_bp = Blueprint("form_bp", __name__)


@form_bp.route("/form/new", methods=["GET"])
@login_required
def new_form():
    # Validação real será implementada futuramente no backend.
    # Persistência, auditoria e integração com SQLAlchemy entram em uma etapa posterior.
    return render_template("form/form.html")