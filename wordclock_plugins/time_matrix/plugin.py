# Authored by Markus E.
# https://github.com/mrksngl

import datetime
import logging
import random
from time import monotonic

import wordclock_tools.wordclock_colors as wcc


FRAME_PERIOD = 1 / 30
RAIN_SPEED = 10  # rows per second


class plugin:
    def __init__(self, config):
        self.show_scroll_text = True
        self.name = 'time_matrix'
        self.pretty_name = 'Matrix with time'
        self.description = 'There is no spoon?'
        self.purist = config.getboolean('plugin_time_default', 'purist')
        self.threshold = 0.9
        self.colors = [(0, int(255.0 / 10 * i), 0) for i in range(8)]
        self.colors.extend([(50, 204, 30), (50, 230, 30), (80, 255, 60)])

    def update_background(self, background, wcd, width, height, clock_time):
        background[:] = bytes(len(background))
        for index in wcd.taw.get_time(clock_time, self.purist):
            offset = index * 3
            background[offset:offset + 3] = b'\xff\xff\xff'
        for index in range(clock_time.minute % 5):
            offset = (width * height + index) * 3
            background[offset:offset + 3] = b'\xff\xff\xff'

    def run(self, wcd, wci):
        width, height = wcd.get_wca_width(), wcd.get_wca_height()
        rain = [None] * width
        background = bytearray((width * height + 4) * 3)
        previous_minute = None
        started = previous = deadline = monotonic()
        frames = 0

        while True:
            if self.show_scroll_text and wcc.scrollenable:
                try:
                    if datetime.datetime.now() > wcc.scrolldatetime:
                        wcd.showText(wcc.scrolltext)
                        wcc.scrolldatetime += datetime.timedelta(seconds=wcc.scrollrepeat)
                except Exception:
                    logging.exception('Unable to display scheduled scroll text')

            now = monotonic()
            elapsed = min(now - previous, 0.1)
            previous = now
            if not self.show_scroll_text or not wcc.scrollactive:
                clock_time = datetime.datetime.now()
                minute = (clock_time.year, clock_time.month, clock_time.day,
                          clock_time.hour, clock_time.minute)
                if minute != previous_minute:
                    self.update_background(background, wcd, width, height, clock_time)
                    previous_minute = minute

                frame = bytearray(background)
                chance = 1 - self.threshold ** (elapsed / 0.1)
                for x, position in enumerate(rain):
                    if position is None:
                        if random.random() < chance:
                            rain[x] = 0.0
                        continue

                    for y in range(max(0, int(position) - 10), min(height - 1, int(position)) + 1):
                        level = y - position + 10
                        if 0 <= level < 10:
                            lower = int(level)
                            fraction = level - lower
                            color = bytes(int(a + (b - a) * fraction) for a, b in
                                          zip(self.colors[lower], self.colors[lower + 1]))
                        elif 10 <= level <= 11:
                            color = bytes(int(c * (11 - level)) for c in self.colors[10])
                        else:
                            continue
                        offset = (y * width + x) * 3
                        frame[offset:offset + 3] = color

                    position += RAIN_SPEED * elapsed
                    rain[x] = None if position >= height + 10 else position

                wcd.show_rgb_frame(frame)
                frames += 1

            now = monotonic()
            deadline = max(deadline + FRAME_PERIOD, now)
            event = wci.waitForEvent(deadline - now)
            if event in (wci.EVENT_BUTTON_RETURN, wci.EVENT_EXIT_PLUGIN,
                         wci.EVENT_NEXT_PLUGIN_REQUESTED):
                duration = monotonic() - started
                logging.info('%s: %d frames in %.2f s (%.2f fps)',
                             self.name, frames, duration, frames / duration if duration else 0)
                return
            if event == wci.EVENT_BUTTON_LEFT:
                self.threshold = min(0.95, self.threshold + 0.05)
            elif event == wci.EVENT_BUTTON_RIGHT:
                self.threshold = max(0.7, self.threshold - 0.05)
