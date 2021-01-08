from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from rpi_ws281x import *
from threading import Thread
from time import sleep

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

##################################
# CALLBACK FOR FILE CHANGE EVENT #
##################################
class OnData(FileSystemEventHandler):
  def on_modified(self, event):
    while True:
      file_data = str()
      with open('data', 'rb') as f:
        file_data = f.read()
      if len(file_data) == 0:
        print('BLOCKED, TRYING AGAIN...')
        sleep(0.01)
      elif file_data == b'quit':
        global active
        active = False
        break
      else:
        global data
        data = [int(x) for x in file_data]
        break

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
                c.r += 1 if c.r < self.r else -1 if c.r > self.r else 0
                c.g += 1 if c.g < self.g else -1 if c.g > self.g else 0
                c.b += 1 if c.b < self.b else -1 if c.b > self.b else 0
                strip.setPixelColor(i, Color(c.r,c.g,c.b))
        strip.show()
        return 1/1000

##########################
# LED UPDATE TICK THREAD #
##########################
def tick_leds():
    pattern = [Solid()]
    while active:
        if data[0] == 0:
            pattern[0].set_colour(data[1], data[3], data[2])
            sleep(pattern[0].tick())
        else:
            sleep(0.01)

############
# START UP #
############
strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
strip.begin()
active = True
data = [-1]
t = Thread(target=tick_leds)
t.start()
observer = Observer()
observer.schedule(OnData(), path='data')
observer.start()
t.join() # block until thread done
observer.stop()
print("stopped")
