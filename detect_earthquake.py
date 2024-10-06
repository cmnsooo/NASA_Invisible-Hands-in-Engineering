import os
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from obspy.signal.invsim import cosine_taper
from obspy.signal.filter import highpass
from obspy.signal.trigger import classic_sta_lta, trigger_onset
import matplotlib.pyplot as plt

a=0.22672614455223083
b=-0.029509663581848145
c=0.0457753948867321

sWindow = 5
lWindow = 50
sampling_rate = 50

def preprocess_signal(data, sampling_rate):
    taper = cosine_taper(len(data), 0.1)
    data = data * taper
    filtered = highpass(data, freq=1.0, df=sampling_rate, corners=4, zerophase=True)
    return filtered

def detectSTALTA(data, threshold_on=5.0, threshold_off=3.0):
    cft = classic_sta_lta(data, sWindow, lWindow)
    triggers = trigger_onset(cft, threshold_on, threshold_off)
    return cft, triggers

def findLongest(triggers):
    if len(triggers) == 0:
        return None
    durations = [(trigger[1] - trigger[0], trigger) for trigger in triggers]
    longest = max(durations, key=lambda k: k[0])[1]
    return longest

def trimming(arr):
    idx = len(arr) - 1
    while idx >= 0 and arr[idx] == 0:
        idx -= 1
    trimmed = arr[:idx + 1]
    return trimmed

def detecting(raw):
    raw = trimming(raw)
    print(len(raw))
    preprocessed_data = preprocess_signal(raw, sampling_rate)
    cft, triggers = detectSTALTA(preprocessed_data)

    trigger = findLongest(triggers)

    print(f'Detected : {triggers}')
    print(f'Longest : {trigger}')

    plt.figure(figsize=(10, 4))
    plt.plot(preprocessed_data, label='Filtered Data')
    if trigger is not None:
        plt.axvline(x=trigger[0], color='red', linestyle='-', label='On')
        plt.axvline(x=trigger[1], color='green', linestyle='-', label='Off')
    plt.title(f'Detected Earthquake Triggers using STA/LTA')
    plt.xlabel('Samples')
    plt.ylabel('Amplitude')
    plt.legend()
    plt.show()

    plt.figure(figsize=(10, 4))
    plt.plot(cft, label='STA/LTA Ratio')
    plt.title('STA/LTA Characteristic Function')
    plt.xlabel('Samples')
    plt.ylabel('STA/LTA Ratio')
    plt.legend()
    plt.show()

    return raw, triggers, cft

def findEq(raw, triggers, char):
    raw = np.array(raw)
    char = np.array(char)

    a=0.22672614455223083
    b=-0.029509663581848145
    c=0.0457753948867321

    ans = []
    for x in triggers:
        ampl = np.max(raw[x[0]:x[1]])
        ratio = np.max(char[x[0]:x[1]])
        dur = x[1] - x[0]

        print(ampl, ratio, dur, a*ampl + b*ratio + c*dur)

        ans.append([a*ampl + b*ratio + c*dur, [x[0], x[1]]])

    ans = sorted(ans, key=lambda x: x[0], reverse=True)
    
    plt.figure(figsize=(10, 4))
    plt.plot(raw, label='Raw Data')
        
    for i in range(min(len(ans), 3)):
        k = ans[i][1]
        plt.axvline(x=k[0], color='red', linestyle='-', label='On')
        plt.axvline(x=k[1], color='green', linestyle='-', label='Off')
        
    plt.title(f"Detected Earthquake Triggers using STA/LTA")
    plt.xlabel('Samples')
    plt.ylabel('Amplitude Change')
    plt.legend()
    plt.show()


