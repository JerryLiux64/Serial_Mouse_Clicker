import time
import json
import sys
import threading
import logging
from pynput.mouse import Button, Controller as mController
from pynput.keyboard import Listener, KeyCode, Key, Controller as kController

logging.basicConfig(level=logging.INFO,
					format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
					datefmt="%Y-%m-%d %H:%M:%S")
logger = logging.getLogger(__name__)

delay = 1
button = Button.left
holding = True
start_stop_key = KeyCode(char='s')
exit_key = KeyCode(char='e')

# print(threading.active_count())
# print(threading.current_thread())
# print(threading.enumerate())

class Action(threading.Thread):
    def __init__(self, delay: float , hold: bool, duration: float, action):
        super(Action, self).__init__()
        self.delay = delay
        self.running = False
        self.program_running = True
        self.holding = holding
        self.duration = duration
        self.action = action

    def start_action(self):
        self.running = True
    
    def stop_action(self):
        self.running = False

    def exit(self):
        self.stop_action()
        self.program_running = False

class ClickMouse(Action):
    def __init__(self, button: str, *args, **kwargs):
        if button not in {'right', 'middle', 'left'}:
            raise ValueError("ClickMouse: button must be one of %r" % {'right', 'middle', 'left'})
        self.button = {'right':Button.right, 'middle':Button.middle, 'left':Button.left}[button]
        logger.error(f"{self.__name__} on {self.button}.")
        super(ClickMouse, self).__init__(*args, **kwargs)

    def run(self):
        print(f"{ClickMouse.__name__}: threading.current_thread()")
        while self.program_running:
            while self.running:
                # print(threading.current_thread())
                mouse.click(self.button)
                time.sleep(self.delay)
                if not self.holding:
                    self.stop_action()
                # if time.time() > timeout:
                #     self.exit()
            time.sleep(0.1)

class ClickKey(Action):            
    def __init__(self, key: str, *args, **kwargs):
        self.key = KeyCode.from_char(key)
        super(ClickKey, self).__init__(*args, **kwargs)

    def run(self):
        print(f"{ClickKey.__name__}: threading.current_thread()")
        while self.program_running:
            # timeout = time.time() + float(self.duration)
            while self.running:
                # print(threading.current_thread())
                keyboard.press(self.key)
                time.sleep(self.delay)
                if not self.holding:
                    self.stop_action()
                # if time.time() > timeout:
                    # self.exit()
            time.sleep(0.1)
 
def create_action(content):
    items = content.keys()
    try:
        assert all(i in items for i in ["action", "delay", "hold", "duration"])
    except AssertionError:
        logger.error(f"An act must contains ['action', 'delay', 'hold', 'duration'].")
        sys.exit(1)

    if content["action"] == "mouse":
        # Check the other args are numbers
        return ClickMouse(**content)
    elif content["action"] == "keyboard":
        return ClickKey(**content)
    else:
        logger.error("Action must be 'button' or 'keyboard'")
        sys.exit(1)
    return None

def on_press(key):
    if key == start_stop_key:
        # print(f"On press: {threading.current_thread()}")
        if action.running:
            action.stop_action()
        else:
            action.start_action()

    elif key == exit_key:
        # print(f"On press exit: {threading.current_thread()}")
        action.exit()
        listener.stop()

with open("auto.json", 'r') as f:
    content = json.load(f)

mouse = mController()
keyboard = kController()

with Listener(on_press=on_press) as listener:
    # print(threading.current_thread())
    listener.join()
    # print(threading.current_thread())
    