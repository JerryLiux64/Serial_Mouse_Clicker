import time
import json
import threading
from pynput.mouse import Button, Controller as mController
from pynput.keyboard import Listener, KeyCode, Key, Controller as kController

delay = 1
button = Button.left
holding = True
start_stop_key = KeyCode(char='s')
exit_key = KeyCode(char='e')

# print(threading.active_count())
# print(threading.current_thread())
# print(threading.enumerate())

class ClickMouse(threading.Thread):
    def __init__(self, delay, button, holding, duration):
        super(ClickMouse, self).__init__()
        self.delay = delay
        self.button = button
        self.running = False
        self.program_running = True
        self.holding = holding
        self.duration = duration

    def start_clicking(self):
        self.running = True
    
    def stop_clicking(self):
        self.running = False

    def exit(self):
        self.stop_clicking()
        self.program_running = False
    
    def run(self):
        # print(threading.current_thread())
        
        while self.program_running:
            timeout = time.time()+self.duration
            while self.running:
                # print(threading.current_thread())
                mouse.click(self.button)
                time.sleep(self.delay)
                if not self.holding:
                    self.stop_clicking()
                if time.time() > timeout:
                    self.exit()
            time.sleep(0.1)
            

# class PressKeyboard(threading.Thread):
#     def __init__(self, key, duration):
#         super(PressKeyboard, self).__init__()
#         self.key = key
#         self.duration = duration
#         self.running = False
#         self.program_running = True
    
#     def start_pressing(self):
#         self.running = True

#     def stop_pressing(self):
#         self.running = False

#     def exit(self):
#         self.stop_pressing()
#         self.program_running = False

#     def run(self):
#         # print(threading.current_thread())
#         while self.program_running:
#             while self.running:
#                 # print(threading.current_thread())
#                 keyboard.press(self.key)
#                 time.sleep(self.duration)
#             time.sleep(0.1)

mouse = mController()
keyboard = kController()
# click_thread = ClickMouse(delay, button, holding, 10)
# click_thread.start()

def on_press(key):
    if key == start_stop_key:
        # print(threading.current_thread())
        click_thread = ClickMouse(delay, button, holding, 10)
        click_thread.start()

        if click_thread.running:
            click_thread.stop_clicking()
        else:
            click_thread.start_clicking()

    elif key == exit_key:
        # print(threading.current_thread())
        click_thread.exit()
        listener.stop()

with Listener(on_press=on_press) as listener:
    # print(threading.current_thread())
    listener.join()
    # print(threading.current_thread())
    