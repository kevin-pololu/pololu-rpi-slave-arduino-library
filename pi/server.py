#!/usr/bin/python

# Copyright Pololu Corporation.  For more information, see https://www.pololu.com/
from flask import Flask
from flask import render_template
from flask import redirect
from subprocess import call
app = Flask(__name__)
app.debug = True

from a_star import AStar
a_star = AStar()

from espeak import espeak
espeak.voice = 'en-us'
espeak.set_parameter(espeak.Parameter.Rate, 125)

import json

led0_state = False
led1_state = False
led2_state = False

music_enable = False

throttle_cmd = 0
steering_cmd = 0

@app.route("/")
def hello():
    return render_template("index.html")

@app.route("/status.json")
def status():
    buttons = a_star.read_buttons()
    analog = a_star.read_analog()
    battery_millivolts = a_star.read_battery_millivolts()
    data = {
        "buttons": buttons,
        "battery_millivolts": battery_millivolts,
        "analog": analog
    }
    return json.dumps(data)

@app.route("/drive/<throttle>,<steering>")
def drive(throttle, steering):
    global throttle_cmd
    global steering_cmd
    throttle_cmd = int(throttle)
    steering_cmd = int(steering)
    return ""

@app.route("/music/<int:enable>")
def music(enable):
    global music_enable
    music_enable = enable
    return ""

@app.route("/leds/<int:led0>,<int:led1>,<int:led2>")
def leds(led0, led1, led2):
    a_star.leds(led0, led1, led2)
    global led0_state
    global led1_state
    global led2_state
    led0_state = led0
    led1_state = led1
    led2_state = led2
    return ""

@app.route("/heartbeat/<int:state>")
def hearbeat(state):
    if state == 0:
      a_star.leds(led0_state, led1_state, led2_state)
    else:
        a_star.leds(not led0_state, not led1_state, not led2_state)
    return ""

@app.route("/play_notes/<notes>")
def play_notes(notes):
    a_star.play_notes(notes)
    return ""

@app.route("/speak/<text>")
def speak(text):
    espeak.synth(text)
    return ""

@app.route("/halt")
def halt():
    call(["bash", "-c", "(sleep 2; sudo halt)&"])
    return redirect("/shutting-down")

@app.route("/shutting-down")
def shutting_down():
    return "Shutting down in 2 seconds! You can remove power when the green LED stops flashing."

if __name__ == "__main__":
    app.run(host = "0.0.0.0")
