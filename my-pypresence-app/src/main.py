import tkinter as tk
from pypresence import Presence, ActivityType
import time
import json
from threading import Timer, Event
from datetime import datetime, timezone, timedelta

# You must update pypresence libary with this to make it work: https://github.com/qwertyquerty/pypresence/commit/d6709d33befb2063b46b523cb5abf7e373734df2

CLIENT_ID = '1152566755357626388'
RPC = Presence(CLIENT_ID)
RPC.connect()

auto_update_timer = None
stop_event = Event()

def stop_auto_update():
    global auto_update_timer, stop_event
    stop_event.set()
    if auto_update_timer:
        auto_update_timer.cancel()
        auto_update_timer = None

def update_status(activity, details, start, end, large_image, large_text, small_image, small_text, activity_type=ActivityType.PLAYING):
    RPC.update(
        activity_type=activity_type,
        state=activity,
        details=details,
        start=start,
        end=end,
        large_image=large_image,
        large_text=large_text,
        small_image=small_image,
        small_text=small_text
    )

def on_button_click(activity, details, start, end, large_image, large_text, small_image, small_text):
    stop_auto_update()
    update_status(activity, details, start, end, large_image, large_text, small_image, small_text)
    print(f"Updated status to: {activity} - {details}")

def auto_update_status():
    global stop_event
    stop_event.clear()
    
    with open('buttons.json', 'r', encoding='utf-8') as f:
        button_config = json.load(f)[0]
    
    with open('auto_change.json', 'r', encoding='utf-8') as f:
        auto_status = json.load(f)
    
    status1 = auto_status["status1"]
    status2 = auto_status["status2"]
    
    def update():
        while not stop_event.is_set():
            for s1, s2 in zip(status1, status2):
                if stop_event.is_set():
                    break
                current_time = time.time()
                update_status(s1, s2, current_time, current_time + 15, 
                            button_config["large_image"], 
                            button_config["large_text"],
                            button_config["small_image"], 
                            button_config["small_text"],
                            ActivityType.LISTENING)
                print(f"Auto updated status to: {s1} - {s2}")
                time.sleep(10)
    
    global auto_update_timer
    auto_update_timer = Timer(0, update)
    auto_update_timer.start()

def on_closing():
    stop_auto_update()
    RPC.close()
    root.destroy()

with open('buttons.json', 'r', encoding='utf-8') as f:
    activities = json.load(f)

root = tk.Tk()
root.title("Discord Rich Presence")
root.protocol("WM_DELETE_WINDOW", on_closing)

for i, activity in enumerate(activities):
    row = i // 4
    column = i % 4
    if i == 0:
        button = tk.Button(
            root, 
            text=activity["text"], 
            command=auto_update_status)
    else:
        button = tk.Button(
            root,
            text=activity["text"],
            command=lambda a=activity["activity"], d=activity["details"], 
                   e=activity["end"], li=activity["large_image"], lt=activity["large_text"], 
                   si=activity["small_image"], st=activity["small_text"]: 
                   on_button_click(a, d, time.time(), e, li, lt, si, st)
        )
    button.grid(row=row, column=column, pady=10, padx=10)

root.mainloop()