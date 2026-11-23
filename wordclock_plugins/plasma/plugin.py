import logging
import math
from time import monotonic


FRAME_PERIOD = 1 / 30
# The sum of the three waves stays in the range -3 to +3 radians.
PALETTE_SCALE = 85
PALETTE = tuple(
    (int((math.sin(step / PALETTE_SCALE) + 1) * 127.5),
     int((math.cos(step / PALETTE_SCALE) + 1) * 127.5))
    for step in range(-3 * PALETTE_SCALE, 3 * PALETTE_SCALE + 1)
)


class plugin:
    def __init__(self, config):
        self.name = "plasma"
        self.pretty_name = "RGB Plasma"
        self.description = "Displays an RGB plasma effect"

    def run(self, wcd, wci):
        width, height = wcd.get_wca_width(), wcd.get_wca_height()
        x_offsets = [x * math.tau / width for x in range(width)]
        y_offsets = [y * math.tau / height for y in range(height)]
        diagonal_step = 0.6 * math.tau / max(width, height)
        diagonal_offsets = [i * diagonal_step for i in range(width + height - 1)]
        # The four trailing RGB pixels are the unlit minute LEDs.
        frame = bytearray((width * height + 4) * 3)

        started_at = deadline = monotonic()
        frames = 0
        while True:
            elapsed = monotonic() - started_at
            render_frame(frame, elapsed, x_offsets, y_offsets, diagonal_offsets)
            wcd.show_rgb_frame(frame)
            frames += 1

            now = monotonic()
            deadline = max(deadline + FRAME_PERIOD, now)
            if wci.waitForEvent(deadline - now) >= 0:
                elapsed = monotonic() - started_at
                logging.info("Plasma: %d frames in %.2f s (%.2f fps)",
                             frames, elapsed, frames / elapsed)
                return


def render_frame(frame, elapsed, x_offsets, y_offsets, diagonal_offsets):
    """Fill the matrix with overlapping waves that drift at different speeds."""
    sin = math.sin
    x_phase = 0.9 * elapsed + 0.45 * sin(0.7 * elapsed)
    y_phase = -0.68 * elapsed + 0.4 * sin(0.5 * elapsed)
    diagonal_phase = 0.55 * elapsed
    x_wave = [sin(x_phase + offset) for offset in x_offsets]
    y_wave = [sin(y_phase + offset) for offset in y_offsets]
    diagonal_wave = [0.75 * sin(diagonal_phase + offset) for offset in diagonal_offsets]

    pixel = 0
    for y, vertical in enumerate(y_wave):
        for x, horizontal in enumerate(x_wave):
            wave = horizontal + vertical + diagonal_wave[x + y]
            red, green_blue = PALETTE[int((wave + 3) * PALETTE_SCALE)]
            frame[pixel] = red
            frame[pixel + 1] = green_blue
            frame[pixel + 2] = green_blue
            pixel += 3
