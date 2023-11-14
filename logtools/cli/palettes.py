import re
import random
from typing import Mapping

from colored import Fore

_SIMPLE_PALETTE_RGB = [
    (228, 26, 28),  # red
    (55, 126, 184),  # blue
    (77, 175, 74),  # green
    (152, 78, 163),  # purple
    (255, 127, 0),  # orange
    (255, 255, 51),  # yellow
    (166, 86, 40),  # brown
    (247, 129, 191),  # pink
    (153, 153, 153),  # grey
]


def rgb_to_ansi(red, green, blue):
    return f'\x1b[38;2;{red};{green};{blue}m'


SIMPLE_PALETTE = [rgb_to_ansi(*rgb) for rgb in _SIMPLE_PALETTE_RGB]

COLORED_PALETTE = [getattr(Fore, color) for color in Fore._COLORS.keys()
                   if not re.match(r'dark|deep|black', color)]

# Randomize, but deterministically
shuffler = random.Random(x=1234)
shuffler.shuffle(COLORED_PALETTE)

FULL_PALETTE = SIMPLE_PALETTE + COLORED_PALETTE


class ColorMap(Mapping[str, str]):
    def __init__(self):
        self._colors = {}
        self._next_color = 0

    def __getitem__(self, key: str) -> str:
        if key not in self._colors:
            self._colors[key] = FULL_PALETTE[self._next_color]
            self._next_color += 1
        return self._colors[key]

    def __len__(self):
        return len(self._colors)

    def __iter__(self):
        return self._colors.__iter__()
