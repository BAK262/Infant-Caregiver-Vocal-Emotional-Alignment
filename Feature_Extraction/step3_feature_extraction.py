# -*- coding: utf-8 -*-
"""
Created on Sun Jan 29 19:57:05 2023

@author: 36146
"""
from tqdm import tqdm
import os
import glob
import sys
import datatable as dt

# main_path = '/Users/liming/Desktop/学术/Intern_UTokyo/project'
main_path = 'D:\Seafile\学术\Intern_UTokyo\project'
corpus = 'corpus_Edinburgh'
if sys.platform == 'win32':
    OpenSmilePath = os.path.join(main_path,"opensmile"+"_"+sys.platform,"bin","SMILExtract.exe")
else:
    OpenSmilePath = os.path.join(main_path,"opensmile"+"_"+sys.platform,"bin","SMILExtract")
OpenSmileConfigPath = os.path.join(main_path,"opensmile"+"_"+sys.platform,"config","is09-13","IS13_ComParE.conf")
wav_path = os.path.join(main_path, corpus,"segments_enhanced")
os.makedirs(wav_path, exist_ok=True)
feature_path = os.path.join(main_path, corpus,"audio_feature")
os.makedirs(feature_path, exist_ok=True)

# iterate through wav_list
wav_list = glob.glob(os.path.join(wav_path, "*.wav"))
os.makedirs(os.path.join(main_path, "temp"), exist_ok=True)
rows = []
for temp_path in tqdm(wav_list):
    wav_id = os.path.split(temp_path)[1].split(".")[0]
    out_path = os.path.join(main_path, "temp", wav_id)
    cmd = OpenSmilePath+" -C "+OpenSmileConfigPath+" -I "+temp_path+" -O "+out_path+" -l 0"
    os.system(cmd)
    with open(out_path, 'r') as f:
        for line in f:
            continue
        feat_vec=line.split(",")[1:-1]
    feat_vec = [float(x) for x in feat_vec]
    # extract information from wav_id and create new row in DataTable
    if len(feat_vec) == 6373:
        file_id, participant, start_time, end_time = wav_id.split("_")[0],wav_id.split("_")[1],wav_id.split("_")[2],wav_id.split("_")[3]
        row = {'file_id': file_id, 'participant': participant, 'start_time': int(start_time), 'end_time': int(end_time)}
        for i in range(6373):
            row[f'feat_vec_{i}'] = feat_vec[i]
        rows.append(row)
    else:
        continue

# Create DataTable with the rows
feature_dt = dt.Frame(rows)
feature_dt.names = ['file_id', 'participant', 'start_time', 'end_time', *[f'feat_vec_{i}' for i in range(6373)]]
os.chdir(feature_path)
feature_dt.to_csv('feature_data.csv')
# os.remove(os.path.join(main_path,'temp'))
