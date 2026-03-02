"""
solar.py — Heliocentric planet position calculations using astropy.

Returns Cartesian (x, y, z) coordinates in AU for each planet at a given UTC datetime,
in the ecliptic plane (HCRS approximation via solar system barycenter).
"""

from datetime import datetime, timezone

import numpy as np
from astropy.coordinates import get_body_barycentric
from astropy.time import Time

PLANETS = [
    "mercury",
    "venus",
    "earth",
    "mars",
    "jupiter",
    "saturn",
    "uranus",
    "neptune",
]

# Approximate mean orbital radii in AU (used for orbit ring rendering hints)
ORBITAL_RADII_AU = {
    "mercury": 0.387,
    "venus": 0.723,
    "earth": 1.000,
    "mars": 1.524,
    "jupiter": 5.203,
    "saturn": 9.537,
    "uranus": 19.19,
    "neptune": 30.07,
}

# Display colors (hex) for each planet
PLANET_COLORS = {
    "mercury": "#b5b5b5",
    "venus": "#e8cda0",
    "earth": "#4fa3e0",
    "mars": "#c1440e",
    "jupiter": "#c88b3a",
    "saturn": "#e4d191",
    "uranus": "#7de8e8",
    "neptune": "#3f54ba",
}


def get_planet_positions(dt: datetime) -> dict[str, dict]:
    """
    Compute heliocentric Cartesian positions (AU) for all 8 planets at a given UTC datetime.

    Args:
        dt: A timezone-aware datetime in UTC (or naive, treated as UTC).

    Returns:
        A dict mapping planet name → {"x": float, "y": float, "z": float, "color": str, "radius_au": float}
        Coordinates are in AU, relative to the Sun (heliocentric).
    """
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    t = Time(dt)

    # Get Sun's barycentric position so we can subtract it for heliocentric coords
    sun_pos = get_body_barycentric("sun", t)
    sun_x = sun_pos.x.to("AU").value
    sun_y = sun_pos.y.to("AU").value
    sun_z = sun_pos.z.to("AU").value

    result = {}
    for planet in PLANETS:
        body_pos = get_body_barycentric(planet, t)
        x = float(body_pos.x.to("AU").value - sun_x)
        y = float(body_pos.y.to("AU").value - sun_y)
        z = float(body_pos.z.to("AU").value - sun_z)
        result[planet] = {
            "x": round(x, 6),
            "y": round(y, 6),
            "z": round(z, 6),
            "color": PLANET_COLORS[planet],
            "radius_au": ORBITAL_RADII_AU[planet],
        }

    return result
