import os
import sys
import json
import shutil
import random

os.mkdir("PreparedData")
for i in  os.listdir(os.path.join(sys.path[0],"Data")):
    path1 = os.path.join(sys.path[0], "Data", i)
    if(not os.path.isdir(path1)):
        continue
    path2 = os.path.join(path1,os.listdir(path1)[0])
    levelnumber = 0
    levelfilepath = ""
    for filename in os.listdir(path2):
        filepath = os.path.join(path2,filename)
        if(os.path.isfile(filepath)):
            if(filename.endswith(".osu")):
                print("删除：",path1)
                shutil.rmtree(path1)
                break
            elif(filename.endswith(".mc")):
                with open(filepath,"r",encoding="utf-8") as f:
                    mcfile = json.load(f)
                version = mcfile["meta"]["version"]
                level = version.split(" ")[-1]
                if(level.strip().startswith("Lv.")):
                    levelint = int(level.strip().replace("Lv.",""))
                    if(levelint >= 15 and levelint <= 30 and (abs(20 - levelnumber) > abs(20 - levelint))):
                        levelnumber = levelint
                        levelfilepath = filepath
                if(levelfilepath != ""):
                    dirpath = "PreparedData\\" + "%09d"%random.randint(0,999999999)
                    os.mkdir(dirpath)
                    shutil.move(levelfilepath,dirpath)
                    for file2 in os.listdir(path2):
                        filepath2 = os.path.join(path2,file2)
                        if(file2.endswith(".mc")):
                            os.remove(filepath2)
                        else:
                            shutil.move(filepath2,dirpath)

                    
