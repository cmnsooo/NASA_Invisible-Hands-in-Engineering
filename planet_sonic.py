import tkinter as tk
from PIL import Image, ImageTk, ImageEnhance
import os
import math
from sound_input import record_audio, generate_and_display_planet
from sound_visualization import visualize
from detect_earthquake import detecting, findEq

# import sound_visualization
# import detect_earthquake
# import sound_to_eq

# Tkinter 윈도우 생성
root = tk.Tk()
root.title("Planet Sonic")

state = 0
audio_data = []  # 전역 변수로 초기화 (record_audio 호출 전)
fs = 0  # 전역 변수로 초기화 (record_audio 호출 전)

# 사용자 화면 크기 감지
screen_width = int(root.winfo_screenwidth() * 0.9)  # 10% 줄임
screen_height = int(root.winfo_screenheight() * 0.9)  # 10% 줄임

# 비율에 맞춰 가로 세로 크기 설정 (7:5 비율)
aspect_ratio = 7 / 5

window_width = 1415
window_height = 1008

# 창 크기 설정 (비율에 맞게 설정된 크기)
root.geometry(f"{window_width}x{window_height}")

# 밝기 조절을 위한 변수
time_step = 0  # 시간을 대신할 변수, sin 함수에 넣기 위해 사용
amplitude = 0.15  # 진폭: 밝기 변화 범위 (최소 밝기를 올리기 위해 줄임)
offset = 1.1  # 기본 밝기 값 (최소 밝기 올림)

# 버튼 밝기 애니메이션: 마우스를 올렸을 때 밝기 증가, 떠나면 원래 밝기로 돌아감
def on_enter(event, button, image_path):
    enhance_image_brightness(button, image_path, 1.5)  # 밝기를 1.5배로

def on_leave(event, button, image_path):
    enhance_image_brightness(button, image_path, 1.0)  # 원래 밝기

# 버튼 이미지 밝기를 조정하는 함수
def enhance_image_brightness(button, image_path, brightness_factor):
    image = Image.open(image_path)
    enhancer = ImageEnhance.Brightness(image)
    bright_image = enhancer.enhance(brightness_factor)
    photo = ImageTk.PhotoImage(bright_image)
    button.config(image=photo)
    button.image = photo  # 참조를 유지하여 가비지 컬렉션 방지

def inRect(x, y, x1, x2, y1, y2):
    if (x1 <= x <= x2) and (y1 <= y <= y2):
        return True
    return False

