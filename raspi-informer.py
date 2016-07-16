#!/usr/bin/python3
from RPi import GPIO as gpio
import json
import os
import sys
import time


class RGBLED:
    def __setattr__(self, prop, val):
        object.__setattr__(self, prop, val)
        if prop == "color":
            self.set_color(val[0], val[1], val[2])
        if prop == "red":
            self._red(val)
        if prop == "green":
            self._green(val)
        if prop == "blue":
            self._blue(val)

    def __init__(self, r, g, b):
        import RPi.GPIO
        self._gpio = RPi.GPIO
        self._r_ = r
        self._g_ = g
        self._b_ = b
        self.color = [0, 0, 0]
        self._gpio.setmode(self._gpio.BOARD)
        self._gpio.setwarnings(False)
        for i in (self._r_, self._g_, self._b_):
            self._gpio.setup(i, self._gpio.OUT)
            self._gpio.output(i, 0)

    def _red(self, m):
        self.set_color(m, self.color[1], self.color[2])

    def _green(self, m):
        self.set_color(self.color[0], m, self.color[2])

    def _blue(self, m):
        self.set_color(self.color[0], self.color[1], m)

    def set_color(self, r, g, b):
        self._gpio.setmode(self._gpio.BOARD)
        self._gpio.setwarnings(False)
        for i, j in zip((self._r_, self._g_, self._b_), (r, g, b)):
            self._gpio.setup(i, self._gpio.OUT)
            self._gpio.output(i, j)

    def invert(self):
        a = [0, 0, 0]
        for i, j in zip(self.color, [0, 1, 2]):
            a[j] = not i
        self.color = a
        a = None

    def on(self):
        self.color = [1, 1, 1]

    def off(self):
        self.color = [0, 0, 0]

global conf
conf = json.load("./conf.json")
global led
try:
    led = RGBLED(conf["pins"]["red"], conf["pins"]["green"],
                 conf["pins"]["blue"])
except KeyError:
    print("Please configure the GPIO pins in config.json")
if os.name == "os2" or os.name == "posix":  # unix
    tmp_path = "/tmp"
elif os.name == "nt":  # windows
    tmp_path = os.path.join(os.path.splitdrive(sys.executable)[0],
                            "windows", "temp")
else:  # some other weird system like riscos
    raise NotImplementedError("Unknown system type: "+os.name)
while 1:
    led.on()
    os.popen("./acquirer.py").read()
    o = open(tmp_path+os.sep+".last_traffic").read().split(":")[1]
    led.color = [(1 if o == "red" else 0), (1 if o == "green" else 0),
                 (1 if o == "blue" else 0)]
    time.sleep(conf["update-sec"])  # not to spam the server and get us banned
