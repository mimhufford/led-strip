from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from rpi_ws281x import *
from threading import Thread
from time import sleep

###################
# LED STRIP SETUP #
###################
LED_COUNT      = 15      # Number of LED pixels. NOTE: 100 is full strip
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
                if data[0] == 0: # Solid
                    mode = 1
                    pulse = bool(data[1])
                    colour = (data[2], data[4], data[3])
                    pattern[1].set_gradient(pulse, False, colour, colour)
                elif data[0] == 1: # Sequence
                    mode = 0
                elif data[0] == 2: # Gradient
                    mode = 1
                    pulse = bool(data[1])
                    rotate = bool(data[2])
                    data = data[3:]
                    colours = []
                    for i in range(0, len(data), 3): # group colours into tuples
                        colours.append((data[i], data[i+2], data[i+1]))
                    pattern[1].set_gradient(pulse, rotate, *colours)
            break # always end the loop, unless the file was locked and we continued

####################
# HELPER FUNCTIONS #
####################
def approx_eq(a, b):
    return abs(a - b) < 1

def colour_approx_eq(a, b):
    return approx_eq(a[0], b[0]) and approx_eq(a[1], b[1]) and approx_eq(a[2], b[2])

def lerp(a, b, t):
    return a + (b - a) * t

def colour_lerp(a, b, t):
    a[0] = lerp(a[0], b[0], t)
    a[1] = lerp(a[1], b[1], t)
    a[2] = lerp(a[2], b[2], t)

def float_strip():
    state = []
    for i in range(strip.numPixels()):
        c = strip.getPixelColorRGB(i)
        state.append([float(c.r), float(c.g), float(c.b)])
    return state

#########
# MODES #
#########
class Sequence:
    def __init__(self):
        self.state = float_strip()
        self.colours = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
        self.index = 0

    def set_sequence(self, colours):
        self.state = float_strip()
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
        for i, p in enumerate(self.state):
            colour_lerp(p, target, DELAY)
            strip.setPixelColor(i, Color(int(p[0]), int(p[1]), int(p[2])))
            if not colour_approx_eq(p, target):
                move_to_next = False

        # switch target colour
        if move_to_next:
            self.index = (self.index + 1) % len(self.colours)
        strip.show()

class Gradient:
    def __init__(self):
        self.pulse = False
        self.pulse_direction = 1
        self.rotate = False
        self.rotate_delay = 0.1
        self.rotate_time = 0.0
        self.state = []
        self.target = []
        self.set_gradient(False, False, (255.0, 0.0, 0.0), (0.0, 0.0, 255.0))

    def set_gradient(self, pulse, rotate, *colours):
        self.pulse = pulse
        self.rotate = rotate
        self.state = float_strip()
        self.target = []
        for i in range(LED_COUNT):
            c_index = int(i / LED_COUNT * (len(colours)-1))
            t = i / (LED_COUNT-1) * (len(colours)-1) - c_index
            a = colours[c_index]
            b = colours[c_index + 1]
            self.target.append((lerp(a[0], b[0], t), lerp(a[1], b[1], t), lerp(a[2], b[2], t)))

    def tick(self):
        # pulse brightness
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

        # rotate colours
        if self.rotate:
            self.rotate_time += DELAY
            while rotate_time >= rotate_delay:
                rotate_time -= rotate_delay
            self.state.insert(0, self.state.pop())
            self.target.insert(0, self.target.pop())

        # push towards target colour
        for i, p in enumerate(self.state):
            colour_lerp(p, self.target[i], DELAY)
            strip.setPixelColor(i, Color(int(p[0]), int(p[1]), int(p[2])))
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
pattern = [Sequence(), Gradient()]
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
