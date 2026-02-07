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
| `strava`      | Cycling distance and goal progress via Strava API    |

## Configuration

Copy the example config and edit it:

```bash
cp config.example.json config.json
```

`config.json` fields:

| Field         | Type     | Description                                                                  |
| ------------- | -------- | ---------------------------------------------------------------------------- |
| `screens`     | string[] | Ordered list of screens to display. Only listed screens are shown.           |
| `weather`     | object   | `lat` and `lon` for the weather screen.                                      |
| `smart_bikes` | object   | `station` — Tartu Smart Bike station name.                                   |
| `adsb`        | object   | `city` (display label), `lat`, `lon`, and optional `radius_km` (default 50). |
| `strava`      | object   | `goal_km` (default 1000) and `period` (`ytd`, `all`, or `recent`).           |

Every screen section accepts an optional `duration` (number) — seconds the screen stays visible before cycling to the next one. Defaults to 5.

Valid screen names: `date`, `weather`, `smart_bikes`, `adsb`, `cpu`, `strava`.
Screens without config (`date`, `cpu`) don't need a config section.

Example:

```json
{
  "screens": ["date", "weather", "smart_bikes", "adsb", "cpu", "strava"],
  "date": {
    "duration": 5
  },
  "weather": {
    "lat": 58.38,
    "lon": 26.72,
    "duration": 5
  },
  "smart_bikes": {
    "station": "Raatuse",
    "duration": 5
  },
  "adsb": {
    "city": "Tartu",
    "lat": 58.38,
    "lon": 26.72,
    "radius_km": 50,
    "duration": 5
  },
  "cpu": {
    "duration": 5
  },
  "strava": {
    "goal_km": 1000,
    "period": "ytd",
    "duration": 5
  }
}
```

## Strava Setup

The `strava` screen requires OAuth2 credentials. One-time setup:

1. Create a Strava API application at https://www.strava.com/settings/api
2. Set the **Authorization Callback Domain** to `localhost`
3. Run the helper script and follow the prompts:

```bash
uv run strava_auth.py
```

4. Copy the output into a `.env` file in the project root (see `.env.example`)

The app automatically refreshes access tokens (they expire every 6 hours) and caches them in `.strava_cache.json`. Both `.env` and `.strava_cache.json` are git-ignored.

## Usage

```bash
uv sync                              # install dependencies
uv run main.py --emulator     # run with pygame emulator
uv run main.py --gif out.gif  # record to GIF (Ctrl+C to save)
```

On a Raspberry Pi, run without flags to use the real SH1106 display:

```bash
uv run main.py
```
