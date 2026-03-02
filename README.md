# SuryaMandal — सूर्यमण्डल

> An interactive 3D solar system visualizer. Pick any date and see the accurate positions of all 8 planets, powered by [astropy](https://www.astropy.org/) ephemeris data and rendered with [Three.js](https://threejs.org/).

**Live demo:** _[deploy to Render and paste URL here]_

---

## What is SuryaMandal?

**Surya** (सूर्य) = Sun · **Mandal** (मण्डल) = realm / circle

SuryaMandal fetches real heliocentric planet positions for any date/time and renders them in an interactive 3D scene in your browser. You can rotate, zoom, pan, click planets to focus on them, or hit **Animate** to watch the solar system move day by day.

### Features

- Accurate positions via `astropy` (same data used by NASA/JPL)
- Interactive 3D rendering with Three.js + OrbitControls
- Date/time picker — travel to any point in history or the future
- Animate mode — step forward day by day
- Planet labels, hover tooltips with distance in AU
- Saturn's rings
- Faint orbit paths for all planets
- Starfield background

---

## Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.13, FastAPI, Uvicorn |
| Astronomy | astropy (get_body_barycentric) |
| Frontend | Three.js 0.170 (CDN, no build step) |
| Deployment | Render (free tier) |

---

## Local Development

```bash
# 1. Clone
git clone git@github.com:davetejas/SuryaMandal.git
cd SuryaMandal

# 2. Create virtual environment
python -m venv .venv
source .venv/bin/activate      # macOS / Linux
# .venv\Scripts\activate       # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the dev server
uvicorn src.main:app --reload

# 5. Open http://localhost:8000
```

The `--reload` flag restarts the server on file changes. The first request may be slow (~2s) as astropy downloads ephemeris data; subsequent requests are fast.

---

## API Reference

### `GET /api/positions`

Returns heliocentric Cartesian coordinates (AU) for all 8 planets.

**Query parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `date` | ISO-8601 string | now | e.g. `2025-06-21T12:00:00Z` |

**Example:**

```bash
curl "http://localhost:8000/api/positions?date=2000-01-01T12:00:00Z"
```

```json
{
  "date": "2000-01-01T12:00:00+00:00",
  "planets": {
    "mercury": { "x": -0.131, "y": -0.447, "z": -0.031, "color": "#b5b5b5", "radius_au": 0.387 },
    "venus":   { "x": 0.612,  "y": -0.349, "z": -0.039, "color": "#e8cda0", "radius_au": 0.723 },
    "earth":   { "x": -0.178, "y":  0.967, "z":  0.0,   "color": "#4fa3e0", "radius_au": 1.0   },
    ...
  }
}
```

### `GET /health`

Returns `{"status": "healthy"}` — used by Render's health check.

---

## Running Tests

```bash
pytest tests/ -v
```

Tests cover:
- All 8 planets returned with correct keys
- Earth's distance from Sun ≈ 1 AU at J2000
- Jupiter's distance ≈ 5.2 AU
- API endpoints: positions, health, invalid date handling
- Frontend HTML is served at `/`

---

## Deploying to Render

1. Push this repo to GitHub (`git@github.com:davetejas/SuryaMandal.git`)
2. Go to [render.com](https://render.com) → **New Web Service**
3. Connect your GitHub account and select **SuryaMandal**
4. Render auto-detects `render.yaml` — no manual config needed
5. Click **Deploy** — your site will be live at `https://suryamandal.onrender.com`

Subsequent pushes to `main` trigger automatic redeployments.

> **Note:** Render free tier spins down after 15 minutes of inactivity. The first request after a cold start takes ~30s. Consider adding a cron ping service (e.g. UptimeRobot) to keep it warm.

---

## Architecture

```
Browser (Three.js)
    │  GET /api/positions?date=…
    ▼
FastAPI (src/main.py)
    │  calls
    ▼
solar.py → astropy.get_body_barycentric()
              │
              └── Returns (x, y, z) in AU for each planet
```

The frontend is a single self-contained HTML file served directly by FastAPI. No separate build pipeline or CDN needed.

---

## Post-MVP Ideas

- Time animation controls (play/pause/speed)
- Click-to-focus on any planet with orbital info panel
- Moon orbiting Earth
- Asteroid belt particle system
- Mobile touch support
- PWA / offline mode

---

## License

BSD 3-Clause — see [LICENSE](LICENSE).
