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
        continue
      elif file_data == b'quit':
        global active
        active = False
      else:
        data = [int(x) for x in file_data]
        global mode
        mode = data[0]
        if mode == 0:
            pattern[0].set_colour(bool(data[1]), data[2], data[4], data[3])
        elif mode == 1:
            pass # nothing to do until we pass in colour

      break # always end the loop, unless the file was locked and we continued

####################
# HELPER FUNCTIONS #
####################
# TODO: this needs improving once we have a better float based lerp
def approx_eq(a, b):
    return abs(a - b) < 30

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

class Sequence:
    def __init__(self):
        self.colours = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
        self.index = 0

    def set_sequence(self, colours):
        self.colours = colours
        self.index = 0

    def tick(self):
        # make sure brightness is on full
        b = strip.getBrightness()
        b = min(255, b + 1)
        strip.setBrightness(b)

        # keep pushing towards next colour
        move_to_next = True
        target = self.colours[self.index]
        for i in range(strip.numPixels()):
            c = strip.getPixelColorRGB(i)
            c.r = int(lerp(c.r, target[0], DELAY))
            c.g = int(lerp(c.g, target[1], DELAY))
            c.b = int(lerp(c.b, target[2], DELAY))
            strip.setPixelColor(i, Color(c.r, c.g, c.b))
            if not (approx_eq(c.r, target[0]) and approx_eq(c.g, target[1]) and approx_eq(c.b, target[2])):
                move_to_next = False

        # switch target colour
        if move_to_next:
            self.index = (self.index + 1) % len(self.colours)
        strip.show()


##########################
# LED UPDATE TICK THREAD #
##########################
def tick_leds():
    while active:
        if mode >= 0 and mode < len(pattern):
            pattern[mode].tick()
        sleep(DELAY)

############
# START UP #
############
strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
strip.begin()
pattern = [Solid(), Sequence()]
active = True
DELAY = 1/30
mode = -1
t = Thread(target=tick_leds)
t.start()
observer = Observer()
observer.schedule(OnData(), path='data')
observer.start()
t.join() # block until thread done
observer.stop()
print("stopped")
