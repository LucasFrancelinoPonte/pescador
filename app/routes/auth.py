from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user

from ..services.auth_service import authenticate_user
from ..utils.auth import login_required
from ..utils.security import get_safe_redirect_target


auth_bp = Blueprint("auth", __name__, url_prefix="")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        remember = request.form.get("remember") == "on"
        next_page = request.form.get("next") or request.args.get("next")

        user = authenticate_user(email, password)
        if user:
            login_user(user, remember=remember)
            flash("Login realizado com sucesso.", "success")
            safe_target = get_safe_redirect_target(next_page)
            return redirect(safe_target or url_for("main.home"))

        flash("E-mail ou senha inválidos.", "danger")

    return render_template("auth/login.html")


@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    flash("Você saiu da sua sessão.", "info")
    return redirect(url_for("auth.login"))