import time
import json
import sys
import threading
import logging
from datetime import datetime
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

class Action(threading.Thread):
    def __init__(self, delay: float , hold: bool, duration: float, action):
        super(Action, self).__init__()
        self.delay = float(delay)
        self.running = False
        self.program_running = True
        self.holding = holding
        self.duration = float(duration)
        self.action = action
        self.timer = 0

    def start_action(self):
        logger.info(f"Start {self.__class__.__name__}.")
        self.timer = -1
        self.running = True
    
    def stop_action(self):
        logger.info(f"Stop {self.__class__.__name__}.")
        self.running = False

    def exit(self):
        self.stop_action()
        self.program_running = False

class ClickMouse(Action):
    def __init__(self, button: str, *args, **kwargs):
        if button not in {'right', 'middle', 'left'}:
            raise ValueError("ClickMouse: button must be one of %r" % {'right', 'middle', 'left'})
        self.button = {'right':Button.right, 'middle':Button.middle, 'left':Button.left}[button]
        logger.info(f"{self.__class__.__name__} on {self.button}.")
        super(ClickMouse, self).__init__(*args, **kwargs)

    def run(self):
        print(f"{ClickMouse.__class__}: threading.current_thread()")
        while self.program_running:
            while self.running:
                if self.timer == -1 or (datetime.now() - self.timer).total_seconds() > self.delay:
                    logger.info(f"Click mouse on {self.button}")
                    mouse.click(self.button)
                    self.timer = datetime.now()
                    if not self.holding:
                        self.stop_action()
            # time.sleep(0.01)

class ClickKey(Action):            
    def __init__(self, key: str, *args, **kwargs):
        self.key = KeyCode.from_char(key)
        logger.info(f"{self.__class__.__name__} on {self.key}.")
        super(ClickKey, self).__init__(*args, **kwargs)

    def run(self):
        print(f"{ClickKey.__name__}: threading.current_thread()")
        while self.program_running:
            while self.running:
                # print(threading.current_thread())
                if self.timer == -1 or (datetime.now() - self.timer).total_seconds() > self.delay:
                    keyboard.press(self.key)
                    self.timer = datetime.now()
                    if not self.holding:
                        self.stop_action()
            # time.sleep(0.01)
 
class ActControl(threading.Thread):
    def __init__(self, content):
        super(ActControl, self).__init__()
        self.content = content
        self.running = False
        self.program_running = True
        self.actions = []
        for act in self.content:
            action = create_action(self.content[act])
            action.start()
            self.actions.append(action)
         
        logger.info(self.actions)

    def start_action(self):
        self.timer = -1
        self.actCount = 0
        self.running = True
    
    def stop_action(self):
        self.running = False

    def exit(self):
        self.stop_action()
        for act in self.actions:    
            act.exit()
        self.program_running = False

    def run(self):
        while self.program_running:
            while self.running:
                cur_action = self.actions[self.actCount]
                if self.timer == -1: 
                    self.timer = datetime.now()
                    cur_action.start_action()
                if (datetime.now() - self.timer).total_seconds() > cur_action.duration:
                    cur_action.stop_action()
                    self.actCount = (self.actCount + 1)%len(self.actions)
                    self.timer = -1
                
            # time.sleep(0.1)

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
        if actControl.running:
            actControl.stop_action()
        else:
            actControl.start_action()

    elif key == exit_key:
        # print(f"On press exit: {threading.current_thread()}")
        actControl.exit()
        listener.stop()

with open("auto.json", 'r') as f:
    content = json.load(f)

mouse = mController()
keyboard = kController()
actControl = ActControl(content)
actControl.start()

with Listener(on_press=on_press) as listener:
    # print(threading.current_thread())
    listener.join()
    # print(threading.current_thread())
    