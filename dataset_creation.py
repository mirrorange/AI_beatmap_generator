import zipfile
import os
import json
import librosa
import numpy as np

def load_audio(audio_file):
    x , sr = librosa.load(audio_file, sr=20000)
    return x, sr

def hcf(x, y):
   """该函数返回两个数的最大公约数"""
 
   # 获取最小值
   if x > y:
       smaller = y
   else:
       smaller = x
   _hcf = 1
   for i in range(1,smaller + 1):
       if((x % i == 0) and (y % i == 0)):
           _hcf = i
 
   return _hcf

def get_audio_features(x, sr, bpm, position, offset):
    one_beat = 60 / bpm
    beat = position * one_beat / 4 - offset/1000
    start = beat
    end = start + one_beat / 8
    end2 = start + one_beat / 4
    if start < 0:
        start = 0
    start_index = int(sr * start)
    end_index = int(sr * end)
    end_index2 = int(sr * end2)
    features = []
    mfcc1 = librosa.feature.mfcc(y=x[start_index:end_index], sr=sr, n_mfcc=32)
    mfcc2 = librosa.feature.mfcc(y=x[end_index:end_index2], sr=sr, n_mfcc=32)
    features += [float(np.mean(e)) for e in mfcc1]
    features += [float(np.mean(e)) for e in mfcc2]
    return features

def get_columns_list(notes):
    columns_list = []
    columns = {
        0: {},
        1: {},
        2: {},
        3: {}
    }
    for note in notes:
        if 'column' in note:
            beat = note['beat'][0]
            sub_beat = note['beat'][1]
            split_count = note['beat'][2]
            if split_count == 8:
                if (len(columns[0]) != 0) and (len(columns[1]) != 0) \
                    and (len(columns[2]) != 0)and (len(columns[3]) != 0):
                    columns_list.append(columns)
                    columns = {0: {}, 1: {}, 2: {}, 3: {}}
                continue
            if split_count != 4:
                if sub_beat == 0:
                    split_count = 4
                else:
                    _hcf = hcf(sub_beat, split_count)
                    sub_beat = int(sub_beat / _hcf)
                    split_count = int(split_count / _hcf)
                if split_count == 2:
                    sub_beat *= 2
                    split_count *= 2
                if split_count == 1:
                    sub_beat *= 4
                    split_count *= 4
                elif split_count != 4:
                    if (len(columns[0]) != 0) and (len(columns[1]) != 0) \
                        and (len(columns[2]) != 0)and (len(columns[3]) != 0):
                        columns_list.append(columns)
                        columns = {0: {}, 1: {}, 2: {}, 3: {}}
                    continue

            position = beat * 4 + sub_beat
            which_col = note["column"]
            if(which_col >= 4):
                continue
            if "endbeat" in note:
                end_position = note["endbeat"][0] * 4 + int(note["endbeat"][1] / note["endbeat"][2] * 4)
                if end_position == position:
                    columns[which_col][position] = 1
                else:
                    for i in range(position, end_position+1):
                        columns[which_col][i] = 2
            else:
                columns[which_col][position] = 1
    return columns_list

def get_columns_min_max(columns):
    _min = 10000000000
    _max = 0
    for col in columns.keys():
        column = columns[col]
        if max(column.keys()) > _max:
            _max = max(column.keys())

        if min(column.keys()) < _min:
            _min = min(column.keys())
    return _min, _max

