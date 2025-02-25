import tkinter as tk
from PIL import Image, ImageTk, ImageEnhance
import os
import math
from sound_input import record_audio, generate_and_display_planet
from sound_visualization import visualize
from detect_earthquake import detecting, findEq

root = tk.Tk()
root.title("Planet Sonic")

state = 0
audio_data = []
fs = 0

screen_width = int(root.winfo_screenwidth() * 0.9)
screen_height = int(root.winfo_screenheight() * 0.9)

aspect_ratio = 7 / 5

window_width = 1415
window_height = 1008

root.geometry(f"{window_width}x{window_height}")

time_step = 0
amplitude = 0.15
offset = 1.1

def on_enter(event, button, image_path):
    enhance_image_brightness(button, image_path, 1.5)

def on_leave(event, button, image_path):
    enhance_image_brightness(button, image_path, 1.0)

def enhance_image_brightness(button, image_path, brightness_factor):
    image = Image.open(image_path)
    enhancer = ImageEnhance.Brightness(image)
    bright_image = enhancer.enhance(brightness_factor)
    photo = ImageTk.PhotoImage(bright_image)
    button.config(image=photo)
    button.image = photo

def inRect(x, y, x1, x2, y1, y2):
    return x1 <= x <= x2 and y1 <= y <= y2

def on_click(event):
    x, y = event.x, event.y
    global state, audio_data, fs
    
    if state == 'start':
        if inRect(x, y, window_width // 2 - 350, window_width // 2 - 50, window_height - 290, window_height - 210):
            load_main_screen()
        if inRect(x, y, window_width // 2 + 50, window_width // 2 + 350, window_height - 290, window_height - 210):
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
            audio_data, fs = record_audio(state=state)
            state = 'main2_recording_off'
    if state == 'main2_recording_off':
        if inRect(x, y, 392, 462, 578, 648):
            load_analyze_screen()
    if state in ['process', 'earth', 'moon', 'mars']:
        if inRect(x, y, 95, 145, 146, 189):
            load_start_screen()

def load_start_screen():
    canvas.delete("all")
    global state
    state = 'start'
    image_path = './data/img/start.png'
    load_image(image_path)
    canvas.bind("<Button-1>", on_click)
    animate_background_brightness()

def animate_background_brightness():
    global time_step
    enhancer = ImageEnhance.Brightness(original_image)
    brightness = amplitude * math.sin(time_step) + offset
    bright_image = enhancer.enhance(brightness)
    bright_photo = ImageTk.PhotoImage(bright_image)
    canvas.create_image(0, 0, image=bright_photo, anchor="nw")
    canvas.image = bright_photo
    time_step += 0.05
    canvas.after(50, animate_background_brightness)

def load_image(image_path):
    global original_image
    if os.path.exists(image_path):
        try:
            original_image = Image.open(image_path)
            original_image = original_image.resize((window_width, window_height), Image.LANCZOS)
            bg_image = ImageTk.PhotoImage(original_image)
            canvas.create_image(0, 0, image=bg_image, anchor="nw")
            canvas.image = bg_image
        except Exception as e:
            print(f"Error loading image: {e}")
    else:
        print(f"Error: {image_path} not found.")

def load_main_screen():
    canvas.delete("all")
    global state
    state = 'main'
    image_path = './data/img/main.png'
    load_image(image_path)
    canvas.bind("<Button-1>", on_click)

def load_main2_screen():
    canvas.delete("all")
    global state
    state = 'main2'
    image_path = './data/img/main2.png'
    load_image(image_path)
    canvas.bind("<Button-1>", on_click)

def load_moon_screen():
    canvas.delete("all")
    global state
    state = 'moon'
    image_path = './data/img/moon.png'
    load_image(image_path)
    canvas.bind("<Button-1>", on_click)

def load_earth_screen():
    canvas.delete("all")
    global state
    state = 'earth'
    image_path = './data/img/earth.png'
    load_image(image_path)
    canvas.bind("<Button-1>", on_click)

def load_mars_screen():
    canvas.delete("all")
    global state
    state = 'mars'
    image_path = './data/img/mars.png'
    load_image(image_path)
    canvas.bind("<Button-1>", on_click)

def load_analyze_screen():
    canvas.delete("all")
    global state
    state = 'analyze'
    image_path = './data/img/analyze.png'
    load_image(image_path)
    canvas.after(3000, load_process_screen)

def load_process_screen():
    canvas.delete("all")
    global state
    state = 'process'
    image_path = './data/img/process.png'
    load_image(image_path)
    generate_and_display_planet(audio_data, fs)
    processed_data = visualize(audio_data, fs, target_freq=100)
    raw, trig, char = detecting(processed_data)
    findEq(raw, trig, char)

canvas = tk.Canvas(root, width=window_width, height=window_height)
canvas.pack(fill="both", expand=True)

load_start_screen()

root.mainloop()
