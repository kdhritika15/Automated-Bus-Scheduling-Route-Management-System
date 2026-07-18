"""
Live availability API: /api/live
"""

from flask import Blueprint, jsonify, request

from services import bus_service

live_bp = Blueprint("live_bp", __name__, url_prefix="/api")


@live_bp.route("/live", methods=["GET"])
def live():
    """
    GET /api/live
    GET /api/live?source=X&destination=Y

    Returns buses with a freshly randomized, persisted passenger_load.
    When source and destination are both provided, only buses matching
    that route are returned — this is what makes the frontend's Live
    Availability section show only the searched route instead of the
    entire fleet. Without them, every bus is returned.
    """
    source = request.args.get("source", "").strip()
    destination = request.args.get("destination", "").strip()

    buses = bus_service.get_live_buses(source or None, destination or None)
    return jsonify({"buses": [b.to_dict() for b in buses]}), 200
