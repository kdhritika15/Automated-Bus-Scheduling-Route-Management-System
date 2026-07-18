from database.db import db
from models.bus import Bus

# Real, geocodable place names (replacing "Station A" / "Station B" etc.)
# so the dynamic Live Route Map can resolve an actual driving route.
# Swap these for landmarks in your own city if deploying elsewhere.
DEFAULT_BUSES = [
    {
        "bus_id": "Bus 21A",
        "source": "Gachibowli, Hyderabad",
        "destination": "Hitech City, Hyderabad",
        "route": "Financial District Route",
        "eta": "6 mins",
        "passenger_load": 0,
    },
    {
        "bus_id": "Bus 10X",
        "source": "Secunderabad Railway Station",
        "destination": "Rajiv Gandhi International Airport",
        "route": "Airport Express via ORR",
        "eta": "18 mins",
        "passenger_load": 0,
    },
    {
        "bus_id": "Bus 42X",
        "source": "Koti",
        "destination": "Ameerpet",
        "route": "MG Road Route",
        "eta": "10 mins",
        "passenger_load": 0,
    },
    {
        "bus_id": "Bus 17A",
        "source": "Uppal",
        "destination": "Kukatpally",
        "route": "NH65 Route",
        "eta": "20 mins",
        "passenger_load": 0,
    },
    {
        "bus_id": "Bus 101",
        "source": "Miyapur",
        "destination": "Ameerpet",
        "route": "Metro Corridor",
        "eta": "12 mins",
        "passenger_load": 0,
    },
    {
        "bus_id": "Bus 102",
        "source": "Kukatpally",
        "destination": "Miyapur",
        "route": "KPHB Route",
        "eta": "8 mins",
        "passenger_load": 0,
    },
    {
        "bus_id": "Bus 103",
        "source": "Charminar",
        "destination": "Mehdipatnam",
        "route": "Old City Route",
        "eta": "15 mins",
        "passenger_load": 0,
    },
    {
        "bus_id": "Bus 104",
        "source": "LB Nagar",
        "destination": "Dilsukhnagar",
        "route": "City Route",
        "eta": "7 mins",
        "passenger_load": 0,
    },
    {
        "bus_id": "Bus 105",
        "source": "Lingampally",
        "destination": "Gachibowli",
        "route": "IT Corridor",
        "eta": "9 mins",
        "passenger_load": 0,
    },
    {
        "bus_id": "Bus 106",
        "source": "Banjara Hills",
        "destination": "Jubilee Hills",
        "route": "Road No.12",
        "eta": "6 mins",
        "passenger_load": 0,
    },
    {
        "bus_id": "Bus 107",
        "source": "Nampally",
        "destination": "Lakdikapul",
        "route": "Assembly Route",
        "eta": "8 mins",
        "passenger_load": 0,
    },
    {
        "bus_id": "Bus 108",
        "source": "Begumpet",
        "destination": "Paradise",
        "route": "Begumpet Main Road",
        "eta": "11 mins",
        "passenger_load": 0,
    },
    {
        "bus_id": "Bus 109",
        "source": "Madhapur",
        "destination": "Kondapur",
        "route": "Cyber Towers Route",
        "eta": "5 mins",
        "passenger_load": 0,
    },
    {
        "bus_id": "Bus 110",
        "source": "Tarnaka",
        "destination": "Habsiguda",
        "route": "Osmania Route",
        "eta": "6 mins",
        "passenger_load": 0,
    },
    {
        "bus_id": "Bus 111",
        "source": "Shamshabad",
        "destination": "Gachibowli",
        "route": "Outer Ring Road",
        "eta": "22 mins",
        "passenger_load": 0,
    },
    {
        "bus_id": "Bus 112",
        "source": "Kompally",
        "destination": "Secunderabad",
        "route": "Medchal Highway",
        "eta": "16 mins",
        "passenger_load": 0,
    },
    {
        "bus_id": "Bus 113",
        "source": "ECIL",
        "destination": "Uppal",
        "route": "Warangal Highway",
        "eta": "14 mins",
        "passenger_load": 0,
    },
    {
        "bus_id": "Bus 114",
        "source": "Nagole",
        "destination": "LB Nagar",
        "route": "Nagole Main Road",
        "eta": "9 mins",
        "passenger_load": 0,
    },
    {
        "bus_id": "Bus 115",
        "source": "Abids",
        "destination": "Koti",
        "route": "City Center Route",
        "eta": "5 mins",
        "passenger_load": 0,
    },
    {
        "bus_id": "Bus 116",
        "source": "Paradise",
        "destination": "Secunderabad Railway Station",
        "route": "Station Route",
        "eta": "6 mins",
        "passenger_load": 0,
    }
]
def seed_database():
    """
    Populates the buses table with default data on first run only.
    Safe to call every time the app starts — it checks for existing
    rows before inserting, so it never creates duplicates.
    """
    if Bus.query.count() == 0:
        for bus_data in DEFAULT_BUSES:
            db.session.add(Bus(**bus_data))
        db.session.commit()
        print("Database seeded with default buses.")
    else:
        print("Database already contains data — skipping seed.")
