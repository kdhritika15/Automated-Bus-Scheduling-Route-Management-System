"""
Validation helpers for bus data coming from API requests.

Kept separate from routes/ so validation rules can be tested and changed
independently of how they're wired into HTTP handlers.
"""


def validate_create_payload(data):
    """
    Validates the JSON body for POST /api/buses.
    Requires a non-empty bus_id and a non-empty route.
    Returns a list of error messages (empty list = valid).
    """
    errors = []

    bus_id = (data.get("bus_id") or "").strip()
    route = (data.get("route") or "").strip()

    if not bus_id:
        errors.append("bus_id is required.")
    if not route:
        errors.append("route is required.")

    return errors


def validate_update_payload(data):
    """
    Validates the JSON body for PUT /api/buses/<bus_id>.
    Updates are partial — only fields present in the body are checked.
    bus_id cannot be changed via update (it's the URL identifier).
    Returns a list of error messages (empty list = valid).
    """
    errors = []

    if "bus_id" in data:
        errors.append("bus_id cannot be changed after creation.")

    if "route" in data and not (data.get("route") or "").strip():
        errors.append("route cannot be empty.")

    return errors


def validate_search_params(source, destination):
    """
    Validates query parameters for GET /api/search.
    Both source and destination are required, non-empty strings.
    """
    errors = []

    if not source:
        errors.append("'source' query parameter is required.")
    if not destination:
        errors.append("'destination' query parameter is required.")

    return errors
