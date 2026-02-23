import random

from screens.base import Screen, load_font

ASCII_LINES = [
    "        _,--',   _._.--._____ ",
    " .--.--';_'-.', \"T_      _.,-'",
    ".'--'T  _T'    {`'T;_ T-.>.'  ",
    "      '-:_      )  / `' '=.   ",
    "        ) >     {_/,     /~)  ",
    "        |/               `^ .'",
]

BLINK_COORDINATES = [
    (1, 17),
    (2, 5),
    (2, 9),
    (2, 14),
    (2, 18),
    (2, 22),
]


class MapScreen(Screen):
    name = "map"
    live = True
    interval = 10.0  # fallback; overwritten by config "duration" at runtime

    def __init__(self):
        self.font = load_font("IBMPlexMono-Regular.ttf", 6)
        self._blink: dict[tuple[int, int], bool] = {
            coord: random.random() > 0.5 for coord in BLINK_COORDINATES
        }
        self._blink_set = set(BLINK_COORDINATES)
        self._char_w: int | None = None
        self._char_h: int | None = None

    def _char_dims(self, draw):
        if self._char_w is None:
            bbox = draw.textbbox((0, 0), "X", font=self.font)
            self._char_w = bbox[2] - bbox[0]
            ascent, descent = self.font.getmetrics()
            self._char_h = ascent + descent
        return self._char_w, self._char_h

    def draw(self, draw, width: int, height: int) -> None:
        char_w, char_h = self._char_dims(draw)

        # Toggle one random blink coordinate each frame (called every 0.5s)
        coord = random.choice(BLINK_COORDINATES)
        self._blink[coord] = not self._blink[coord]

        total_h = char_h * len(ASCII_LINES)
        y_start = (height - total_h) // 2

        for row, line in enumerate(ASCII_LINES):
            y = y_start + row * char_h
            for col, char in enumerate(line):
                rc = (row, col)
                if rc in self._blink_set and not self._blink[rc]:
                    continue  # invisible (blink off)
                draw.text((col * char_w, y), char, fill="white", font=self.font)
