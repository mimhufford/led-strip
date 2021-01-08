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

####################
# HELPER FUNCTIONS #
####################
def lerp(a, b, t):
    return a + (b - a) * t

#########
# MODES #
#########
class Solid:
    def __init__(self):
        self.r = 0
        self.g = 0
        self.b = 0
        self.pulse = False
        self.pulse_direction = 1

    def set_colour(self, pulse, r, g, b):
        self.r = r
        self.g = g
        self.b = b
        self.pulse = pulse

    def tick(self):
        b = strip.getBrightness()
        if self.pulse:
            if b == 255:
                self.pulse_direction = -1
            elif b == 0:
                self.pulse_direction = 1
            strip.setBrightness(b + self.pulse_direction)
        else:
            b = min(255, b + 1)    
            strip.setBrightness(b)
 
        for i in range(strip.numPixels()):
            c = strip.getPixelColorRGB(i)
            c.r = int(lerp(c.r, self.r, DELAY))
            c.g = int(lerp(c.g, self.g, DELAY))
            c.b = int(lerp(c.b, self.b, DELAY))
            strip.setPixelColor(i, Color(c.r, c.g, c.b))
        strip.show()

##########################
# LED UPDATE TICK THREAD #
##########################
def tick_leds():
    pattern = [Solid()]
    while active:
        if data[0] == 0:
            pattern[0].set_colour(bool(data[1]), data[2], data[4], data[3])
            pattern[0].tick()
        sleep(DELAY)

############
# START UP #
############
strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
strip.begin()
active = True
DELAY = 1/30
data = [-1]
t = Thread(target=tick_leds)
t.start()
observer = Observer()
observer.schedule(OnData(), path='data')
observer.start()
t.join() # block until thread done
observer.stop()
print("stopped")
