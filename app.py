from rpi_ws281x import *
from flask import Flask, render_template, redirect

app = Flask(__name__)

def write(data):
    with open('data', 'wb') as f:
        f.write(bytes(data))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/solid/<pulse>/<r>/<g>/<b>')
def solid(pulse, r, g, b):
    write([0, int(pulse), int(r), int(g), int(b)])
    return redirect('/')

@app.route('/sequence')
def sequence():
    write([1])
    return redirect('/')

@app.route('/gradient/<pulse>/<ar>/<ag>/<ab>/<br>/<bg>/<bb>')
def gradient(pulse, ar, ag, ab, br, bg, bb):
    write([2, int(pulse), int(ar), int(ag), int(ab), int(br), int(bg), int(bb)])
    return redirect('/')

@app.route('/shutdown')
def shutdown():
    write(b'quit')
    return redirect('/')

@app.route('/theatre')
def theatre():
    return redirect('/')

@app.route('/rainbow')
def rainbow():
    return redirect('/')

app.run(debug=True, host='0.0.0.0')
