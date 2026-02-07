from abc import ABC, abstractmethod
from pathlib import Path

from PIL import ImageFont

FONTS_DIR = Path(__file__).resolve().parent.parent / "fonts"


def load_font(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONTS_DIR / name), size)


class Screen(ABC):
    # How many seconds this screen stays visible before the loop moves to the next one.
    interval: float = 5.0
    # Whether this screen needs continuous redrawing (e.g. ticking clock).
    live: bool = False

    @property
    @abstractmethod
    def name(self) -> str:
        # Short identifier for the screen (e.g. "date", "cpu").
        ...

    def prefetch(self) -> None:
        # Called in a background thread before the screen is displayed.
        # Override to fetch slow data (e.g. HTTP requests) ahead of time.
        pass

    @abstractmethod
    def draw(self, draw, width: int, height: int) -> None:
        # Called once per display cycle.
        #   draw   — a Pillow ImageDraw object (the 128x64 pixel canvas)
        #   width  — display width in pixels  (128)
        #   height — display height in pixels (64)
        # Everything drawn here gets flushed to the OLED when the
        # `with canvas(device)` block in main.py exits.
        ...
