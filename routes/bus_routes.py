"""
CRUD API for buses: /api/buses and /api/buses/<bus_id>
"""

from flask import Blueprint, jsonify, request

from services import bus_service, validators
from services.auth_service import login_required

bus_bp = Blueprint("bus_bp", __name__, url_prefix="/api/buses")


@bus_bp.route("", methods=["GET"])
def get_buses():
    """GET /api/buses — returns every bus. Public — no login required."""
    buses = bus_service.get_all_buses()
    return jsonify({"buses": [b.to_dict() for b in buses]}), 200


@bus_bp.route("/<bus_id>", methods=["GET"])
def get_bus(bus_id):
    """GET /api/buses/<bus_id> — returns one bus, or 404. Public."""
    bus = bus_service.get_bus_by_bus_id(bus_id)
    if not bus:
        return jsonify({"error": f"Bus '{bus_id}' not found."}), 404
    return jsonify(bus.to_dict()), 200


@bus_bp.route("", methods=["POST"])
@login_required
def add_bus():
    """
    POST /api/buses — creates a new bus. Admin only (401 if not logged in).
    Body: { "bus_id": "...", "source": "...", "destination": "...", "route": "..." }
    "eta" is optional (defaults to "N/A"). All other fields are required.
    """
    data = request.get_json(silent=True) or {}

    errors = validators.validate_create_payload(data)
    if errors:
        return jsonify({"error": " ".join(errors)}), 400

    if bus_service.get_bus_by_bus_id(data["bus_id"].strip()):
        return jsonify({"error": f"Bus ID '{data['bus_id']}' already exists."}), 409

    bus = bus_service.create_bus(data)
    return jsonify(bus.to_dict()), 201


@bus_bp.route("/<bus_id>", methods=["PUT"])
@login_required
def update_bus(bus_id):
    """
    PUT /api/buses/<bus_id> — partially updates an existing bus.
    Admin only (401 if not logged in).
    Body: any subset of { "bus_id", "route", "source", "destination", "eta" }.
    Renaming bus_id is allowed, but rejected with 409 if another bus
    already uses the new ID.
    """
    bus = bus_service.get_bus_by_bus_id(bus_id)
    if not bus:
        return jsonify({"error": f"Bus '{bus_id}' not found."}), 404

    data = request.get_json(silent=True) or {}

    errors = validators.validate_update_payload(data)
    if errors:
        return jsonify({"error": " ".join(errors)}), 400

    new_bus_id = (data.get("bus_id") or "").strip()
    if new_bus_id and new_bus_id != bus.bus_id:
        existing = bus_service.get_bus_by_bus_id(new_bus_id)
        if existing:
            return jsonify({"error": f"Bus ID '{new_bus_id}' already exists."}), 409

    bus = bus_service.update_bus(bus, data)
    return jsonify(bus.to_dict()), 200


@bus_bp.route("/<bus_id>", methods=["DELETE"])
@login_required
def delete_bus(bus_id):
    """DELETE /api/buses/<bus_id> — removes a bus. Admin only (401 if not logged in)."""
    bus = bus_service.get_bus_by_bus_id(bus_id)
    if not bus:
        return jsonify({"error": f"Bus '{bus_id}' not found."}), 404

    bus_service.delete_bus(bus)
    return jsonify({"message": f"Bus '{bus_id}' deleted."}), 200
