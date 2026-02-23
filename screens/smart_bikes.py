import httpx

from screens.base import Screen, load_font

ALL_STATIONS_URL = "https://serverapp.ratas.tartu.ee/api/map/stations/"
STATION_INFO_BASE_URL = "https://serverapp.ratas.tartu.ee/api/map/station/"
RATAS_API_TIMEOUT = 60 * 2

HEADERS = {
    "accept": "application/json, text/plain, */*",
    "origin": "https://ratas.tartu.ee",
    "referer": "https://ratas.tartu.ee/",
}


class SmartBikeManager:
    def __init__(self):
        self.all_stations = self._get_alL_stations()

    def _get_alL_stations(self, url: str = ALL_STATIONS_URL):
        response = httpx.get(url, headers=HEADERS, timeout=RATAS_API_TIMEOUT)
        response.raise_for_status()
        return response.json()["results"]

    def _get_station_info_by_name(self, station_name: str) -> dict:
        for station_info in self.all_stations:
            if station_info["name"] == station_name:
                return station_info

    def _get_raw_bikes_by_station_name(self, station_name: str):
        station_info = self._get_station_info_by_name(station_name)
        station_id = station_info["station_id"]
        url = f"{STATION_INFO_BASE_URL}{station_id}/"

        response = httpx.get(url, headers=HEADERS, timeout=RATAS_API_TIMEOUT)
        response.raise_for_status()
        return response.json()

    def _count_bikes_from_raw_station_info(self, bikes_info: dict):
        counted_bikes = {
            "station_name": bikes_info["name"],
            "regular_bikes": bikes_info["bikes_primary"]
            + bikes_info["bikes_secondary"],
            "electric_bikes": bikes_info["pedelecs_primary"]
            + bikes_info["pedelecs_secondary"],
        }
        return counted_bikes

    def get_bikes_on_station(self, station_name: str):
        info = self._get_raw_bikes_by_station_name(station_name)
        return self._count_bikes_from_raw_station_info(info)


class SmartBikesScreen(Screen):
    name = "smart_bikes"

    def __init__(self, station_name: str):
        self.font = load_font("FreePixel.ttf", 20)
        self.manager = SmartBikeManager()
        self.station_name = station_name
        self.bikes_info = None

    def prefetch(self):
        self.bikes_info = self.manager.get_bikes_on_station(self.station_name)

    def draw(self, draw, width, height):
        if self.bikes_info is None:
            text = "Loading..."
            bbox = draw.textbbox((0, 0), text, font=self.font)
            tw = bbox[2] - bbox[0]
            th = bbox[3] - bbox[1]
            draw.text(
                ((width - tw) // 2, (height - th) // 2),
                text,
                fill="white",
                font=self.font,
            )
            return

        station = self.bikes_info["station_name"]
        regular = f"Bikes: {self.bikes_info['regular_bikes']}"
        electric = f"E-bikes: {self.bikes_info['electric_bikes']}"

        s_bbox = draw.textbbox((0, 0), station, font=self.font)
        r_bbox = draw.textbbox((0, 0), regular, font=self.font)
        e_bbox = draw.textbbox((0, 0), electric, font=self.font)

        s_w, s_h = s_bbox[2] - s_bbox[0], s_bbox[3] - s_bbox[1]
        r_w, r_h = r_bbox[2] - r_bbox[0], r_bbox[3] - r_bbox[1]
        e_w, e_h = e_bbox[2] - e_bbox[0], e_bbox[3] - e_bbox[1]

        spacing = 4
        total_h = s_h + spacing + r_h + spacing + e_h
        y = (height - total_h) // 2

        draw.text(((width - s_w) // 2, y), station, fill="white", font=self.font)
        y += s_h + spacing
        draw.text(((width - r_w) // 2, y), regular, fill="white", font=self.font)
        y += r_h + spacing
        draw.text(((width - e_w) // 2, y), electric, fill="white", font=self.font)
