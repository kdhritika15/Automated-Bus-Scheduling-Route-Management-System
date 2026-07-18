"""
Business logic for buses — all database reads/writes go through here.
Routes call these functions instead of touching db.session or Bus.query
directly, so the "how" of persistence stays in one place.
"""

import random

from database.db import db
from models.bus import Bus


def get_all_buses():
    """Returns every bus in the fleet."""
    return Bus.query.all()


def get_bus_by_bus_id(bus_id):
    """Looks up a single bus by its human-facing bus_id (e.g. 'Bus 42X')."""
    return Bus.query.filter_by(bus_id=bus_id).first()


def create_bus(data):
    """
    Creates and saves a new bus. Assumes data has already passed
    validate_create_payload — caller is also responsible for checking
    bus_id uniqueness before calling this.
    """
    bus = Bus(
        bus_id=data["bus_id"].strip(),
        source=data["source"].strip(),
        destination=data["destination"].strip(),
        route=data["route"].strip(),
        eta=(data.get("eta") or "N/A").strip(),
        passenger_load=0,
    )
    db.session.add(bus)
    db.session.commit()
    return bus


def update_bus(bus, data):
    """
    Applies a partial update to an existing bus. Only fields present
    in `data` are changed — omitted fields keep their current value.

    bus_id uniqueness for a rename is checked by the caller (routes/bus_routes.py)
    before this is called, since that check needs a database lookup against
    other buses, not just this one.
    """
    if "bus_id" in data:
        bus.bus_id = data["bus_id"].strip()
    if "source" in data:
        bus.source = data["source"].strip()
    if "destination" in data:
        bus.destination = data["destination"].strip()
    if "route" in data:
        bus.route = data["route"].strip()
    if "eta" in data:
        bus.eta = (data.get("eta") or "N/A").strip()

    db.session.commit()
    return bus


def delete_bus(bus):
    """Removes a bus from the database."""
    db.session.delete(bus)
    db.session.commit()


def search_buses(source, destination):
    """
    Finds buses matching a source/destination search.

    A bus matches if either:
      - its stored source AND destination exactly match the search
        (case-insensitive), or
      - the search text appears inside the bus's route name — this is
        what lets Admin-added buses (which only have a route, no
        source/destination) show up in search, same behavior the
        frontend used in Phase 2.
    """
    source_l = source.lower()
    destination_l = destination.lower()

    matches = []
    for bus in Bus.query.all():
        exact_match = (
            bus.source
            and bus.destination
            and bus.source.lower() == source_l
            and bus.destination.lower() == destination_l
        )
        route_match = bus.route and (
            source_l in bus.route.lower() or destination_l in bus.route.lower()
        )
        if exact_match or route_match:
            matches.append(bus)

    return matches


def get_live_buses(source=None, destination=None):
    """
    Returns buses with a freshly randomized, persisted passenger_load.
    This replaces the frontend's Math.random() trick — the load is now
    generated and stored server-side.

    If source and destination are both given, only buses matching that
    route (via the same rules as search_buses) are returned and updated —
    this powers the route-specific Live Availability section. If either
    is omitted, every bus is returned (kept for flexibility elsewhere).
    """
    if source and destination:
        buses = search_buses(source, destination)
    else:
        buses = Bus.query.all()

    for bus in buses:
        bus.passenger_load = random.randint(0, 100)
    db.session.commit()
    return buses


def get_dashboard_stats():
    """
    Computes summary numbers for the dashboard cards. Read-only — does
    not modify passenger_load or any other stored value, unlike
    get_live_buses(). Uses whatever passenger_load each bus currently
    has in the database (last set by a /api/live call, or 0 if a bus
    has never appeared in a live lookup).
    """
    buses = Bus.query.all()
    total_buses = len(buses)

    active_routes = len({bus.route for bus in buses if bus.route})

    # "Available" = not near-full capacity. Threshold kept simple and
    # explicit here rather than hardcoded inline in the route handler.
    AVAILABLE_LOAD_THRESHOLD = 90
    available_buses = sum(
        1 for bus in buses if bus.passenger_load < AVAILABLE_LOAD_THRESHOLD
    )

    if total_buses > 0:
        average_passenger_load = round(
            sum(bus.passenger_load for bus in buses) / total_buses, 1
        )
    else:
        average_passenger_load = 0

    return {
        "total_buses": total_buses,
        "active_routes": active_routes,
        "available_buses": available_buses,
        "average_passenger_load": average_passenger_load,
    }