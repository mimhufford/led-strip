from rpi_ws281x import *
from flask import Flask, render_template, redirect

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/red')
def red():
    f = open('data', 'w')
    f.write('0 255 0 0')
    f.close()
    return redirect('/')

@app.route('/green')
def green():
    f = open('data', 'w')
    f.write('0 0 255 0')
    f.close()
    return redirect('/')

@app.route('/blue')
def blue():
    f = open('data', 'w')
    f.write('0 0 0 255')
    f.close()
    return redirect('/')

@app.route('/white')
def white():
    f = open('data', 'w')
    f.write('0 255 255 255')
    f.close()
    return redirect('/')

@app.route('/off')
def off():
    f = open('data', 'w')
    f.write('0 0 0 0')
    f.close()
    return redirect('/')

@app.route('/shutdown')
def shutdown():
    f = open('data', 'w')
    f.write('-1')
    f.close()
    return redirect('/')

@app.route('/theatre')
def theatre():
    return redirect('/')

@app.route('/rainbow')
def rainbow():
    return redirect('/')

app.run(debug=True, host='0.0.0.0')
