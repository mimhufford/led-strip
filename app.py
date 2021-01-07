from rpi_ws281x import *
from flask import Flask, render_template, redirect

app = Flask(__name__)

def write(data):
    with open('data', 'wb') as f:
        f.write(bytes(data))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/red')
def red():
    write([0, 255, 0, 0])
    return redirect('/')

@app.route('/green')
def green():
    write([0, 0, 255, 0])
    return redirect('/')

@app.route('/blue')
def blue():
    write([0, 0, 0, 255])
    return redirect('/')

@app.route('/white')
def white():
    write([0, 255, 255, 255])
    return redirect('/')

@app.route('/off')
def off():
    write([0, 0, 0, 0])
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
