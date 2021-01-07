from time import sleep
from rpi_ws281x import *

###################
# LED STRIP SETUP #
###################
LED_COUNT      = 50      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53

strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
strip.begin()

#########
# MODES #
#########
class Solid:
    def __init__(self):
        self.done = False
        self.r = 0
        self.g = 0
        self.b = 0

    def set_colour(self, r, g, b):
        if self.r != r or self.g != g or self.b != b:
            self.done = False
        self.r = r
        self.g = g
        self.b = b

    def tick(self):
        if self.done:
            return 0.01
        self.done = True
        for i in range(strip.numPixels()):
            c = strip.getPixelColorRGB(i)
            if c.r != self.r or c.g != self.g or c.b != self.b:
                self.done = False
                c.r += 1 if c.r < self.r else -1 if cr > self.r else 0
                c.g += 1 if c.g < self.g else -1 if cg > self.g else 0
                c.b += 1 if c.b < self.b else -1 if cb > self.b else 0
                strip.setPixelColor(i, Color(c.r,c.g,c.b))
        strip.show()
        return 1/1000

pattern = [Solid()]

while True:
    f = open('data', 'r')
    data = f.read()
    f.close()
    if data == '':
        continue

    data = [int(x) for x in data.split()]

    mode = data[0]

    if mode == -1:
        break
    elif mode == 0:
        pattern[mode].set_colour(data[1], data[3], data[2])

    sleep(pattern[mode].tick())