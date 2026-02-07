## Overview

**display-hata** is a collection Python scripts for Raspberry Pi Zero 2W, that drives an SH1106 OLED display (128x64, blue) to cycle through information screens. Uses `luma.oled` for hardware rendering and `luma.emulator` (pygame) for local development.

## Hardware

- **Board:** Raspberry Pi Zero 2W
- **Display:** SH1106 OLED, 128x64 resolution, blue
- **Interface:** I2C (primary), also supports SPI
- **Dev mode:** `luma.emulator` with pygame (no physical hardware needed)

## Architecture

- **Device layer** — factory that returns either a real `luma.oled.device.sh1106` or a `luma.emulator.device.pygame` device based on environment, e.g. `uv run main.py --emulator`
- **Screen abstraction** — each screen extends `Screen` (in `screens/base.py`) and implements `draw()`. Screens have three key properties:
  - `interval: float` — many seconds this screen stays visible before the loop moves to the next one.
  - `live: bool = False` — when `True`, the screen redraws continuously every 0.5s for its interval (e.g. ticking clock). When `False`, it draws once and sleeps.
  - `prefetch()` — optional hook called in a background thread while the _previous_ screen is displayed, so slow I/O (HTTP requests) completes before the screen is drawn.
- **Screen loop** — main loop cycles through registered screens on a timer. Before each screen is shown, its `prefetch()` has already run in a background thread during the previous screen's interval.
