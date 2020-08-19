import os
import json

for i1 in os.listdir("PreparedData"):
    i3 = 0
    if(not os.path.isdir(os.path.join("PreparedData",i1))):
        continue
    for i2 in os.listdir(os.path.join("PreparedData",i1)):
        if(i2.endswith(".mc")):
            continue
            #with open(os.path.join("PreparedData",i1,i2),"r",encoding="utf-8") as f:
                #mcfile = json.load(f)
        elif(i2.endswith(".ogg") or i2.endswith(".mp3")):
            i3 = i3 + 1
        elif(i2.endswith(".jpg") or i2.endswith(".png")):
            print("删除：",os.path.join("PreparedData",i1,i2))
            os.remove(os.path.join("PreparedData",i1,i2))
        else:
            print(os.path.join("PreparedData",i1,i2))
    if(i3 != 1):
        print(i3)
        print(os.path.join("PreparedData",i1))