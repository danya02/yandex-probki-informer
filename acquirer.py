#!/usr/bin/python
import pygame
import pygame.image
import os
import time
# global declarations
global color_table
color_table = {
    "green": pygame.Color(0, 154, 34, 255),
    "yellow": pygame.Color(255, 102, 0, 255),
    "red": pygame.Color(255, 0, 0, 255)
}


def download(path="/tmp/img.png",
             url="http://info.maps.yandex.net/traffic/moscow/tends_200.png"):
    os.popen("wget -O "+path+" "+url).read()


def get_pix(path="/tmp/img.png", pix=(46, 67)):
    download()
    img = pygame.image.load(path)
    global color_table
    for i in color_table:
        if img.get_at(pix) == color_table[i]:
            return i
    raise ValueError("Unexpected pixel at position "+str(pix)+": "+str(
        img.get_at(pix)))


def log():
    out = open("/tmp/.last_traffic", "w")
    out.write(str(time.time())+":"+get_pix())
    out.flush()
    out.close()


if __name__ == "__main__":
    log()
