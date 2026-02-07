import httpx

from screens.base import Screen, load_font

PROVIDERS = [
    {
        "name": "adsb.lol",
        "url": "https://api.adsb.lol/v2/lat/{lat}/lon/{lon}/dist/{dist_nm}",
        "key": "ac",
    },
    {
        "name": "adsb.fi",
        "url": "https://opendata.adsb.fi/api/v2/lat/{lat}/lon/{lon}/dist/{dist_nm}",
        "key": "aircraft",
    },
]


def _fetch_unique_aircraft_count(lat: float, lon: float, dist_nm: int) -> int:
    """Fetch from both providers and return count of unique aircraft by hex."""
    seen_hexes: set[str] = set()

    for provider in PROVIDERS:
        url = provider["url"].format(lat=lat, lon=lon, dist_nm=dist_nm)
        try:
            resp = httpx.get(url, timeout=10)
            resp.raise_for_status()
            for ac in resp.json().get(provider["key"], []):
                hex_code = ac.get("hex")
                if hex_code:
                    seen_hexes.add(hex_code)
        except Exception:
            pass

    return len(seen_hexes)


class AdsbScreen(Screen):
    name = "adsb"

    def __init__(self, city: str, lat: float, lon: float, radius_km: int = 50):
        self.city = city
        self.lat = lat
        self.lon = lon
        self.dist_nm = int(radius_km * 0.539957)

        self.font = load_font("FreePixel.ttf", 16)
        self.count: int | None = None

    def prefetch(self):
        self.count = _fetch_unique_aircraft_count(self.lat, self.lon, self.dist_nm)

    def draw(self, draw, width, height):
        if self.count is None:
            lines = ["Aircraft", "N/A"]
        else:
            if self.count == 0:
                count_line = "No planes"
            elif self.count == 1:
                count_line = "1 plane"
            else:
                count_line = f"{self.count} planes"

            lines = [
                count_line,
                f"above {self.city}",
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