def on_click(event):
    x, y = event.x, event.y
    global state, audio_data, fs  # 전역 변수를 가져옴
    # 클릭한 좌표가 [window_width // 2 - 350, window_width // 2 - 50] x [window_height - 290, window_height - 210] 범위 내에 있을 때 load_third_screen 호출
    if state == 'start':
        if inRect(x, y, window_width // 2 - 350, window_width // 2 - 50,  window_height - 290, window_height - 210):
            load_main_screen()  # 세 번째 화면으로 이동
        if inRect(x, y, window_width // 2 + 50, window_width // 2 + 350,  window_height - 290, window_height - 210):
            load_main2_screen()
    if state == 'main':
        if inRect(x, y, 171, 405, 449, 683):
            load_moon_screen()
        if inRect(x, y, 589, 823, 449, 683):
            load_earth_screen()
        if inRect(x, y, 1007, 1291, 449, 683):
            load_mars_screen()
    if state == 'main2':
        if inRect(x, y, 392, 462, 578, 648):
            state = 'main2_recording_on'
            audio_data, fs = record_audio(state=state)  # 클릭 시 녹음 시작
            state = 'main2_recording_off'
    if state == 'main2_recording_off':
        if inRect(x, y, 392, 462, 578, 648):
            load_analyze_screen()
    if state == 'process':
        if inRect(x, y, 95, 145, 146, 189):
            load_start_screen()
    if state == 'earth':
        if inRect(x, y, 95, 145, 146, 189):
            load_start_screen()
    if state == 'moon':
        if inRect(x, y, 95, 145, 146, 189):
            load_start_screen()
    if state == 'mars':
        if inRect(x, y, 95, 145, 146, 189):
            load_start_screen()
    
    

# 첫 번째 화면 함수
def load_start_screen():
    canvas.delete("all")  # 기존의 캔버스 내용을 삭제
    global state
    state = 'start'

    # 첫 번째 이미지 로드
    image_path = './data/img/start.png'  # 첫 번째 이미지 경로
    load_image(image_path)  # 이미지를 불러오는 함수 호출

    # 클릭 이벤트 설정 (마우스 클릭 시 on_click 함수 호출)
    canvas.bind("<Button-1>", on_click)

    # 배경 밝기 애니메이션 시작
    animate_background_brightness()

# 배경 이미지 밝기 애니메이션 함수
def animate_background_brightness():
    global time_step

    # 밝기 조절 객체 생성
    enhancer = ImageEnhance.Brightness(original_image)

    # sin 함수 기반으로 밝기 변화 생성 (1.0 <= 밝기 <= 1.25 범위)
    brightness = amplitude * math.sin(time_step) + offset
    bright_image = enhancer.enhance(brightness)
    bright_photo = ImageTk.PhotoImage(bright_image)

    # 배경 이미지 업데이트
    canvas.create_image(0, 0, image=bright_photo, anchor="nw")
    canvas.image = bright_photo  # 가비지 컬렉션 방지

    # 시간 증가 (주기적 변화)
    time_step += 0.05  # 시간 증가폭을 줄여 주기적으로 더 천천히 변화

    # 50ms마다 밝기 조절 반복
    canvas.after(50, animate_background_brightness)

# 이미지 로드 및 배경 설정 함수
def load_image(image_path):
    global original_image
    if not os.path.exists(image_path):
        print(f"Error: {image_path} 경로에서 이미지를 찾을 수 없습니다.")
    else:
        try:
            original_image = Image.open(image_path)
            original_image = original_image.resize((window_width, window_height), Image.LANCZOS)  # 화면 비율에 맞춰 이미지 크기 조정
            bg_image = ImageTk.PhotoImage(original_image)
            canvas.create_image(0, 0, image=bg_image, anchor="nw")
            canvas.image = bg_image  # 이미지 객체가 가비지 컬렉션되지 않도록 참조 유지
        except Exception as e:
            print(f"Error loading image: {e}")


def load_main_screen():
    canvas.delete("all")
    global state
    state = 'main'

    # 두 번째 이미지 로드
    image_path = './data/img/main.png'  # 두 번째 이미지 경로
    load_image(image_path)  # 이미지를 불러오는 함수 호출

    canvas.bind("<Button-1>", on_click)


def load_main2_screen():
    canvas.delete("all")
    global state
    state = 'main2'

    # 두 번째 이미지 로드
    image_path = './data/img/main2.png'  # 두 번째 이미지 경로
    load_image(image_path)  # 이미지를 불러오는 함수 호출

    canvas.bind("<Button-1>", on_click)


def load_moon_screen():
    canvas.delete("all")
    global state
    state = 'moon'

    # 두 번째 이미지 로드
    image_path = './data/img/moon.png'  # 두 번째 이미지 경로
    load_image(image_path)  # 이미지를 불러오는 함수 호출

    canvas.bind("<Button-1>", on_click)

def load_earth_screen():
    canvas.delete("all")
    global state
    state = 'earth'

    # 배경 이미지 로드
    image_path = './data/img/earth.png'
    load_image(image_path)  # 이미지를 먼저 불러와서 그리기

    # 클릭 이벤트 설정
    canvas.bind("<Button-1>", on_click)

def load_mars_screen():
    canvas.delete("all")
    global state
    state = 'mars'

    # 두 번째 이미지 로드
    image_path = './data/img/mars.png'  # 두 번째 이미지 경로
    load_image(image_path)  # 이미지를 불러오는 함수 호출

    canvas.bind("<Button-1>", on_click)

def load_analyze_screen():
    canvas.delete("all")
    global state
    state = 'analyze'

    # 두 번째 이미지 로드
    image_path = './data/img/analyze.png'  # 두 번째 이미지 경로
    load_image(image_path)  # 이미지를 불러오는 함수 호출

    # 3초 후에 load_progress_screen 함수 호출
    canvas.after(3000, load_process_screen)  # 1000밀리초 = 1초

def load_process_screen():
    canvas.delete("all")
    global state
    state = 'process'

    # 두 번째 이미지 로드
    image_path = './data/img/process.png'  # 두 번째 이미지 경로
    load_image(image_path)  # 이미지를 불러오는 함수 호출\

    generate_and_display_planet(audio_data, fs)
    processed_data = visualize(audio_data, fs, target_freq=100)
    raw, trig, char = detecting(processed_data)
    findEq(raw, trig, char)



# 캔버스 위젯 생성
canvas = tk.Canvas(root, width=window_width, height=window_height)
canvas.pack(fill="both", expand=True)

# 첫 번째 화면 로드
load_start_screen()

root.mainloop()