def get_one_data(start, end, columns, bpm, x_, sr, offset):
    # 判断是否有beat
    x0 = []
    y0 = []
    
    # 判断note的键型
    x1 = []
    y1 = []
    
    
     # 判断是否有long_note
    x2 = []
    y2 = []
    
    # 判断long_note的键型
    x3 = []
    y3 = []
    for i in range(start, end):
        audio_features = get_audio_features(x_, sr, bpm, i, offset)
        x0.append(audio_features)
        x2.append(audio_features)
        beat_count = 0
        has_beat = False
        has_ln = False
        long_note_count = 0
        # column 0
        if i in columns[0]:
            if columns[0][i] == 1:
                has_beat = True
                beat_count += 1
            else:
                has_ln = True
                long_note_count += 1
            
        
        # column 1
        if i in columns[1]:
            if columns[1][i] == 1:
                has_beat = True
                beat_count += 2
            else:
                has_ln = True
                long_note_count += 2
            
        # column 2
        if i in columns[2]:
            if columns[2][i] == 1:
                has_beat = True
                beat_count += 2*2 
            else:
                has_ln = True
                long_note_count += 2*2
        
        # column 3
        if i in columns[3]:
            if columns[3][i] == 1:
                has_beat = True
                beat_count += 2*2*2
            else:
                has_ln = True
                long_note_count += 2*2*2
        
        y0.append(int(has_beat))
        
        if has_beat:
            x1.append(audio_features)
            y1.append(beat_count)
            
        y2.append(int(has_ln))
        
        if has_ln:
            x3.append(audio_features)
            y3.append(long_note_count)
        
    return x0, y0, x1, y1, x2, y2, x3, y3

mcz_files = os.listdir("original_beatmaps")
count = 0
X0 = []
Y0 = []
X1 = []
Y1 = []
X2 = []
Y2 = []
X3 = []
Y3 = []
x_ = []
sr = 0
for mcz_file in mcz_files:
    if ".mcz" not in mcz_file:
        continue
    print(count, mcz_file)
    zFile = zipfile.ZipFile("original_beatmaps/" + mcz_file, "r")
    audio_file = ""
    mc_file = ""
    mc_data = {}
    for fileM in zFile.namelist():
        zFile.extract(fileM, './')
        if ".mc" in fileM:
            mc_file = fileM
            data = zFile.read(fileM).decode("utf-8")
            mc_data = json.loads(data)
            print("\t", mc_data["meta"]["version"], mc_data["time"][0], mc_data["note"][-1], "\n")
        elif ".ogg" in fileM:
            audio_file = fileM
        elif ".mp3" in fileM:
            audio_file = fileM
    
    notes = mc_data["note"]
    notes = notes[:len(notes)-1]
    columns_list = get_columns_list(notes)
    bpm = mc_data["time"][0]['bpm']
    if "offset" not in mc_data["note"][-1]:
        offset = 0 
    else:
        offset = mc_data["note"][-1]["offset"]
    
    print(audio_file, bpm, offset)
    
    x_, sr = load_audio(audio_file)
    
    print(len(x_), sr, "\n")
    no_ln_count = 0
    for columns in columns_list:
        _min, _max = get_columns_min_max(columns)
        if (_max - _min) > 40:
            _now = _min
#             print(_now)
            while (_now + 40) < _max:
                x0, y0, x1, y1, x2, y2, x3, y3,  = get_one_data(_now, _now+40, columns, bpm, x_, sr, offset)
                X0.append(x0)
                Y0.append(y0)
                if len(y1) >= 1:    
                    X1.append(x1)
                    Y1.append(y1)
                
                
                if len(y3) > 0:
                    X2.append(x2)
                    Y2.append(y2)
                    X3.append(x3)
                    Y3.append(y3)
                elif (len(y1) >= 1) and (no_ln_count < 15):
                    X2.append(x2)
                    Y2.append(y2)
                    no_ln_count += 1
                
                _now += 38
            
#     break
    count += 1


with open("dataset.json", "w") as f:
    json.dump({
        "X0": X0,
        "Y0": Y0,
        "X1": X1,
        "Y1": Y1,
        "X2": X2,
        "Y2": Y2,
        "X3": X3,
        "Y3": Y3,
    }, f)

with open("glove/malody.txt", "w") as f:
    for y1 in Y1:
        strs = [str(i) for i in y1]
        line = " ".join(strs)
        print(line)
        f.write(line + "\n")

with open("glove/malody2.txt", "w") as f:
    for y3 in Y3:
        strs = [str(i) for i in y3]
        if len(strs) > 0:
            line = " ".join(strs)
            print(line)
            f.write(line + "\n")

