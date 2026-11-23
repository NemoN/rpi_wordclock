import logging
import os
from time import monotonic

import wordclock_tools.wordclock_colors as wcc


FRAME_PERIOD = 1 / 30
# The original advanced one color step every 50 ms, plus rendering time.
COLOR_SPEED = 10


class plugin:
    def __init__(self, config):
        self.name = os.path.dirname(__file__).split('/')[-1]
        self.pretty_name = 'Rainbow'
        self.description = 'Displays a nice rainbow'
        self.palette = [(color.r, color.g, color.b)
                        for color in (self.wheel(i) for i in range(256))]

    def run(self, wcd, wci):
        width, height = wcd.get_wca_width(), wcd.get_wca_height()
        offsets = [x * y for y in range(height) for x in range(width)]
        frame = bytearray((width * height + 4) * 3)
        started = deadline = monotonic()
        frames = 0
        while True:
            position = (monotonic() - started) * COLOR_SPEED
            base = int(position)
            fraction = position - base
            for index, offset in enumerate(offsets):
                first = self.palette[(offset + base) & 255]
                second = self.palette[(offset + base + 1) & 255]
                for channel in range(3):
                    frame[index * 3 + channel] = int(
                        first[channel] + (second[channel] - first[channel]) * fraction)
            wcd.show_rgb_frame(frame)
            frames += 1
            now = monotonic()
            deadline = max(deadline + FRAME_PERIOD, now)
            if wci.waitForEvent(deadline - now) >= 0:
                duration = monotonic() - started
                logging.info('rainbow: %d frames in %.2f s (%.2f fps)',
                             frames, duration, frames / duration if duration else 0)
                return

    def wheel(self, pos):
        if pos < 85:
            return wcc.Color(pos * 3, 255 - pos * 3, 0)
        if pos < 170:
            pos -= 85
            return wcc.Color(255 - pos * 3, 0, pos * 3)
        pos -= 170
        return wcc.Color(0, pos * 3, 255 - pos * 3)
