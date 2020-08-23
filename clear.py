import os
import shutil

for i in os.listdir():
    if(os.path.isfile(i) and i.endswith(".mc") or i.endswith(".ogg") or i.endswith(".mp3") or i.endswith(".mcz")):
        os.remove(i)
        