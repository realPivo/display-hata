## Overview

**display-hata** is a Python application for Raspberry Pi Zero 2W that drives an SH1106 OLED display (128x64, blue) to cycle through information screens. Uses `luma.oled` for hardware rendering and `luma.emulator` (pygame) for local development.

![Example GIF](./example.gif)

## Hardware

- **Board:** Raspberry Pi Zero 2W
- **Display:** SH1106 OLED, 128x64 resolution, blue
- **Interface:** I2C (primary), also supports SPI
- **Dev mode:** `luma.emulator` with pygame (no physical hardware needed)

## Architecture

- **Device layer** — factory that returns either a real `luma.oled.device.sh1106` or a `luma.emulator.device.pygame` device based on environment.
- **Screen abstraction** — each screen extends `Screen` (in `screens/base.py`) and implements `draw()`. Screens have three key properties:
  - `interval: float` — many seconds this screen stays visible before the loop moves to the next one.
  - `live: bool = False` — when `True`, the screen redraws continuously every 0.5s for its interval (e.g. ticking clock). When `False`, it draws once and sleeps.
  - `prefetch()` — optional hook called in a background thread while the _previous_ screen is displayed, so slow I/O (HTTP requests) completes before the screen is drawn.
- **Screen loop** — main loop cycles through registered screens on a timer. Before each screen is shown, its `prefetch()` has already run in a background thread during the previous screen's interval.

## Screens

| Screen        | Description                                          |
| ------------- | ---------------------------------------------------- |
| `date`        | Current date and time with ticking seconds           |
| `weather`     | Temperature and condition via Open-Meteo API         |
| `smart_bikes` | Bike availability at a configured Smart Bike station |
| `adsb`        | Aircraft count within 50 km via adsb.lol / adsb.fi   |
| `cpu`         | CPU usage percentage                                 |

## Configuration

Copy the example config and edit it:

```bash
cp config.example.json config.json
```

`config.json` fields:

| Field          | Type     | Description                                                                 |
| -------------- | -------- | --------------------------------------------------------------------------- |
| `screens`      | string[] | Ordered list of screens to display. Only listed screens are shown.          |
| `weather`      | object   | `lat` and `lon` for the weather screen.                                     |
| `smart_bikes`  | object   | `station` — Tartu Smart Bike station name.                                  |
| `adsb`         | object   | `city` (display label), `lat`, `lon`, and optional `radius_km` (default 50).|

Valid screen names: `date`, `weather`, `smart_bikes`, `adsb`, `cpu`.
Screens without config (`date`, `cpu`) don't need a config section.

Example:

```json
{
  "screens": ["date", "weather", "smart_bikes", "adsb", "cpu"],
  "weather": {
    "lat": 58.38,
    "lon": 26.72
  },
  "smart_bikes": {
    "station": "Raatuse"
  },
  "adsb": {
    "city": "Tartu",
    "lat": 58.38,
    "lon": 26.72,
    "radius_km": 50
  }
}
```

## Usage

```bash
uv sync                              # install dependencies
uv run python main.py --emulator     # run with pygame emulator
uv run python main.py --gif out.gif  # record to GIF (Ctrl+C to save)
```

On a Raspberry Pi, run without flags to use the real SH1106 display:

```bash
uv run python main.py
```
