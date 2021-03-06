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

@app.route('/sequence/<colours>')
def sequence(colours):
    data = [1]
    colours = colours.split('-')
    if len(colours) == 0:
        print('ERROR: No colours provided')
    elif len(colours) % 3 != 0:
        print('ERROR: Each colour requires 3 values')
    else:
        for c in colours:
            data.append(int(c))
        write(data)
    return redirect('/')

@app.route('/gradient/<pulse>/<rotate>/<colours>')
def gradient(pulse, rotate, colours):
    data = [2, int(pulse), int(rotate)]
    colours = colours.split('-')
    if len(colours) == 0:
        print('ERROR: No colours provided')
    elif len(colours) % 3 != 0:
        print('ERROR: Each colour requires 3 values')
    else:
        for c in colours:
            data.append(int(c))
        write(data)
    return redirect('/')

@app.route('/bouncer')
def bouncer():
    write([3])
    return redirect('/')

@app.route('/fireplace')
def fireplace():
    write([4])
    return redirect('/')

@app.route('/shutdown')
def shutdown():
    write(b'quit')
    return redirect('/')

@app.route('/rainbow')
def rainbow():
    return redirect('/')

app.run(debug=True, host='0.0.0.0')
