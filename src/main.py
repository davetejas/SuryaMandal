"""
main.py — SuryaMandal FastAPI application.

Serves the Three.js frontend and exposes a planet-position API backed by astropy.
"""

import os
from datetime import datetime, timezone
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from src.solar import get_planet_positions

STATIC_DIR = Path(__file__).parent / "static"

app = FastAPI(
    title="SuryaMandal API",
    description="Interactive 3D solar system — planet positions via astropy",
    version="1.0.0",
)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", include_in_schema=False)
async def root():
    """Serve the Three.js frontend."""
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health")
async def health_check():
    """Health check used by Render and load balancers."""
    return {"status": "healthy"}


@app.get("/api/positions")
async def planet_positions(
    date: str = Query(
        default=None,
        description="ISO-8601 UTC datetime, e.g. 2025-06-21T12:00:00Z. Defaults to now.",
    )
):
    """
    Return heliocentric Cartesian positions (AU) for all 8 planets.

    Response shape:
    ```json
    {
      "date": "2025-06-21T12:00:00+00:00",
      "planets": {
        "earth": {"x": 0.98, "y": 0.12, "z": 0.0, "color": "#4fa3e0", "radius_au": 1.0},
        ...
      }
    }
    ```
    """
    if date is None:
        dt = datetime.now(tz=timezone.utc)
    else:
        try:
            dt = datetime.fromisoformat(date.replace("Z", "+00:00"))
        except ValueError:
            raise HTTPException(
                status_code=422,
                detail=f"Invalid date format '{date}'. Use ISO-8601, e.g. 2025-06-21T12:00:00Z",
            )

    positions = get_planet_positions(dt)
    return {"date": dt.isoformat(), "planets": positions}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("src.main:app", host="0.0.0.0", port=port, reload=False)
