from rpi_ws281x import *
from flask import Flask, render_template, redirect

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/on')
def on():
    f = open('data', 'w')
    f.write('1')
    f.close()
    return redirect('/')

@app.route('/off')
def off():
    f = open('data', 'w')
    f.write('0')
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
