import sounddevice as sd
import numpy as np
from scipy.fft import fft
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
import random
import threading
import keyboard

# 1. 미리 정의된 행성 데이터
planet_features = {
    "Earth": {"gravity": 9.8, "atmosphere": 1.0, "temperature": 15, "mass": 5.97e24, "elements": ["Oxygen", "Nitrogen"], "atmospheric_composition": "78% Nitrogen, 21% Oxygen"},
    "Mars": {"gravity": 3.7, "atmosphere": 0.6, "temperature": -60, "mass": 0.64171e24, "elements": ["Carbon Dioxide"], "atmospheric_composition": "95% Carbon Dioxide"},
    "Venus": {"gravity": 8.87, "atmosphere": 92, "temperature": 460, "mass": 4.867e24, "elements": ["Carbon Dioxide"], "atmospheric_composition": "96% Carbon Dioxide"},
    "Jupiter": {"gravity": 24.79, "atmosphere": 0.1, "temperature": -108, "mass": 1.898e27, "elements": ["Hydrogen", "Helium"], "atmospheric_composition": "90% Hydrogen, 10% Helium"}
}

# 녹음 중 플래그
is_recording = False

# 2. 실시간 음성 녹음 설정 (엔터 키를 누르면 녹음 종료)
def record_audio(fs=44100, state=0):
    if state != 'main2_recording_on':
        return
    
    global is_recording

    is_recording = True
    print("Recording... Press 'Enter' to stop.")
    
    audio_data = []

    def capture_audio():
        nonlocal audio_data
        audio_data = sd.rec(int(100 * fs), samplerate=fs, channels=1, dtype='float64')  # 최대 100초까지만 허용 (임시)
        sd.wait()  # 녹음 완료 대기

    # 녹음 쓰레드 시작
    recording_thread = threading.Thread(target=capture_audio)
    recording_thread.start()

    # 엔터키 입력 대기
    keyboard.wait('enter')

    # 엔터키 입력 후 녹음 중단
    is_recording = False
    sd.stop()
    print("Recording finished")
    
    return audio_data[:int(fs*len(audio_data)/fs)], fs

