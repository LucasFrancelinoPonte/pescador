from __future__ import annotations

from functools import wraps

from flask import flash, redirect, request, url_for
from flask_login import current_user


def login_required(view_function):
    @wraps(view_function)
    def wrapped_view(*args, **kwargs):
        if current_user.is_authenticated:
            return view_function(*args, **kwargs)

        flash("Você precisa entrar para acessar esta página.", "warning")
        return redirect(url_for("auth.login", next=request.url))

    return wrapped_view