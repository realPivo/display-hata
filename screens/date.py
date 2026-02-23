from datetime import datetime

from screens.base import Screen, load_font


class DateScreen(Screen):
    name = "date"
    live = True

    def __init__(self):
        self.font = load_font("FreePixel.ttf", 20)

    def draw(self, draw, width, height):
        now = datetime.now()

        lines = [
            now.strftime("%A"),  # "Friday"
            now.strftime("%d.%m.%Y"),  # "07.02.2026"
            now.strftime("%H:%M:%S"),  # "14:30:05"
        ]

        spacing = 6

        # --- Measure all lines ---
        bboxes = [draw.textbbox((0, 0), line, font=self.font) for line in lines]
        widths = [b[2] - b[0] for b in bboxes]
        heights = [b[3] - b[1] for b in bboxes]

        total_h = sum(heights) + spacing * (len(lines) - 1)
        y = (height - total_h) // 2

        # --- Draw lines ---
        for line, w, h in zip(lines, widths, heights):
            draw.text(
                ((width - w) // 2, y),
                line,
                fill="white",
                font=self.font,
            )
            y += h + spacing
