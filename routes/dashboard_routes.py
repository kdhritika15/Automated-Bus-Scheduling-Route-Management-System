"""
Dashboard summary API: /api/dashboard/stats

Read-only endpoint powering the four dashboard cards. Does not modify
any existing endpoint or behavior — added fresh alongside them.
"""

from flask import Blueprint, jsonify

from services import bus_service

dashboard_bp = Blueprint("dashboard_bp", __name__, url_prefix="/api")


@dashboard_bp.route("/dashboard/stats", methods=["GET"])
def dashboard_stats():
    """
    GET /api/dashboard/stats
    Returns: { total_buses, active_routes, available_buses, average_passenger_load }
    Public — no login required, same as other GET endpoints.
    """
    stats = bus_service.get_dashboard_stats()
    return jsonify(stats), 200