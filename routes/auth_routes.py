"""
Admin authentication API: /api/auth/login, /api/auth/logout, /api/auth/status
"""

from flask import Blueprint, jsonify, request, session

from services.auth_service import verify_credentials

auth_bp = Blueprint("auth_bp", __name__, url_prefix="/api/auth")


@auth_bp.route("/login", methods=["POST"])
def login():
    """
    POST /api/auth/login
    Body: { "username": "...", "password": "..." }
    On success, sets session["is_admin"] = True (a signed cookie Flask
    manages automatically) and returns 200. Invalid credentials return 401.
    """
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    if not username or not password:
        return jsonify({"error": "Username and password are required."}), 400

    if not verify_credentials(username, password):
        return jsonify({"error": "Invalid username or password."}), 401

    session["is_admin"] = True
    session["username"] = username
    return jsonify({"message": "Login successful.", "username": username}), 200


@auth_bp.route("/logout", methods=["POST"])
def logout():
    """POST /api/auth/logout — clears the admin session."""
    session.clear()
    return jsonify({"message": "Logged out successfully."}), 200


@auth_bp.route("/status", methods=["GET"])
def status():
    """
    GET /api/auth/status — lets the frontend check whether the current
    browser session is already logged in (e.g. after a page refresh),
    so the UI can show the right buttons on load instead of always
    starting in a logged-out state.
    """
    return jsonify({"is_admin": bool(session.get("is_admin"))}), 200
