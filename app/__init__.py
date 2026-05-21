from __future__ import annotations

from flask import Flask
from sqlalchemy import inspect, text

from config import Config

from .errors import register_error_handlers
from .extensions import csrf, db, login_manager
from .routes.auth import auth_bp
from .routes.dashboard_bp import dashboard_bp
from .routes.export_bp import export_bp
from .routes.form_bp import form_bp
from .routes.import_bp import import_bp
from .routes.sql_bp import sql_bp
from .routes.main import main_bp
from .services.auth_service import get_user_by_id
from .services.sheet_service import sync_startup_cache
from .utils.logging import configure_logging
from .utils.seed_data import ensure_seed_data


def create_app(config_class: type[Config] = Config) -> Flask:
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "warning"

    configure_logging(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(export_bp)
    app.register_blueprint(form_bp)
    app.register_blueprint(import_bp)
    app.register_blueprint(sql_bp)
    app.register_blueprint(main_bp)

    register_error_handlers(app)

    with app.app_context():
        if app.config.get("ENABLE_DATABASE", False):
            # Future database layer: keep this block for the eventual SQLAlchemy-backed MVP.
            db.create_all()
            _ensure_socioeconomic_columns()

            try:
                if app.config.get("SEED_ON_STARTUP", False):
                    ensure_seed_data(app)
            except Exception:
                # Seed data stays optional so the Vercel deploy can boot even without local writes.
                app.logger.exception("Seed data failed")

        if app.config.get("ENABLE_STARTUP_TASKS", False):
            # Future audit/export/import bootstrap hooks can live behind this flag.
            sync_startup_cache()

    return app


@login_manager.user_loader
def load_user(user_id: str):
    return get_user_by_id(user_id)


def _ensure_socioeconomic_columns() -> None:
    inspector = inspect(db.engine)
    if not inspector.has_table("socioeconomic_submissions"):
        return

    existing_columns = {column["name"] for column in inspector.get_columns("socioeconomic_submissions")}
    required_alterations = {
        "localidade": "ALTER TABLE socioeconomic_submissions ADD COLUMN localidade VARCHAR(120) NOT NULL DEFAULT ''",
        "sexo": "ALTER TABLE socioeconomic_submissions ADD COLUMN sexo VARCHAR(20) NOT NULL DEFAULT ''",
        "renda_mensal": "ALTER TABLE socioeconomic_submissions ADD COLUMN renda_mensal NUMERIC(10, 2)",
    }

    for column_name, ddl in required_alterations.items():
        if column_name not in existing_columns:
            db.session.execute(text(ddl))
    db.session.commit()