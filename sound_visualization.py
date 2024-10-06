import numpy as np
import matplotlib.pyplot as plt
from sound_input import record_audio
from scipy.signal import spectrogram

def visualize(audio_data, fs, target_freq=100, window='hann', nperseg=1024, noverlap=None):
    """
    입력된 오디오 데이터를 기반으로 16000Hz 주파수 대역의 음역대(주파수 스펙트럼)을 시각화합니다.
    
    Parameters:
    - audio_data: 녹음된 오디오 데이터
    - fs: 샘플링 주파수 (sampling rate)
    - target_freq: 시각화할 주파수 (기본값: 16000 Hz)
    - window: 윈도우 함수 (default: 'hann')
    - nperseg: STFT를 위한 각 세그먼트의 길이
    - noverlap: 오버랩 양 (기본적으로 nperseg의 절반)
    """
    # 주파수 스펙트럼 계산 (Spectrogram)
    f, t, Sxx = spectrogram(audio_data.flatten(), fs, window=window, nperseg=nperseg, noverlap=noverlap)

    # target_freq에 가장 가까운 주파수 성분 찾기
    freq_idx = np.argmin(np.abs(f - target_freq))

    # 16000Hz에 해당하는 주파수 성분만 시각화
    Sxx_specificHz = Sxx[freq_idx, :]
    Sxx_specificHz = Sxx_specificHz / np.max(Sxx_specificHz)  # 정규화
    dB_specificHz = 10 * np.log10(Sxx_specificHz)

    # 시각화
    plt.figure(figsize=(10, 4))
    plt.plot(t, dB_specificHz)  # dB 스케일로 표현
    plt.ylabel('Amplitude [dB]')
    plt.xlabel('Time [s]')
    plt.title(f'{target_freq} Hz Frequency Band Over Time')
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    return Sxx_specificHz

# def main():
#     # 실시간으로 오디오 녹음
#     audio_data, fs = record_audio()

#     # 16000Hz 주파수를 시각화
#     visualize(audio_data, fs, target_freq=100)

# if __name__ == "__main__":
#     main()
