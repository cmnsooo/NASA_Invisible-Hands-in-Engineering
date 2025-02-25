from sound_visualization import visualize
from sound_input import record_audio
from detect_earthquake import detecting, findEq

def main():
    audio_data, fs = record_audio()
    processed_data = visualize(audio_data, fs, target_freq=100)
    raw, trig, char = detecting(processed_data)
    findEq(raw, trig, char)

if __name__ == '__main__':
    main()


