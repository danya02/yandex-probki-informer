#!/usr/bin/python
import pygame
import pygame.image
import os
import time
import json
import sys
import requests
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
    global tmp_path
    out = open(tmp_path+os.sep+".last_traffic", "w")
    out.write(str(time.time())+":"+get_pix(tmp_path+os.sep+"img.png",
                                           conf["pix"]))
    out.flush()
    out.close()


if __name__ == "__main__":
    log()
