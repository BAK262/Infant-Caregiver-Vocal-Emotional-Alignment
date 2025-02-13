# -*- coding: utf-8 -*-
"""
Created on Fri Feb  3 10:33:37 2023

@author: Ming Li
"""
from p_tqdm import p_map
from functools import partial
import librosa
import librosa.display 
import numpy as np
import os
import glob
import soundfile as sf

# main_path = '/Users/liming/Desktop/学术/Intern_UTokyo/project'
main_path = 'D:\Seafile\学术\Intern_UTokyo\project'
corpus = 'corpus_Edinburgh'
wav_path = os.path.join(main_path, corpus,"segmented_wav")

save_path = os.path.join(main_path, corpus,"segments_enhanced")
os.makedirs(save_path, exist_ok=True)

wav_list = glob.glob(os.path.join(wav_path, "*.wav"))

def process_file(temp_path, save_path):
    # load audio data
    sound, sr = librosa.load(temp_path,sr=None)
    wav_id = os.path.split(temp_path)[1].split(".")[0]
    participant = wav_id.split("_")[1]

    # if it's an empty file, skip
    if sound.shape[0] == 0:
        return "opps"
    
    # voice emphasize
    sound_enh = np.append(sound[0], sound[1:] -0.97 * sound[:-1])
    # always save enhanced audio segments 
    sf.write(os.path.join(save_path, os.path.split(temp_path)[1]), sound_enh, sr)

    # voice detection
    # resample to a fixed sample rate
    sound_edt = librosa.resample(sound_enh, orig_sr=sr, target_sr=16000)
    # compute the fundamental frequency
    if participant == "CHI":
        f0_min = 120 # Hz
        f0_max = 1000 # Hz
    else:
        f0_min = 120 # Hz
        f0_max = 600 # Hz
    f0t, voiced_flagt, voiced_probst = librosa.pyin(sound_edt,sr=16000,frame_length=512, fill_na=np.nan, n_thresholds=50, fmin=f0_min, fmax=f0_max)
    # detect the length of voiced duration
    not_null_indices = np.flatnonzero(~np.isnan(f0t))
    consecutive_lengths = np.diff(np.r_[-1, not_null_indices, len(f0t)]) - 1
    max_length_in_sec = max(consecutive_lengths)*128/16000
    # set the threshold for detecting the target participant's voice
    # based on the syllable length range of children and adults
    if participant == "CHI":
        length_threshold = 0.6 # in second
    else:
        length_threshold = 0.25 # in second
    # if there is no target participant's voice, record it
    if max_length_in_sec < length_threshold:
        return(wav_id)
    else:
        return('opps')

if __name__ == '__main__':
    # enhanced voice will be automatically by 'process_file' funciton
    record_list = p_map(partial(process_file, save_path=save_path), wav_list)
    # record segments without voice
    filtered_list = [x for x in record_list if x != 'opps']
    with open(os.path.join(main_path,corpus,"segments_without_voice.txt"), "w") as f:
        for item in filtered_list:
            f.write("%s\n" % item)

