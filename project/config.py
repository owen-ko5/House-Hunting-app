import os


class Config:
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Fix Render's old postgres:// scheme that SQLAlchemy 2.x rejects
    if SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace(
            "postgres://", "postgresql://", 1
        )

    # JWT — must be set in Render environment variables
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    if not JWT_SECRET_KEY:
        raise RuntimeError(
            "JWT_SECRET_KEY is not set. "
            "Add it in Render -> your service -> Environment."
        )

    JWT_ACCESS_TOKEN_EXPIRES  = 60 * 60            # 1 hour
    JWT_REFRESH_TOKEN_EXPIRES = 60 * 60 * 24 * 30  # 30 days

    # Observability / ops
    SENTRY_DSN = os.getenv("SENTRY_DSN")            # optional; error tracking is skipped if unset
    LOG_LEVEL  = os.getenv("LOG_LEVEL", "INFO")
    ENV        = os.getenv("FLASK_ENV", "production")

    # Rate limiting backend (use Redis in production via RATELIMIT_STORAGE_URI;
    # falls back to in-memory, which is fine for a single dyno/instance only)
    RATELIMIT_STORAGE_URI = os.getenv("RATELIMIT_STORAGE_URI", "memory://")
