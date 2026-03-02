"""
Tests for SuryaMandal solar position calculations and FastAPI endpoints.
"""

from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.solar import PLANETS, get_planet_positions

client = TestClient(app)

J2000 = datetime(2000, 1, 1, 12, 0, 0, tzinfo=timezone.utc)


# ── Unit tests: solar.py ─────────────────────────────────────────────────────

def test_returns_all_planets():
    positions = get_planet_positions(J2000)
    for planet in PLANETS:
        assert planet in positions, f"Missing planet: {planet}"


def test_position_has_required_keys():
    positions = get_planet_positions(J2000)
    for name, data in positions.items():
        assert "x" in data
        assert "y" in data
        assert "z" in data
        assert "color" in data
        assert "radius_au" in data


def test_earth_distance_at_j2000():
    """Earth should be ~1 AU from the Sun at any date."""
    positions = get_planet_positions(J2000)
    earth = positions["earth"]
    dist = (earth["x"]**2 + earth["y"]**2 + earth["z"]**2) ** 0.5
    assert 0.98 <= dist <= 1.02, f"Earth distance {dist:.4f} AU unexpected"


def test_jupiter_distance_reasonable():
    """Jupiter should be ~5-6 AU from the Sun."""
    positions = get_planet_positions(J2000)
    jup = positions["jupiter"]
    dist = (jup["x"]**2 + jup["y"]**2 + jup["z"]**2) ** 0.5
    assert 4.9 <= dist <= 5.5, f"Jupiter distance {dist:.4f} AU unexpected"


def test_naive_datetime_treated_as_utc():
    naive = datetime(2024, 6, 21, 12, 0, 0)
    aware = datetime(2024, 6, 21, 12, 0, 0, tzinfo=timezone.utc)
    pos_naive = get_planet_positions(naive)
    pos_aware = get_planet_positions(aware)
    assert pos_naive["earth"]["x"] == pos_aware["earth"]["x"]


# ── Integration tests: FastAPI endpoints ─────────────────────────────────────

def test_health_endpoint():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "healthy"}


def test_positions_endpoint_no_date():
    resp = client.get("/api/positions")
    assert resp.status_code == 200
    body = resp.json()
    assert "date" in body
    assert "planets" in body
    for planet in PLANETS:
        assert planet in body["planets"]


def test_positions_endpoint_with_date():
    resp = client.get("/api/positions?date=2000-01-01T12:00:00Z")
    assert resp.status_code == 200
    body = resp.json()
    assert "2000-01-01" in body["date"]
    assert "earth" in body["planets"]


def test_positions_endpoint_invalid_date():
    resp = client.get("/api/positions?date=not-a-date")
    assert resp.status_code == 422


def test_frontend_serves_html():
    resp = client.get("/")
    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]
    assert b"SuryaMandal" in resp.content
