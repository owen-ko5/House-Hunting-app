import logging
import os
import sys

from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from werkzeug.exceptions import HTTPException

from config import Config

db      = SQLAlchemy()
migrate = Migrate()
jwt     = JWTManager()
limiter = Limiter(key_func=get_remote_address, default_limits=["200 per hour"])


def _init_sentry(app):
    """Optional error tracking — only runs if SENTRY_DSN is set."""
    dsn = app.config.get("SENTRY_DSN")
    if not dsn:
        return
    try:
        import sentry_sdk
        from sentry_sdk.integrations.flask import FlaskIntegration
        sentry_sdk.init(dsn=dsn, integrations=[FlaskIntegration()], traces_sample_rate=0.1)
    except ImportError:
        app.logger.warning("SENTRY_DSN set but sentry-sdk is not installed.")


def _init_logging(app):
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(
        "%(asctime)s %(levelname)s [%(name)s] %(message)s"
    ))
    app.logger.handlers = [handler]
    app.logger.setLevel(app.config.get("LOG_LEVEL", "INFO"))


def _register_error_handlers(app):
    @app.errorhandler(HTTPException)
    def handle_http_exception(err):
        response = {"error": err.description or err.name}
        return jsonify(response), err.code

    @app.errorhandler(Exception)
    def handle_unexpected_exception(err):
        # Never leak internals to the client; log the real thing server-side.
        app.logger.exception("Unhandled exception")
        return jsonify({"error": "Internal server error."}), 500


def _register_security_headers(app):
    @app.after_request
    def set_security_headers(response):
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        if app.config.get("ENV") == "production":
            response.headers.setdefault(
                "Strict-Transport-Security", "max-age=63072000; includeSubDomains"
            )
        return response


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    _init_logging(app)
    _init_sentry(app)

    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3001")
    CORS(app, origins=[
        "http://localhost:3001",
        "http://localhost:3000",
        frontend_url,
    ], supports_credentials=True)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    limiter.init_app(app)

    _register_error_handlers(app)
    _register_security_headers(app)

    from . import models  # noqa: F401
    from .routes import api_bp
    app.register_blueprint(api_bp, url_prefix="/api")

    return app