# 3. FFT를 통한 주파수 분석
def extract_frequency_features(audio_data, fs):
    N = len(audio_data)
    T = 1.0 / fs
    yf = fft(audio_data.flatten())
    xf = np.fft.fftfreq(N, T)[:N // 2]
    
    # 주파수 성분 중 중요한 부분만 추출
    important_frequencies = 2.0 / N * np.abs(yf[:N // 2])
    return xf, important_frequencies

# 4. 주파수 기반 행성 생성
def create_new_planet(freq_features, existing_planets):
    random_planet = random.choice(list(existing_planets.values()))
    
    # 음성 특징 기반으로 중력, 대기 성분, 온도를 조정
    gravity = random_planet["gravity"] * np.mean(freq_features) * 10
    atmosphere = random_planet["atmosphere"] * np.var(freq_features)
    temperature_celsius = random_planet["temperature"] + np.mean(freq_features) * 100  # 섭씨 온도
    temperature_kelvin = temperature_celsius + 273.15  # 켈빈 온도
    mass = random_planet["mass"] * np.mean(freq_features) * 5
    elements = random_planet["elements"]
    atmospheric_composition = random_planet["atmospheric_composition"]
    
    # 새로운 행성의 특성 반환
    new_planet = {
        "gravity": gravity,
        "atmosphere": atmosphere,
        "temperature": temperature_kelvin,  # 켈빈 온도로 반환
        "mass": mass,
        "elements": elements,
        "atmospheric_composition": atmospheric_composition
    }
    
    return new_planet

# 5. 밀도 계산 함수
def calculate_density(planet_radius, planet_mass):
    # 구의 부피 공식 V = 4/3 * pi * r^3
    volume = (4/3) * np.pi * planet_radius**3
    # 밀도 rho = mass / volume
    density = planet_mass / volume
    return density

# 6. 행성 시각화 및 설명 출력 (타원형 고리 추가 및 행성 뒤로 가려지는 부분 처리)
def visualize_and_describe_planet_with_design(planet):
    fig, ax = plt.subplots(figsize=(6, 6))
    
    # 행성의 크기는 중력에 비례, 색상은 온도에 비례 (전체 크기를 10분의 1로 축소)
    scale_factor = 0.1  # 크기 축소 비율
    radius = planet["gravity"] * 0.5 * scale_factor
    temperature_color = planet["temperature"] / 1000  # 켈빈 온도 사용
    
    # temperature_color 값이 0과 1 사이로 유지되도록 클리핑
    temperature_color = np.clip(temperature_color, 0, 1)
    
    # 밀도 계산
    density = calculate_density(radius / scale_factor, planet['mass'])  # 실제 크기에서 밀도를 계산
    
    # 행성 그리기
    planet_circle = plt.Circle((0.5, 0.5), radius=radius, color=(temperature_color, 0, 1 - temperature_color), alpha=0.8)
    ax.add_artist(planet_circle)

    # 타원형 고리 추가 (앞쪽 고리와 뒤쪽 고리 분리)
    ring_outer_radius_x = radius * 1.5  # 타원의 x축 반경
    ring_outer_radius_y = radius * 0.7  # 타원의 y축 반경
    ring_inner_radius_x = radius * 1.2
    ring_inner_radius_y = radius * 0.5
    theta = np.linspace(0, 2 * np.pi, 100)
    
    # 뒤쪽 고리 부분 (행성 뒤에 가려짐)
    ring_x_outer = 0.5 + ring_outer_radius_x * np.cos(theta)
    ring_y_outer = 0.5 + ring_outer_radius_y * np.sin(theta)
    ring_x_inner = 0.5 + ring_inner_radius_x * np.cos(theta)
    ring_y_inner = 0.5 + ring_inner_radius_y * np.sin(theta)

    ax.fill_betweenx(ring_y_outer[ring_y_outer > 0.5], ring_x_outer[ring_y_outer > 0.5], ring_x_inner[ring_y_outer > 0.5], color='gray', alpha=0.3)
    
    # 앞쪽 고리 부분 (행성 앞에 보이는 부분)
    ax.fill_betweenx(ring_y_outer[ring_y_outer <= 0.5], ring_x_outer[ring_y_outer <= 0.5], ring_x_inner[ring_y_outer <= 0.5], color='gray', alpha=0.3)

    # 타원형 구름 효과 추가 (축소 비율 적용)
    cloud_radius_x = radius * 0.9  # x축 반경
    cloud_radius_y = radius * 0.5  # y축 반경 (타원형 모양을 위해 y축 반경을 다르게 설정)
    
    for _ in range(8):  # 타원형 구름 8개 추가
        cloud_angle = np.random.uniform(0, 2 * np.pi)
        cloud_distance_x = np.random.uniform(0, cloud_radius_x)
        cloud_distance_y = np.random.uniform(0, cloud_radius_y)
        cloud_x = 0.5 + cloud_distance_x * np.cos(cloud_angle)
        cloud_y = 0.5 + cloud_distance_y * np.sin(cloud_angle)
        ax.plot(cloud_x, cloud_y, 'o', color='white', markersize=np.random.uniform(10, 20) * scale_factor, alpha=0.7)

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect('equal', 'box')
    plt.title(f"Generated Planet (Gravity: {planet['gravity']:.2f}, Temp: {planet['temperature']:.2f} K)")  # 켈빈 온도로 출력
    plt.show()

    # 행성의 물리적 특성 설명
    print("=== Generated Planet Details ===")
    print(f"Mass: {planet['mass']:.2e} kg")
    print(f"Main Elements: {', '.join(planet['elements'])}")
    print(f"Atmospheric Composition: {planet['atmospheric_composition']}")
    print(f"Surface Gravity: {planet['gravity']:.2f} m/s²")
    print(f"Surface Temperature: {planet['temperature']:.2f} K")  # 켈빈 온도로 출력
    print(f"Density: {density:.2f} kg/m³")  # 밀도 출력

# 7. 전체 프로세스
def generate_and_display_planet(audio_data, fs):
    """
    실시간 음성을 녹음하여 행성을 생성하고 시각화하며, 행성의 특성에 대한 설명을 출력.
    """
    
    # 2. 주파수 특징 추출
    xf, freq_features = extract_frequency_features(audio_data, fs)
    
    # 3. 주파수 특징 정규화
    scaler = MinMaxScaler()
    normalized_features = scaler.fit_transform(freq_features.reshape(-1, 1))
    
    # 4. 새로운 행성 생성
    new_planet = create_new_planet(normalized_features, planet_features)
    
    # 5. 생성된 행성 시각화 및 설명 출력 (디자인 요소 포함)
    visualize_and_describe_planet_with_design(new_planet)

# 실행
# generate_and_display_planet()
