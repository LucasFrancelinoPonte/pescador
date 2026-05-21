from __future__ import annotations

from flask import render_template


def register_error_handlers(app) -> None:
    @app.errorhandler(400)
    def bad_request(error):
        app.logger.warning("400 Bad Request: %s", error)
        return render_template("errors/error.html", title="Solicitação inválida", message="A solicitação não pôde ser processada."), 400

    @app.errorhandler(403)
    def forbidden(error):
        app.logger.warning("403 Forbidden: %s", error)
        return render_template("errors/error.html", title="Acesso negado", message="Você não tem permissão para acessar este recurso."), 403

    @app.errorhandler(404)
    def not_found(error):
        app.logger.info("404 Not Found: %s", error)
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.exception("500 Internal Server Error")
        return render_template("errors/500.html"), 500