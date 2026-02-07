import json
from pathlib import Path

from screens.adsb import AdsbScreen
from screens.cpu import CpuScreen
from screens.date import DateScreen
from screens.smart_bikes import SmartBikesScreen
from screens.strava import StravaScreen
from screens.weather import WeatherScreen

_config_path = Path(__file__).resolve().parent.parent / "config.json"
with open(_config_path) as f:
    _config = json.load(f)

_SCREEN_FACTORIES = {
    "date": lambda cfg: DateScreen(),
    "weather": lambda cfg: WeatherScreen(lat=cfg["lat"], lon=cfg["lon"]),
    "smart_bikes": lambda cfg: SmartBikesScreen(cfg["station"]),
    "adsb": lambda cfg: AdsbScreen(city=cfg["city"], lat=cfg["lat"], lon=cfg["lon"], radius_km=cfg.get("radius_km", 50)),
    "cpu": lambda cfg: CpuScreen(),
    "strava": lambda cfg: StravaScreen(goal_km=cfg.get("goal_km", 1000), period=cfg.get("period", "ytd")),
}

all_screens = []
for name in _config["screens"]:
    factory = _SCREEN_FACTORIES[name]
    screen_cfg = _config.get(name, {})
    screen = factory(screen_cfg)
    screen.interval = screen_cfg.get("duration", 5)
    all_screens.append(screen)
