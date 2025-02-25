import sounddevice as sd
import numpy as np
from scipy.fft import fft
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
import random
import threading
import keyboard

planet_features = {
    "Earth": {"gravity": 9.8, "atmosphere": 1.0, "temperature": 15, "mass": 5.97e24, "elements": ["Oxygen", "Nitrogen"], "atmospheric_composition": "78% Nitrogen, 21% Oxygen"},
    "Mars": {"gravity": 3.7, "atmosphere": 0.6, "temperature": -60, "mass": 0.64171e24, "elements": ["Carbon Dioxide"], "atmospheric_composition": "95% Carbon Dioxide"},
    "Venus": {"gravity": 8.87, "atmosphere": 92, "temperature": 460, "mass": 4.867e24, "elements": ["Carbon Dioxide"], "atmospheric_composition": "96% Carbon Dioxide"},
    "Jupiter": {"gravity": 24.79, "atmosphere": 0.1, "temperature": -108, "mass": 1.898e27, "elements": ["Hydrogen", "Helium"], "atmospheric_composition": "90% Hydrogen, 10% Helium"}
}

is_recording = False

def record_audio(fs=44100, state=0):
    if state != 'main2_recording_on':
        return
    global is_recording
    is_recording = True
    print("Recording... Press 'Enter' to stop.")
    audio_data = []
    def capture_audio():
        nonlocal audio_data
        audio_data = sd.rec(int(100 * fs), samplerate=fs, channels=1, dtype='float64')
        sd.wait()
    recording_thread = threading.Thread(target=capture_audio)
    recording_thread.start()
    keyboard.wait('enter')
    is_recording = False
    sd.stop()
    print("Recording finished")
    return audio_data[:int(fs*len(audio_data)/fs)], fs

def extract_frequency_features(audio_data, fs):
    N = len(audio_data)
    T = 1.0 / fs
    yf = fft(audio_data.flatten())
    xf = np.fft.fftfreq(N, T)[:N // 2]
    important_frequencies = 2.0 / N * np.abs(yf[:N // 2])
    return xf, important_frequencies

def create_new_planet(freq_features, existing_planets):
    random_planet = random.choice(list(existing_planets.values()))
    gravity = random_planet["gravity"] * np.mean(freq_features) * 10
    atmosphere = random_planet["atmosphere"] * np.var(freq_features)
    temperature_celsius = random_planet["temperature"] + np.mean(freq_features) * 100
    temperature_kelvin = temperature_celsius + 273.15
    mass = random_planet["mass"] * np.mean(freq_features) * 5
    elements = random_planet["elements"]
    atmospheric_composition = random_planet["atmospheric_composition"]
    return {"gravity": gravity, "atmosphere": atmosphere, "temperature": temperature_kelvin, "mass": mass, "elements": elements, "atmospheric_composition": atmospheric_composition}

def calculate_density(planet_radius, planet_mass):
    volume = (4/3) * np.pi * planet_radius**3
    density = planet_mass / volume
    return density

def visualize_and_describe_planet_with_design(planet):
    fig, ax = plt.subplots(figsize=(6, 6))
    scale_factor = 0.1
    radius = planet["gravity"] * 0.5 * scale_factor
    temperature_color = planet["temperature"] / 1000
    temperature_color = np.clip(temperature_color, 0, 1)
    density = calculate_density(radius / scale_factor, planet['mass'])
    planet_circle = plt.Circle((0.5, 0.5), radius=radius, color=(temperature_color, 0, 1 - temperature_color), alpha=0.8)
    ax.add_artist(planet_circle)
    ring_outer_radius_x = radius * 1.5
    ring_outer_radius_y = radius * 0.7
    ring_inner_radius_x = radius * 1.2
    ring_inner_radius_y = radius * 0.5
    theta = np.linspace(0, 2 * np.pi, 100)
    ring_x_outer = 0.5 + ring_outer_radius_x * np.cos(theta)
    ring_y_outer = 0.5 + ring_outer_radius_y * np.sin(theta)
    ring_x_inner = 0.5 + ring_inner_radius_x * np.cos(theta)
    ring_y_inner = 0.5 + ring_inner_radius_y * np.sin(theta)
    ax.fill_betweenx(ring_y_outer[ring_y_outer > 0.5], ring_x_outer[ring_y_outer > 0.5], ring_x_inner[ring_y_outer > 0.5], color='gray', alpha=0.3)
    ax.fill_betweenx(ring_y_outer[ring_y_outer <= 0.5], ring_x_outer[ring_y_outer <= 0.5], ring_x_inner[ring_y_outer <= 0.5], color='gray', alpha=0.3)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect('equal', 'box')
    plt.title(f"Generated Planet (Gravity: {planet['gravity']:.2f}, Temp: {planet['temperature']:.2f} K)")
    plt.show()
    print("=== Generated Planet Details ===")
    print(f"Mass: {planet['mass']:.2e} kg")
    print(f"Main Elements: {', '.join(planet['elements'])}")
    print(f"Atmospheric Composition: {planet['atmospheric_composition']}")
    print(f"Surface Gravity: {planet['gravity']:.2f} m/s²")
    print(f"Surface Temperature: {planet['temperature']:.2f} K")
    print(f"Density: {density:.2f} kg/m³")

def generate_and_display_planet(audio_data, fs):
    xf, freq_features = extract_frequency_features(audio_data, fs)
    scaler = MinMaxScaler()
    normalized_features = scaler.fit_transform(freq_features.reshape(-1, 1))
    new_planet = create_new_planet(normalized_features, planet_features)
    visualize_and_describe_planet_with_design(new_planet)
