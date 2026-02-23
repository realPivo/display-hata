import httpx

from screens.base import Screen, load_font


def _fetch_weather(lat: float, lon: float) -> dict | None:
    """
    Fetch current weather.
    Replace URL with your preferred provider.
    Expected to return:
      {
        "temp": float,
        "feels_like": float,
        "condition": str,
      }
    """
    try:
        # Example using Open-Meteo (no API key)
        url = (
            "https://api.open-meteo.com/v1/forecast"
            f"?latitude={lat}&longitude={lon}"
            "&current=temperature_2m,apparent_temperature,weathercode"
        )
        resp = httpx.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()["current"]

        condition_map = {
            0: "Clear sky",
            1: "Mostly clear",
            2: "Partly cloudy",
            3: "Overcast",
            45: "Fog",
            48: "Rime fog",
            51: "Light drizzle",
            53: "Drizzle",
            55: "Heavy drizzle",
            56: "Frzg drizzle",
            57: "Hvy Frzg drizz",
            61: "Light rain",
            63: "Rain",
            65: "Heavy rain",
            66: "Frzg rain",
            67: "Hvy Frzg rain",
            71: "Light snow",
            73: "Snow",
            75: "Heavy snow",
            77: "Snow grains",
            80: "Light showers",
            81: "Showers",
            82: "Heavy showers",
            85: "Snow showers",
            86: "Hvy Sno Shwrs",
            95: "Thunderstorm",
            96: "T-Storm+Hail",
            99: "T-Storm+Hail",
        }

        return {
            "temp": round(data["temperature_2m"]),
            "feels_like": round(data["apparent_temperature"]),
            "condition": condition_map.get(data["weathercode"], "Weather"),
        }

    except Exception:
        return None


class WeatherScreen(Screen):
    name = "weather"

    def __init__(self, lat: float, lon: float):
        self.lat = lat
        self.lon = lon
        self.font_lg = load_font("FreePixel.ttf", 28)
        self.font = load_font("FreePixel.ttf", 18)
        self.font_sm = load_font("FreePixel.ttf", 14)
        self.weather: dict | None = None

    def prefetch(self):
        self.weather = _fetch_weather(self.lat, self.lon)

    def draw(self, draw, width, height):
        if not self.weather:
            rows = [("Weather", self.font_sm), ("N/A", self.font_lg)]
        else:
            rows = [
                (self.weather["condition"], self.font_sm),
                (f"{self.weather['temp']}°C", self.font_lg),
                (f"Feels {self.weather['feels_like']}°", self.font_sm),
            ]

        spacing = 6
        bboxes = [draw.textbbox((0, 0), text, font=font) for text, font in rows]
        heights = [b[3] - b[1] for b in bboxes]
        widths = [b[2] - b[0] for b in bboxes]

        total_h = sum(heights) + spacing * (len(rows) - 1)
        y = (height - total_h) // 2

        for i, (text, font) in enumerate(rows):
            draw.text(
                ((width - widths[i]) // 2, y),
                text,
                fill="white",
                font=font,
            )
            y += heights[i] + spacing
