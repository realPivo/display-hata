import time
from pathlib import Path

import httpx
from dotenv import dotenv_values

from screens.base import Screen, load_font

_FETCH_INTERVAL = 900  # seconds (15 minutes)
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_ENV_PATH = _PROJECT_ROOT / ".env"

_N2YO_BASE = "https://api.n2yo.com/rest/v1/satellite/above/{lat}/{lon}/0/{radius}/{cat}/&apiKey={key}"


def _fetch_count(
    lat: float, lon: float, category: int, api_key: str, search_radius: int
) -> int:
    url = _N2YO_BASE.format(
        lat=lat, lon=lon, radius=search_radius, cat=category, key=api_key
    )
    try:
        resp = httpx.get(url, timeout=10)
        resp.raise_for_status()
        return resp.json().get("info", {}).get("satcount", 0)
    except Exception:
        return 0


class SatellitesScreen(Screen):
    name = "satellites"

    def __init__(self, lat: float, lon: float, min_elevation: int = 30):
        self.lat = lat
        self.lon = lon
        self.search_radius = 90 - min_elevation
        self.font_sm = load_font("FreePixel.ttf", 14)
        self.font = load_font("FreePixel.ttf", 19)
        self.iss_above: bool = False
        self.galileo: int = 0
        self.starlink: int = 0
        self._fetched: bool = False
        self._last_fetch_at: float = 0

    def prefetch(self):
        if self._fetched and (time.time() - self._last_fetch_at) < _FETCH_INTERVAL:
            return
        api_key = dotenv_values(_ENV_PATH).get("N2YO_API_KEY", "")
        if not api_key:
            return
        self.iss_above = (
            _fetch_count(self.lat, self.lon, 2, api_key, self.search_radius) > 0
        )
        self.galileo = _fetch_count(self.lat, self.lon, 22, api_key, self.search_radius)
        self.starlink = _fetch_count(
            self.lat, self.lon, 52, api_key, self.search_radius
        )
        self._fetched = True
        self._last_fetch_at = time.time()

    def draw(self, draw, width, height):
        if not self._fetched:
            lines = [("Space objects", self.font_sm), ("N/A", self.font)]
        else:
            lines = [("Space objects", self.font_sm)]
            if self.iss_above:
                lines.append(("ISS above!", self.font))
            lines += [
                (f"{self.galileo} Galileo", self.font),
                (f"{self.starlink} Starlink", self.font),
            ]

        spacing = 3
        bboxes = [draw.textbbox((0, 0), text, font=font) for text, font in lines]
        heights = [b[3] - b[1] for b in bboxes]
        widths = [b[2] - b[0] for b in bboxes]
        total_h = sum(heights) + spacing * (len(lines) - 1)
        y = (height - total_h) // 2

        for i, (text, font) in enumerate(lines):
            draw.text(((width - widths[i]) // 2, y), text, fill="white", font=font)
            y += heights[i] + spacing
