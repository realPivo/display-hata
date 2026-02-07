import psutil

from screens.base import Screen, load_font


class CpuScreen(Screen):
    name = "cpu"

    def __init__(self):
        self.font = load_font("FreePixel.ttf", 16)

    def draw(self, draw, width, height):
        label = "CPU"
        # cpu_percent(interval=None) returns the CPU usage since the last call,
        # without blocking. On the very first call it returns 0.0 (no previous
        # sample), but after that it reflects real usage between cycles.
        pct = f"{psutil.cpu_percent(interval=None):.0f}%"  # e.g. "23%"

        # Measure each line's pixel size (same bbox technique as DateScreen —
        # see date.py for a detailed explanation of textbbox).
        label_bbox = draw.textbbox((0, 0), label, font=self.font)
        pct_bbox = draw.textbbox((0, 0), pct, font=self.font)

        label_w = label_bbox[2] - label_bbox[0]
        pct_w = pct_bbox[2] - pct_bbox[0]
        label_h = label_bbox[3] - label_bbox[1]
        pct_h = pct_bbox[3] - pct_bbox[1]

        # Center both lines vertically and horizontally (same approach as DateScreen).
        spacing = 4
        total_h = label_h + spacing + pct_h
        y_offset = (height - total_h) // 2

        draw.text(((width - label_w) // 2, y_offset), label, fill="white", font=self.font)
        draw.text(((width - pct_w) // 2, y_offset + label_h + spacing), pct, fill="white", font=self.font)
