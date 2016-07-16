#!/usr/bin/python3
from RPi import GPIO as gpio
import json
import os
import sys
import time
import random
import threading


global conf
conf = json.load("./conf.json")
conf["debug"] = True
for i in sys.argv:
    try:
        conf[i.split("=")[0]] = eval(i.split("=")[1])
    except:
        pass
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
    global status
    global leds
    global conf
    all_seq = []
    for i in range(0, 7):
        all_seq = all_seq+[int(bin(i)[0]),
                           int(bin(i)[1]),
                           int(bin(i)[2])]
    led_color = [0, 0, 0]
    while 1:
        if status == 0:
            led_color = leds
        elif status == 1:
            led_color = [conf["pins"]["common-cathode"]]*3
        elif status == -1:
            led_color = random.choice(all_seq)
        if conf["debug"]:
            if status == -1:
                print("STATUS: borked ", end="")
            elif status == 0:
                print("STATUS: enabled ", end="")
            elif status == 1:
                print("STATUS: updating ", end="")
            print(str(led_color))
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
    except:
        status = -1  # meaning the system has been borked
    time.sleep(conf["update-sec"]  # not to spam the server and get us banned
               if status > -1 else 5)  # in case we've run into a disconnect
