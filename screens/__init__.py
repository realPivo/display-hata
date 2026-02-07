import json
from pathlib import Path

from screens.adsb import AdsbScreen
from screens.cpu import CpuScreen
from screens.date import DateScreen
from screens.smart_bikes import SmartBikesScreen
from screens.weather import WeatherScreen

_config_path = Path(__file__).resolve().parent.parent / "config.json"
with open(_config_path) as f:
    _config = json.load(f)

CITIES = {name: tuple(coords) for name, coords in _config["cities"].items()}
CURRENT_CITY = _config["current_city"]

all_screens = [
    DateScreen(),
    WeatherScreen(lat=CITIES[CURRENT_CITY][0], lon=CITIES[CURRENT_CITY][1]),
    SmartBikesScreen("Pargi"),
    AdsbScreen(
        city=CURRENT_CITY, lat=CITIES[CURRENT_CITY][0], lon=CITIES[CURRENT_CITY][1]
    ),
    CpuScreen(),
]
