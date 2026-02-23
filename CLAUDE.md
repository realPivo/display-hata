# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**display-hata** is a Python application for Raspberry Pi Zero 2W that drives an SH1106 OLED display (128x64, blue) to cycle through information screens. Uses `luma.oled` for hardware rendering and `luma.emulator` (pygame) for local development.

## Hardware Target

- **Board:** Raspberry Pi Zero 2W
- **Display:** SH1106 OLED, 128x64 resolution, blue
- **Interface:** I2C (primary), also supports SPI
- **Dev mode:** `luma.emulator` with pygame (no physical hardware needed)

## Package Manager

Uses **uv** (pyproject.toml). Key commands:

```bash
uv sync                  # install dependencies
uv run python main.py    # run the app
uv add <package>         # add a dependency
```

## Key Dependencies

- `luma.core` — device abstraction and rendering primitives
- `luma.oled` — SH1106/SSD1306 OLED drivers
- `luma.emulator` — pygame-based emulator for development
- `pillow` — image/font rendering (pulled in by luma)
- `psutil` — CPU usage and system metrics
- `httpx` — HTTP client for external API calls (weather, smart bikes, ADS-B, Strava)
- `python-dotenv` — loads `.env` file for Strava credentials

## Architecture

The app follows a **screen-based architecture**:

- **Device layer** — factory in `device.py` that returns a real `luma.oled.device.sh1106`, a `luma.emulator.device.pygame`, or a `luma.emulator.device.gifanim` device based on CLI flags and environment
- **Screen abstraction** — each screen extends `Screen` (in `screens/base.py`) and implements `draw()`. Screens have two key flags:
  - `live: bool = False` — when `True`, the screen redraws continuously every 0.5s for its interval (e.g. ticking clock). When `False`, it draws once and sleeps.
  - `prefetch()` — optional hook called in a background thread while the *previous* screen is displayed, so slow I/O (HTTP requests) completes before the screen is drawn.
- **Screen loop** — main loop cycles through registered screens on a timer. Before each screen is shown, its `prefetch()` has already run in a background thread during the previous screen's interval.

### Screens

| Screen        | `live` | `prefetch` | Description                                          |
|---------------|--------|------------|------------------------------------------------------|
| `date`        | yes    | no         | Current date and time (ticking seconds)              |
| `weather`     | no     | yes        | Temperature and condition via Open-Meteo API         |
| `smart_bikes` | no     | yes        | Bike availability at a configured Smart Bike station |
| `adsb`        | no     | yes        | Aircraft count within 50 km via adsb.lol / adsb.fi   |
| `cpu`         | no     | no         | CPU usage percentage                                 |
| `strava`      | no     | yes        | Cycling distance and goal progress via Strava API    |
| `bf6`         | no     | yes        | Battlefield 6 K/D ratio and kill/death counts (gametools.network API, cached 15 min) |
| `map`         | yes    | no         | ASCII art map with randomly blinking city dots       |

### Display Coordinates

The SH1106 is 128x64 pixels. Origin (0, 0) is top-left. Use `luma.core.render.canvas` context manager for drawing — it handles double-buffering and flush.

## Configuration

The app reads `config.json` at startup (see `config.example.json` for reference). Fields:

- `current_city` — name of the active city (must be a key in `cities`)
- `smart_bikes_station` — Tartu Smart Bike station name (e.g. `"Pargi"`)
- `cities` — map of city names to `[latitude, longitude]` pairs

`current_city` determines the location used by the `weather` and `adsb` screens. `smart_bikes_station` sets which station the `smart_bikes` screen queries.

The `strava` screen reads OAuth2 credentials from a `.env` file (see `.env.example`). Mutable tokens are cached in `.strava_cache.json` (git-ignored). Run `uv run python strava_auth.py` for initial setup.

## Development vs Production

The device is selected at startup via CLI flags:

- **`--emulator`** (or auto-detected non-Pi): `luma.emulator.device.pygame` — opens a pygame window simulating 128x64
- **`--gif <file>`**: `luma.emulator.device.gifanim` — records frames to a GIF file (Ctrl+C to stop and save)
- **Production (on Pi, no flags):** `luma.oled.device.sh1106` via I2C (`port=1, address=0x3C`)

## Conventions

- Python 3.13+
- All rendering uses Pillow's `ImageDraw` through `luma.core.render.canvas`
- Fonts: `FreePixel.ttf` bundled in `fonts/`; load via `load_font()` helper in `screens/base.py`
