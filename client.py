from pynput import keyboard
from pynput.keyboard import Key
import time
import requests

SERVER_URL = "http://YOUR_SERVER_IP:8000/submit"
USER_ID = int(input("Enter your user id: "))

key_press_time = {}
sequence = []
last_release_time = None
typed_chars = []

def on_press(key):
    key_press_time[key] = time.time()

def on_release(key):
    global last_release_time

    now = time.time()
    press_time = key_press_time.pop(key, None)
    if press_time is None:
        return

    hold_time = now - press_time
    flight_time = 0.0 if last_release_time is None else press_time - last_release_time
    last_release_time = now

    try:
        key_name = key.char
        typed_chars.append(key.char)
    except AttributeError:
        key_name = str(key).replace("Key.", "")
        if key == Key.space:
            typed_chars.append(" ")
        elif key == Key.enter:
            typed_chars.append("\n")
        elif key == Key.backspace and typed_chars:
            typed_chars.pop()

    sequence.append({
        "key": key_name,
        "hold_time": round(hold_time, 4),
        "flight_time": round(flight_time, 4)
    })

    if key == Key.esc:
        send_data()
        return False

def send_data():
    payload = {
        "user_id": USER_ID,
        "sequence": sequence,
        "text_typed": "".join(typed_chars)
    }
    r = requests.post(SERVER_URL, json=payload)
    print("Server response:", r.json())

with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()
