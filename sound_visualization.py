import numpy as np
import matplotlib.pyplot as plt
from sound_input import record_audio
from scipy.signal import spectrogram

def visualize(audio_data, fs, target_freq=100, window='hann', nperseg=1024, noverlap=None):
    f, t, Sxx = spectrogram(audio_data.flatten(), fs, window=window, nperseg=nperseg, noverlap=noverlap)
    freq_idx = np.argmin(np.abs(f - target_freq))

    Sxx_specificHz = Sxx[freq_idx, :]
    Sxx_specificHz = Sxx_specificHz / np.max(Sxx_specificHz)
    dB_specificHz = 10 * np.log10(Sxx_specificHz)

    plt.figure(figsize=(10, 4))
    plt.plot(t, dB_specificHz)
    plt.ylabel('Amplitude [dB]')
    plt.xlabel('Time [s]')
    plt.title(f'{target_freq} Hz Frequency Band Over Time')
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    return Sxx_specificHz

# def main():
#     audio_data, fs = record_audio()
#     visualize(audio_data, fs, target_freq=100)

# if __name__ == "__main__":
#     main()
