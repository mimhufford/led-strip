from threading import Thread
from time import sleep
from rpi_ws281x import *
from flask import Flask, render_template, redirect

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
class Off:
    def tick(self):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, Color(0,0,0))
        strip.show()
        print("off")
        return 1

class On:
    def tick(self):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, Color(255,255,255))
        strip.show()
        print("on")
        return 1

pattern = [Off(), On()]

while True:
    f = open('data', 'r')
    mode = int(f.read())
    f.close()
    if mode == -1:
        break
    sleep(pattern[mode].tick())
