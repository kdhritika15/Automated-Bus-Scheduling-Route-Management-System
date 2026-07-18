"""
Search API: /api/search?source=...&destination=...
"""

from flask import Blueprint, jsonify, request

from services import bus_service, validators

search_bp = Blueprint("search_bp", __name__, url_prefix="/api")


@search_bp.route("/search", methods=["GET"])
def search():
    """
    GET /api/search?source=X&destination=Y
    Returns buses whose source+destination exactly match, or whose route
    contains the searched text. Mirrors the frontend's Phase 2 search logic.
    """
    source = request.args.get("source", "").strip()
    destination = request.args.get("destination", "").strip()

    errors = validators.validate_search_params(source, destination)
    if errors:
        return jsonify({"error": " ".join(errors)}), 400

    matches = bus_service.search_buses(source, destination)

    if not matches:
        return jsonify({"buses": [], "message": "No matching bus found."}), 200

    return jsonify({"buses": [b.to_dict() for b in matches]}), 200
