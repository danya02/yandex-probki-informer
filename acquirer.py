#!/usr/bin/python
import pygame
import pygame.image
import os
import time
import json
import sys
import requests
import numpy
# global declarations
global conf
conf = json.load(open("./config.json"))
global color_table
color_table = {
    "green": pygame.Color(conf["colors"]["green"]["r"],
                          conf["colors"]["green"]["g"],
                          conf["colors"]["green"]["b"], 255),
    "yellow": pygame.Color(conf["colors"]["yellow"]["r"],
                           conf["colors"]["yellow"]["g"],
                           conf["colors"]["yellow"]["b"], 255),
    "red": pygame.Color(conf["colors"]["red"]["r"],
                        conf["colors"]["red"]["g"],
                        conf["colors"]["red"]["b"], 255)
}
global tmp_path
if os.name == "os2" or os.name == "posix":  # unix
    tmp_path = "/tmp"
elif os.name == "nt":  # windows
    tmp_path = os.path.join(os.path.splitdrive(sys.executable)[0],
                            "windows", "temp")
else:  # some other weird system like riscos
    raise NotImplementedError("Unknown system type: "+os.name)


def download(path, url):
    r = requests.get(url)
    with open(path, "wb") as code:
        code.write(r.content)


def get_pix(img, pix):
    global conf
    global color_table
    for i in color_table:
        if img.get_at(pix) == color_table[i]:
            return i
    raise ValueError("Unexpected pixel at position "+str(pix)+": "+str(
        img.get_at(pix)))


def get_arrows(img):
    global conf
    offset = 0
    try:
        while 1:
            get_pix(img, (conf["pix"][0]+offset, conf["pix"][1]))
            offset += 1
            if conf["debug"]:
                print(offset)
    except:
        pass
    return offset/pygame.image.load("arrow.gif").get_width()


def log():
    global conf
    global tmp_path
    download(tmp_path+os.sep+"img.png", conf["url"])
    out = open(tmp_path+os.sep+".last_traffic", "w")
    out.write(str(time.time())+":"+get_pix(
        pygame.image.load(tmp_path+os.sep+"img.png"), conf["pix"])+","+str(
            get_arrows(pygame.image.load(tmp_path+os.sep+"img.png"))))
    out.flush()
    out.close()


if __name__ == "__main__":
    log()
