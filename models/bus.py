from datetime import datetime

from database.db import db


class Bus(db.Model):
    """
    Represents a single bus in the fleet.

    This replaces the unified `busData` array from script.js (Phase 2)
    with a real, persistent table. Fields map 1:1 to what the frontend
    already sends/expects: bus_id, source, destination, route, eta.
    passenger_load, created_at, and updated_at are new — previously
    passenger load was faked client-side with Math.random() and never stored.
    """

    __tablename__ = "buses"

    id = db.Column(db.Integer, primary_key=True)

    # Human-facing identifier, e.g. "Bus 42X". Must be unique — this is
    # the server-side fix for the duplicate-bus gap noted in the Phase 1 analysis.
    bus_id = db.Column(db.String(20), unique=True, nullable=False)

    # Required now that the Admin Panel always collects Source and
    # Destination — this is what makes route-based search and
    # route-specific Live Availability reliable.
    source = db.Column(db.String(100), nullable=False)
    destination = db.Column(db.String(100), nullable=False)

    route = db.Column(db.String(150), nullable=False)
    eta = db.Column(db.String(20), default="N/A")

    # Replaces the frontend's random passenger load with a real stored value.
    passenger_load = db.Column(db.Integer, default=0)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Serializes this bus into the JSON shape the frontend expects."""
        return {
            "bus_id": self.bus_id,
            "source": self.source,
            "destination": self.destination,
            "route": self.route,
            "eta": self.eta,
            "passenger_load": self.passenger_load,
        }

    def __repr__(self):
        return f"<Bus {self.bus_id}>"
