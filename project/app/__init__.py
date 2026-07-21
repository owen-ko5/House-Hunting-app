import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from config import Config

db      = SQLAlchemy()
migrate = Migrate()
jwt     = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3001")
    CORS(app, origins=[
        "http://localhost:3001",
        "http://localhost:3000",
        frontend_url,
    ], supports_credentials=True)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    from . import models  # noqa: F401

    from .routes import api_bp
    app.register_blueprint(api_bp, url_prefix="/api")

    return app
