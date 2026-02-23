import json
import time
from pathlib import Path

import httpx
from dotenv import dotenv_values

from screens.base import Screen, load_font

_FETCH_INTERVAL = 300  # seconds (5 minutes)

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_CACHE_PATH = _PROJECT_ROOT / ".strava_cache.json"
_ENV_PATH = _PROJECT_ROOT / ".env"

STRAVA_TOKEN_URL = "https://www.strava.com/api/v3/oauth/token"
STRAVA_STATS_URL = "https://www.strava.com/api/v3/athletes/{athlete_id}/stats"

_PERIOD_KEYS = {
    "ytd": "ytd_ride_totals",
    "all": "all_ride_totals",
    "recent": "recent_ride_totals",
}


class StravaClient:
    """Manages Strava OAuth2 tokens and API calls."""

    def __init__(self):
        env = dotenv_values(_ENV_PATH)
        self.client_id = env["STRAVA_CLIENT_ID"]
        self.client_secret = env["STRAVA_CLIENT_SECRET"]
        self.athlete_id = env["STRAVA_ATHLETE_ID"]
        self._initial_refresh_token = env["STRAVA_REFRESH_TOKEN"]

        self.access_token: str | None = None
        self.refresh_token: str | None = None
        self.expires_at: int = 0
        self._load_cache()

    def _load_cache(self):
        if _CACHE_PATH.exists():
            try:
                data = json.loads(_CACHE_PATH.read_text())
                self.access_token = data.get("access_token")
                self.refresh_token = data.get("refresh_token")
                self.expires_at = data.get("expires_at", 0)
            except (json.JSONDecodeError, KeyError):
                pass

    def _save_cache(self):
        data = {
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "expires_at": self.expires_at,
        }
        _CACHE_PATH.write_text(json.dumps(data, indent=2))

    def _needs_refresh(self) -> bool:
        return self.access_token is None or time.time() >= (self.expires_at - 60)

    def _refresh_access_token(self):
        token_to_use = self.refresh_token or self._initial_refresh_token
        resp = httpx.post(
            STRAVA_TOKEN_URL,
            data={
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "grant_type": "refresh_token",
                "refresh_token": token_to_use,
            },
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()

        self.access_token = data["access_token"]
        self.refresh_token = data["refresh_token"]
        self.expires_at = data["expires_at"]
        self._save_cache()

    def _get_access_token(self) -> str:
        if self._needs_refresh():
            self._refresh_access_token()
        return self.access_token

    def get_ride_stats(self) -> dict:
        token = self._get_access_token()
        url = STRAVA_STATS_URL.format(athlete_id=self.athlete_id)
        resp = httpx.get(
            url,
            headers={"Authorization": f"Bearer {token}"},
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()


class StravaScreen(Screen):
    name = "strava"

    def __init__(self, goal_km: float = 1000, period: str = "ytd"):
        self.font = load_font("FreePixel.ttf", 16)
        self.goal_km = goal_km
        self.period_key = _PERIOD_KEYS.get(period, "ytd_ride_totals")
        self.client = StravaClient()
        self.distance_km: float | None = None
        self._last_fetch_at: float = 0

    def prefetch(self):
        if (
            self.distance_km is not None
            and (time.time() - self._last_fetch_at) < _FETCH_INTERVAL
        ):
            return
        try:
            stats = self.client.get_ride_stats()
            ride_totals = stats[self.period_key]
            self.distance_km = ride_totals["distance"] / 1000.0
            self._last_fetch_at = time.time()
        except Exception:
            self.distance_km = None

    def draw(self, draw, width, height):
        if self.distance_km is None:
            lines = ["Strava Rides", "N/A"]
        else:
            dist = self.distance_km
            goal = self.goal_km
            pct = (dist / goal * 100) if goal > 0 else 0

            lines = [
                "Strava Rides",
                f"{dist:.1f}/{goal:.0f} km",
                f"{pct:.1f}% done",
            ]

        spacing = 4
        bboxes = [draw.textbbox((0, 0), line, font=self.font) for line in lines]
        heights = [b[3] - b[1] for b in bboxes]
        widths = [b[2] - b[0] for b in bboxes]

        total_h = sum(heights) + spacing * (len(lines) - 1)
        y = (height - total_h) // 2

        for i, line in enumerate(lines):
            draw.text(
                ((width - widths[i]) // 2, y),
                line,
                fill="white",
                font=self.font,
            )
            y += heights[i] + spacing
