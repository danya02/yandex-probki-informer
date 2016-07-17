#!/usr/bin/python3
import RPi.GPIO as gpio
import threading
import json
gpio.setmode(gpio.BOARD)
gpio.setwarnings(False)
old_pi = True
try:
    gpio.setup(27, gpio.OUT)
    old_pi = False
except:
    pass
gpios_old = [3, 5, 7, 8, 10, 11, 12, 13, 15, 16, 18, 19, 21, 22, 23, 24, 26]
gpios_new = gpios_old+[27, 28, 29, 31, 32, 33, 35, 36, 37, 38, 40]

for i in gpios_old if old_pi else gpios_new:
    gpio.setup(i, gpio.OUT)
    gpio.output(i, 0)
global gpio_list
gpio_list = gpios_old if old_pi else gpios_new
global running
running = True


def blinker():
    import time
    global gpio_list
    global running
    status = False
    while running:
        for i in gpios_old if old_pi else gpios_new:
            gpio.output(i, status)
        status = not status
    time.sleep(0.5)
blinker_thread = threading.Thread(target=blinker, name="blinkenlights")
blinker_thread.daemon = True
blinker_thread.start()

print("Your GPIO configuration is not completed. Please complete it.")
old_layout = """
    +---+---+
1   |3V3|5V | 2
    |---|---|
3   |%s|5V | 4
    |---|---|
5   |%s|GND| 6
    |---|---|
7   |%s|%s| 8
    |---|---|
9   |GND|%s| 10
    |---|---|
11  |%s|%s| 12
    |---|---|
13  |%s|GND| 14
    |---|---|
15  |%s|%s| 16
    |---|---|
17  |3V3|%s| 18
    |---|---|
19  |%s|GND| 20
    |---|---|
21  |%s|%s| 22
    |---|---|
23  |%s|%s| 24
    |---|---|
25  |GND|%s| 26
    +---+---+"""
new_layout = """
        +---+---+
    1   |3V3|5V | 2
        |---|---|
    3   |%s|5V | 4
        |---|---|
    5   |%s|GND| 6
        |---|---|
    7   |%s|%s| 8
        |---|---|
    9   |GND|%s| 10
        |---|---|
    11  |%s|%s| 12
        |---|---|
    13  |%s|GND| 14
        |---|---|
    15  |%s|%s| 16
        |---|---|
    17  |3V3|%s| 18
        |---|---|
    19  |%s|GND| 20
        |---|---|
    21  |%s|%s| 22
        |---|---|
    23  |%s|%s| 24
        |---|---|
    25  |GND|%s| 26
        |---|---|
    27  |%s|%s| 28
        |---|---|
    29  |%s|GND| 30
        |---|---|
    31  |%s|%s| 32
        |---|---|
    33  |%s|GND| 34
        |---|---|
    35  |%s|%s| 36
        |---|---|
    37  |%s|%s| 38
        |---|---|
    39  |GND|%s| 40
        +---+---+"""
gpio_labels = ["   "]*len(gpios_old if old_pi else gpios_new)
gpios_local = gpios_old if old_pi else gpios_new
layout = old_layout if old_pi else new_layout
r_set = False
y_set = False
g_set = False
out = [0, 0, 0]
while not r_set:
    print(layout % gpio_labels)
    i = input("Please select RED pin: ")
    try:
        i = int(i)
    except:
        i = 0
    if i not in gpios_local:
        print("Invalid pin, try again.")
    elif i in out:
        print("Pin already selected, try again.")
    else:
        gpio_labels[gpios_local.index(i)] = " R "
        print(layout % gpio_labels)
        last_gpio_list = gpio_list
        gpio_list = [i]
        if input("Is this pin correct? (y/N) ").upper() == "Y":
            out[0] = i
            r_set = True
        else:
            gpio_labels[gpios_local.index(i)] = "   "
        gpio_list = last_gpio_list
while not y_set:
    print(layout % gpio_labels)
    i = input("Please select YELLOW pin: ")
    try:
        i = int(i)
    except:
        i = 0
    if i not in gpios_local:
        print("Invalid pin, try again.")
    elif i in out:
        print("Pin already selected, try again.")
    else:
        gpio_labels[gpios_local.index(i)] = " Y "
        print(layout % gpio_labels)
        last_gpio_list = gpio_list
        gpio_list = [i]
        if input("Is this pin correct? (y/N) ").upper() == "Y":
            out[1] = i
            r_set = True
        else:
            gpio_labels[gpios_local.index(i)] = "   "
        gpio_list = last_gpio_list
while not g_set:
    print(layout % gpio_labels)
    i = input("Please select GREEN pin: ")
    try:
        i = int(i)
    except:
        i = 0
    if i not in gpios_local:
        print("Invalid pin, try again.")
    elif i in out:
        print("Pin already selected, try again.")
    else:
        gpio_labels[gpios_local.index(i)] = " G "
        print(layout % gpio_labels)
        last_gpio_list = gpio_list
        gpio_list = [i]
        if input("Is this pin correct? (y/N) ").upper() == "Y":
            out[2] = i
            r_set = True
        else:
            gpio_labels[gpios_local.index(i)] = "   "
        gpio_list = last_gpio_list
running = False
for i in gpios_old if old_pi else gpios_new:
    gpio.output(i, 1)
answered = False
while not answered:
    all_on = input("Are all LEDs on? (y/n)").upper()
    if all_on not in ["Y", "N"]:
        print("Please answer `Y` or `N`.")
    else:
        answered = True
if not all_on == "Y":
    answered = False
    while not answered:
        any_on = input("Are any LEDs on? (y/n)").upper()
        if any_on not in ["Y", "N"]:
            print("Please answer `Y` or `N`.")
        else:
            answered = True
    if any_on == "Y":
        print("""Your configuration is incorrect. Please set up such a
configuration that either the LEDs have a common cathode or a common anode.""")
        raise SystemExit(0)
    else:
        common_cathode = False
else:
    common_cathode = True
conf = json.load(open("config.json"))
conf["pins"]["red"] = out[0]
conf["pins"]["yellow"] = out[1]
conf["pins"]["green"] = out[2]
conf["pins"]["common-cathode"] = common_cathode
json.dump(open("config.json", "w"))
