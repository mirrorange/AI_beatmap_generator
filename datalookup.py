import os
import json

i3 = 0
for i1 in os.listdir("PreparedData"):
    i = 0
    for i2 in os.listdir(os.path.join("PreparedData",i1)):
        if(i2.endswith(".mc")):
            with open(os.path.join("PreparedData",i1,i2),"r",encoding="utf-8") as f:
                mcfile = json.load(f)
                print(mcfile["meta"]["version"])
            i = i + 1
    print(i)
    i3 = i3 + 1
print(i3)