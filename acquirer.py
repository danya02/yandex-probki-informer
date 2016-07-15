#!/usr/bin/python
import pygame
import pygame.image
import os
import time
import json
# global declarations
global conf
conf = json.load(open("./config.json"))
global color_table
color_table = {
    "green": pygame.Color(conf["colors"]["green"]),
    "yellow": pygame.Color(conf["colors"]["yellow"]),
    "red": pygame.Color(conf["colors"]["red"])
}


def download(path, url):
    os.popen("wget -O "+path+" "+url+" 2>/dev/null").read()  # halting call


def get_pix(path, pix):
    global conf
    download(path, conf["url"])
    img = pygame.image.load(path)
    global color_table
    for i in color_table:
        if img.get_at(pix) == color_table[i]:
            return i
    raise ValueError("Unexpected pixel at position "+str(pix)+": "+str(
        img.get_at(pix)))


def log():
    global conf
    out = open("/tmp/.last_traffic", "w")
    out.write(str(time.time())+":"+get_pix("/tmp/img.png", conf["pix"]))
    out.flush()
    out.close()


if __name__ == "__main__":
    log()
