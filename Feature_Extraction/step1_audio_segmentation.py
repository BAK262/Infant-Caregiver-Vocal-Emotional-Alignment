# -*- coding: utf-8 -*-
"""
Created on Tue Jan 24 17:07:48 2023

@author: liming
"""

import os
import pandas as pd
from pydub import AudioSegment

# main_path = '/Users/liming/Desktop/学术/Intern_UTokyo/project'
main_path = 'D:\Seafile\学术\Intern_UTokyo\project'
corpus = 'corpus_Edinburgh'
audio_path = os.path.join(main_path, corpus,"raw_data")
wav_path = os.path.join(main_path, corpus,"segmented_wav")
os.makedirs(wav_path, exist_ok=True)

for mp3_filename in os.listdir(audio_path):
    if mp3_filename.endswith(".mp3"):
        mp3_file = os.path.join(audio_path, mp3_filename)
        txt_file = os.path.join(audio_path, mp3_filename[:-4] + ".txt")
        if os.path.exists(txt_file):
            sound = AudioSegment.from_mp3(mp3_file)
            lines = pd.read_csv(txt_file, sep="\t", header=None)
            for index, row in lines.iterrows():
                participant = row[0]
                start = row[1]
                end = int(row[2])
                segment = sound[start:end]
                wav_file = os.path.join(wav_path, mp3_filename[:-4] + '_' + participant + '_' + f"{start}" + '_' + f"{end}.wav")
                segment.export(wav_file, format="wav")
            os.remove(mp3_file)
        else:
            continue
