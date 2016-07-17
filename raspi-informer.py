#!/usr/bin/python3
from RPi import GPIO as gpio
import json
import os
import sys
import time
import random
import threading


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
conf = json.load(open("./config.json"))
global led
try:
    led = RGBLED(conf["pins"]["red"], conf["pins"]["yellow"],
                 conf["pins"]["green"])
except KeyError:
    os.execv("./gpio-setup.py", [])
if os.name == "os2" or os.name == "posix":  # unix
    tmp_path = "/tmp"
elif os.name == "nt":  # windows
    tmp_path = os.path.join(os.path.splitdrive(sys.executable)[0],
                            "windows", "temp")
else:  # some other weird system like riscos
    raise NotImplementedError("Unknown system type: "+os.name)
global status
status = 1
global leds
leds = [not conf["pins"]["common-cathode"],
        not conf["pins"]["common-cathode"],
        not conf["pins"]["common-cathode"]]


def blinker():
    global led
    global status
    global leds
    global conf
    all_seq = []
    for i in range(0, 7):
        j = bin(i)[2:]
        j = "00"+j if len(j) == 1 else ("0"+j if len(j) == 2 else j)
        all_seq = all_seq+[int(j[0]),
                           int(j[1]),
                           int(j[2])]
    while 1:
        if status == 0:
            led.color = leds
        elif status == 1:
            led.color = [conf["pins"]["common-cathode"]]*3
        elif status == -1:
            led.color = random.choice(all_seq)
        if conf["debug"]:
            if status == -1:
                print("STATUS: borked ", end="")
            elif status == 0:
                print("STATUS: enabled ", end="")
            elif status == 1:
                print("STATUS: updating ", end="")
            print(str(led.color))
        time.sleep(0.5)  # not to allow the CPU to overhet

blinkenlights = threading.Thread(target=blinker, name="blinkenlights")
blinkenlights.daemon = True
blinkenlights.start()

while 1:
    status = 1
    try:
        os.popen("./acquirer.py").read()
        o = open(tmp_path+os.sep+".last_traffic").read().split(":")[1]
        leds = [(conf["pins"]["common-cathode"] if o == "red" else
                 (not conf["pins"]["common-cathode"])),
                (conf["pins"]["common-cathode"] if o == "yellow" else
                 (not conf["pins"]["common-cathode"])),
                (conf["pins"]["common-cathode"] if o == "green" else
                 (not conf["pins"]["common-cathode"]))]
        status = 0
    except:
        status = -1  # meaning the system has been borked
    time.sleep(conf["update-sec"]  # not to spam the server and get us banned
               if status > -1 else 5)  # in case we've run into a disconnect
