############################################################
############################################################
############################################################
# TODO: Flask does it's own thread stuff so this is fucked #
############################################################
############################################################
############################################################

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

###########
# GLOBALS #
###########
mode = 0
done = False
pattern = [Off(), On()]

###############
# FLASK SETUP #
###############
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/on')
def on():
    global mode
    mode = 1
    return redirect('/')

@app.route('/off')
def off():
    global mode
    mode = 0
    return redirect('/')

@app.route('/shutdown')
def shutdown():
    global done
    done = True
    return redirect('/')

@app.route('/theatre')
def theatre():
    return redirect('/')

@app.route('/rainbow')
def rainbow():
    return redirect('/')

app.run(debug=True, host='0.0.0.0')

##########################
# LED STRIP THREAD SETUP #
##########################
def fn():
    while not done:
        sleep(pattern[mode].tick())

t = Thread(target=fn)
t.start()
