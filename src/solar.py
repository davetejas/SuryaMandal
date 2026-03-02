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
    "moon",
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
    "moon": 0.00257,  # 384,400 km — geocentric; rendered separately at fixed visual scale
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
    "moon": "#c8c8c8",
    "mars": "#c1440e",
    "jupiter": "#c88b3a",
    "saturn": "#e4d191",
    "uranus": "#7de8e8",
    "neptune": "#3f54ba",
}

# ---------------------------------------------------------------------------
# Nakshatra table
# Source: https://en.wikipedia.org/wiki/List_of_Nakshatras
#
# The 27 nakshatras divide the 360° ecliptic into equal 13°20' (13.333…°) arcs.
# start_deg / end_deg are tropical ecliptic longitudes (degrees).
#
# Column relationship to get_planet_positions():
#   heliocentric (x, y) → ecliptic_longitude_deg(x, y) → get_nakshatra(lon)
#   (For the Sun: geocentric lon = Earth's heliocentric lon + 180°)
# ---------------------------------------------------------------------------

NAKSHATRAS: list[dict] = [
    # num  name                  ruling_planet  deity                    symbol                              start_deg    end_deg
    {"num":  1, "name": "Ashwini",           "ruling_planet": "Ketu",    "deity": "Ashwini Kumara",       "symbol": "Horse's head",                      "start_deg":   0.000, "end_deg":  13.333},
    {"num":  2, "name": "Bharani",           "ruling_planet": "Venus",   "deity": "Yama",                 "symbol": "Yoni",                              "start_deg":  13.333, "end_deg":  26.667},
    {"num":  3, "name": "Krittika",          "ruling_planet": "Sun",     "deity": "Agni",                 "symbol": "Knife / razor",                     "start_deg":  26.667, "end_deg":  40.000},
    {"num":  4, "name": "Rohini",            "ruling_planet": "Moon",    "deity": "Brahma",               "symbol": "Cart / banyan tree",                "start_deg":  40.000, "end_deg":  53.333},
    {"num":  5, "name": "Mrigashirsha",      "ruling_planet": "Mars",    "deity": "Soma",                 "symbol": "Deer's head",                       "start_deg":  53.333, "end_deg":  66.667},
    {"num":  6, "name": "Ardra",             "ruling_planet": "Rahu",    "deity": "Rudra",                "symbol": "Teardrop / diamond",                "start_deg":  66.667, "end_deg":  80.000},
    {"num":  7, "name": "Punarvasu",         "ruling_planet": "Jupiter", "deity": "Aditi",                "symbol": "Bow and quiver",                    "start_deg":  80.000, "end_deg":  93.333},
    {"num":  8, "name": "Pushya",            "ruling_planet": "Saturn",  "deity": "Brihaspati",           "symbol": "Cow's udder / lotus",               "start_deg":  93.333, "end_deg": 106.667},
    {"num":  9, "name": "Ashlesha",          "ruling_planet": "Mercury", "deity": "Sarpas / Nagas",       "symbol": "Serpent",                           "start_deg": 106.667, "end_deg": 120.000},
    {"num": 10, "name": "Magha",             "ruling_planet": "Ketu",    "deity": "Pitrs",                "symbol": "Royal throne",                      "start_deg": 120.000, "end_deg": 133.333},
    {"num": 11, "name": "Purva Phalguni",    "ruling_planet": "Venus",   "deity": "Aryaman",              "symbol": "Front legs of bed / fig tree",       "start_deg": 133.333, "end_deg": 146.667},
    {"num": 12, "name": "Uttara Phalguni",   "ruling_planet": "Sun",     "deity": "Bhaga",                "symbol": "Four legs of bed / hammock",         "start_deg": 146.667, "end_deg": 160.000},
    {"num": 13, "name": "Hasta",             "ruling_planet": "Moon",    "deity": "Savitri / Surya",      "symbol": "Hand / fist",                       "start_deg": 160.000, "end_deg": 173.333},
    {"num": 14, "name": "Chitra",            "ruling_planet": "Mars",    "deity": "Tvastar / Vishwakarma","symbol": "Bright jewel / pearl",               "start_deg": 173.333, "end_deg": 186.667},
    {"num": 15, "name": "Swati",             "ruling_planet": "Rahu",    "deity": "Vayu",                 "symbol": "Shoot of plant / coral",             "start_deg": 186.667, "end_deg": 200.000},
    {"num": 16, "name": "Vishakha",          "ruling_planet": "Jupiter", "deity": "Indra and Agni",       "symbol": "Triumphal arch / potter's wheel",    "start_deg": 200.000, "end_deg": 213.333},
    {"num": 17, "name": "Anuradha",          "ruling_planet": "Saturn",  "deity": "Mitra",                "symbol": "Triumphal arch / lotus",             "start_deg": 213.333, "end_deg": 226.667},
    {"num": 18, "name": "Jyeshtha",          "ruling_planet": "Mercury", "deity": "Indra",                "symbol": "Circular amulet / umbrella",        "start_deg": 226.667, "end_deg": 240.000},
    {"num": 19, "name": "Mula",              "ruling_planet": "Ketu",    "deity": "Nirriti",              "symbol": "Bunch of roots / elephant goad",    "start_deg": 240.000, "end_deg": 253.333},
    {"num": 20, "name": "Purva Ashadha",     "ruling_planet": "Venus",   "deity": "Apah",                 "symbol": "Elephant tusk / fan",               "start_deg": 253.333, "end_deg": 266.667},
    {"num": 21, "name": "Uttara Ashadha",    "ruling_planet": "Sun",     "deity": "Visvedevas",           "symbol": "Elephant tusk",                     "start_deg": 266.667, "end_deg": 280.000},
    {"num": 22, "name": "Shravana",          "ruling_planet": "Moon",    "deity": "Vishnu",               "symbol": "Ears / three footprints",           "start_deg": 280.000, "end_deg": 293.333},
    {"num": 23, "name": "Dhanishtha",        "ruling_planet": "Mars",    "deity": "Eight Vasus",          "symbol": "Drum / flute",                      "start_deg": 293.333, "end_deg": 306.667},
    {"num": 24, "name": "Shatabhishak",      "ruling_planet": "Rahu",    "deity": "Varuna",               "symbol": "Empty circle / stars",              "start_deg": 306.667, "end_deg": 320.000},
    {"num": 25, "name": "Purva Bhadrapada",  "ruling_planet": "Jupiter", "deity": "Aja Ekapada",          "symbol": "Swords / two-faced man",             "start_deg": 320.000, "end_deg": 333.333},
    {"num": 26, "name": "Uttara Bhadrapada", "ruling_planet": "Saturn",  "deity": "Ahir Budhyana",        "symbol": "Twins / snake in water",             "start_deg": 333.333, "end_deg": 346.667},
    {"num": 27, "name": "Revati",            "ruling_planet": "Mercury", "deity": "Pushan",               "symbol": "Pair of fish / drum",               "start_deg": 346.667, "end_deg": 360.000},
]

# Quick lookup: index by nakshatra number (1-based)
NAKSHATRA_BY_NUM: dict[int, dict] = {n["num"]: n for n in NAKSHATRAS}


def ecliptic_longitude_deg(x: float, y: float) -> float:
    """
    Convert heliocentric Cartesian (x, y) in AU to ecliptic longitude in degrees [0, 360).

    For the Sun's geocentric longitude (as seen from Earth), pass the negated
    Earth position: ecliptic_longitude_deg(-earth_x, -earth_y).
    """
    import math
    lon = math.degrees(math.atan2(y, x)) % 360.0
    return lon


def get_nakshatra(ecliptic_lon_deg: float) -> dict:
    """
    Return the nakshatra dict for a given tropical ecliptic longitude (degrees).

    Each nakshatra spans exactly 13°20' (13.333…°).
    Index: floor(lon / (360/27))

    Returns a copy of the matching NAKSHATRAS entry.
    """
    lon = ecliptic_lon_deg % 360.0
    idx = int(lon / (360.0 / 27))  # 0-based index → nakshatra num = idx + 1
    return NAKSHATRAS[idx]


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
