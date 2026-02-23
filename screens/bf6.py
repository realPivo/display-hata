import time

import httpx

from screens.base import Screen, load_font

_FETCH_INTERVAL = 900  # seconds (15 minutes)


def _fetch_bf6(username: str, platform: str) -> dict | None:
    try:
        url = (
            "https://api.gametools.network/bf6/stats/"
            f"?categories=multiplayer&raw=false&format_values=true"
            f"&seperation=false&name={username}&platform={platform}&skip_battlelog=true"
        )
        resp = httpx.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return {
            "kills": data["kills"],
            "deaths": data["deaths"],
            "kd": data["killDeath"],
        }
    except Exception:
        return None


class Bf6Screen(Screen):
    name = "bf6"

    def __init__(self, username: str, platform: str = "pc"):
        self.username = username
        self.platform = platform
        self.font_title = load_font("BF_HEADLINE_NARROW-BOLD.ttf", 22)
        self.font = load_font("FreePixel.ttf", 19)
        self.font_sm = load_font("FreePixel.ttf", 16)
        self.stats: dict | None = None
        self._last_fetch_at: float = 0

    def prefetch(self):
        if self.stats is not None and (time.time() - self._last_fetch_at) < _FETCH_INTERVAL:
            return
        self.stats = _fetch_bf6(self.username, self.platform)
        if self.stats is not None:
            self._last_fetch_at = time.time()

    def draw(self, draw, width, height):
        if not self.stats:
            lines = [("BATTLEFIELD 6", self.font_title), ("N/A", self.font)]
        else:
            lines = [
                ("BATTLEFIELD 6", self.font_title),
                (f"K/D: {self.stats['kd']:.2f}", self.font),
                (
                    f"{self.stats['kills']:,} / {self.stats['deaths']:,}".replace(
                        ",", " "
                    ),
                    self.font_sm,
                ),
            ]

        spacing = 4
        bboxes = [draw.textbbox((0, 0), text, font=font) for text, font in lines]
        heights = [b[3] - b[1] for b in bboxes]
        widths = [b[2] - b[0] for b in bboxes]
        total_h = sum(heights) + spacing * (len(lines) - 1)
        y = (height - total_h) // 2

        for i, (text, font) in enumerate(lines):
            draw.text(((width - widths[i]) // 2, y), text, fill="white", font=font)
            y += heights[i] + spacing
