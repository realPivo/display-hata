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
- `httpx` — HTTP client for external API calls (smart bikes)

## Architecture

The app follows a **screen-based architecture**:

- **Device layer** — factory that returns either a real `luma.oled.device.sh1106` or a `luma.emulator.device.pygame` device based on environment
- **Screen abstraction** — each screen extends `Screen` (in `screens/base.py`) and implements `draw()`. Screens have two key flags:
  - `live: bool = False` — when `True`, the screen redraws continuously every 0.5s for its interval (e.g. ticking clock). When `False`, it draws once and sleeps.
  - `prefetch()` — optional hook called in a background thread while the *previous* screen is displayed, so slow I/O (HTTP requests) completes before the screen is drawn.
- **Screen loop** — main loop cycles through registered screens on a timer. Before each screen is shown, its `prefetch()` has already run in a background thread during the previous screen's interval.

### Screens

| Screen        | `live` | `prefetch` | Description                                      |
|---------------|--------|------------|--------------------------------------------------|
| `date`        | yes    | no         | Current date and time (ticking seconds)          |
| `cpu`         | no     | no         | CPU usage percentage                             |
| `smart_bikes` | no     | yes        | Bike availability at a Tartu Smart Bike station  |

### Display Coordinates

The SH1106 is 128x64 pixels. Origin (0, 0) is top-left. Use `luma.core.render.canvas` context manager for drawing — it handles double-buffering and flush.

## Development vs Production

The device is selected at startup:

- **Dev (default on non-Pi):** `luma.emulator.device.pygame` — opens a pygame window simulating 128x64
- **Production (on Pi):** `luma.oled.device.sh1106` via I2C (`port=1, address=0x3C`)

## Conventions

- Python 3.13+
- All rendering uses Pillow's `ImageDraw` through `luma.core.render.canvas`
- Fonts: use Pillow's built-in `ImageFont.load_default()` or bundle .ttf files in a `fonts/` directory
