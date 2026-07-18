import os
from werkzeug.security import generate_password_hash

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    """
    Central configuration for the Flask app.
    Values can be overridden via environment variables (e.g. in a .env file),
    so secrets never need to be hardcoded or committed to version control.
    """

    # Used by Flask to sign session cookies. Change this in production.
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")

    # SQLite database file lives inside the database/ folder.
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "sqlite:///" + os.path.join(BASE_DIR, "database", "bus_scheduler.db"),
    )

    # Disables a SQLAlchemy feature we don't need; avoids console warnings.
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Single default admin account (Phase 6). Stored as a hash, not plain
    # text, even though the source password is simple — never keep a
    # readable password in config or memory if it can be avoided.
    ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD_HASH = generate_password_hash(
        os.environ.get("ADMIN_PASSWORD", "admin123")
    )
