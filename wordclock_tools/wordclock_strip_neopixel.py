from rpi_ws281x import Adafruit_NeoPixel, ws
from rpi_ws281x import Color as NeoPixelColor
import wordclock_tools.wordclock_colors as wcc
import logging

class wordclock_strip_neopixel(Adafruit_NeoPixel):

    def __init__(self, wcl):
        self._wiring = wcl
        self._rgb_frame_mapping = None
        try:
            super(wordclock_strip_neopixel, self).__init__(wcl.LED_COUNT, wcl.LED_PIN, wcl.LED_FREQ_HZ,
                                                wcl.LED_DMA, wcl.LED_INVERT, 255 , 0, ws.WS2811_STRIP_GRB)
        except:
            logging.error('Update deprecated external dependency rpi_ws281x. '
                    'For details see also https://github.com/jgarff/rpi_ws281x/blob/master/python/README.md')

    def setPixelColor(self, index, color):
        """
        Here we receive a wordclock color as input and convert it to a NeoPixelColor.
        """
        neopixelcolor = NeoPixelColor(color.r, color.g, color.b)
        super(wordclock_strip_neopixel, self).setPixelColor(index, neopixelcolor)

    def show_rgb_frame(self, frame):
        """Write a row-major RGB frame, including minute LEDs, to the strip."""
        if self._rgb_frame_mapping is None:
            wiring = self._wiring
            width, height = wiring.WCA_WIDTH, wiring.WCA_HEIGHT
            self._rgb_frame_mapping = [
                (wiring.getStripIndexFrom2D(x, y), (y * width + x) * 3)
                for x in range(width)
                for y in range(height)
            ] + [
                (wiring.mapMinutes(i + 1), (width * height + i) * 3)
                for i in range(4)
            ]

        set_pixel = self.getPixels().__setitem__
        for index, offset in self._rgb_frame_mapping:
            color = (frame[offset] << 16) | (frame[offset + 1] << 8) | frame[offset + 2]
            set_pixel(index, color)
        self.show()
