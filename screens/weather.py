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
            0: "Clear",
            1: "Mostly clear",
            2: "Cloudy",
            3: "Overcast",
            61: "Rain",
            71: "Snow",
            95: "Storm",
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
        self.font = load_font("FreePixel.ttf", 16)
        self.font_sm = load_font("FreePixel.ttf", 12)
        self.weather: dict | None = None

    def prefetch(self):
        self.weather = _fetch_weather(self.lat, self.lon)

    def draw(self, draw, width, height):
        if not self.weather:
            lines = ["Weather", "N/A"]
        else:
            temp = self.weather["temp"]
            feels = self.weather["feels_like"]
            condition = self.weather["condition"]

            lines = [
                f"{temp}°C | {condition}",
                f"Feels {feels}°",
            ]

        spacing = 4
        fonts = []
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=self.font)
            if bbox[2] - bbox[0] <= width:
                fonts.append(self.font)
            else:
                fonts.append(self.font_sm)

        bboxes = [draw.textbbox((0, 0), line, font=fonts[i]) for i, line in enumerate(lines)]
        heights = [b[3] - b[1] for b in bboxes]
        widths = [b[2] - b[0] for b in bboxes]

        total_h = sum(heights) + spacing * (len(lines) - 1)
        y = (height - total_h) // 2

        for i, line in enumerate(lines):
            draw.text(
                ((width - widths[i]) // 2, y),
                line,
                fill="white",
                font=fonts[i],
            )
            y += heights[i] + spacing
