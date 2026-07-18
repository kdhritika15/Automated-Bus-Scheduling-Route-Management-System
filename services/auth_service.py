"""
Admin authentication logic — credential checking and the decorator that
protects write endpoints. Session state itself is Flask's built-in
signed-cookie session (session["is_admin"]), so no extra session library
or database table is needed for this single-admin setup.
"""

from functools import wraps

from flask import jsonify, session
from werkzeug.security import check_password_hash

from config import Config


def verify_credentials(username, password):
    """
    Checks a submitted username/password against the single configured
    admin account. Returns True only if both match.
    """
    if username != Config.ADMIN_USERNAME:
        return False
    return check_password_hash(Config.ADMIN_PASSWORD_HASH, password)


def login_required(view_func):
    """
    Decorator for routes that require an active admin session.
    Returns 401 Unauthorized (JSON) if session["is_admin"] is not set —
    this is the actual enforcement point; the frontend hiding buttons is
    a UX nicety, not the security boundary.
    """

    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if not session.get("is_admin"):
            return jsonify({"error": "Unauthorized. Admin login required."}), 401
        return view_func(*args, **kwargs)

    return wrapper
