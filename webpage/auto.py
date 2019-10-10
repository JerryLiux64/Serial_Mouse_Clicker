import time
import json
import sys
import threading
import logging
# from abc import ABC, abstractmethod
from datetime import datetime
from pynput.mouse import Button, Controller as mController
from pynput.keyboard import Listener, KeyCode, Key, Controller as kController

logging.basicConfig(level=logging.INFO,
					format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
					datefmt="%Y-%m-%d %H:%M:%S")
logger = logging.getLogger(__name__)

class Action(threading.Thread):
    def __init__(self, runtime: float , holding: str, duration: float, breaktime = 0, *args, **kwargs):
        super(Action, self).__init__()
        self.runtime = float(runtime)
        self.running = False
        self.program_running = True
        self.hold = {"Yes":True, "No":False}[holding]
        self.duration = float(duration)
        # self.action = action
        self.breaktime = float(breaktime)
        self.timer = 0

    def start_action(self):
        logger.info(f"Start {self.__class__.__name__}.")
        self.timer = datetime.now()
        self.first_round = True
        self.running = True
    
    def stop_action(self):
        logger.info(f"Stop {self.__class__.__name__}.")
        self.running = False

    def exit(self):
        self.stop_action()
        self.program_running = False

class ClickMouse(Action):
    def __init__(self, actionOn: str, mouse = "", *args, **kwargs):
        if actionOn not in {'Left-Click', 'Middle', 'Right-Click'}:
            raise ValueError("ClickMouse: button must be one of %r" % {'Left-Click', 'Middle', 'Right-Click'})
        self.button = {'Right-Click':Button.right, 'Middle':Button.middle, 'Left-Click':Button.left}[actionOn]
        self.mouse = mouse
        logger.info(f"{self.__class__.__name__} on {self.button}.")
        super(ClickMouse, self).__init__(*args, **kwargs)

    def run(self):
        print(f"{ClickMouse.__class__}: threading.current_thread()")
        while self.program_running:
            while self.running:
                # if self.timer == -1 or (datetime.now() - self.timer).total_seconds() > self.runtime:
                #     logger.info(f"Click mouse on {self.button}")
                #     self.mouse.click(self.button)
                #     self.timer = datetime.now()
                #     if not self.hold:
                #         logger.info("Hoding is 'No'. Click only once per round.")
                #         self.stop_action()
                
                cur_time = (datetime.now() - self.timer).total_seconds()
                if self.first_round:
                    # logger.info(f"Click mouse on {self.button}")
                    self.mouse.click(self.button)
                    self.first_round = False
                elif cur_time < self.runtime:
                    if self.hold:
                        # logger.info(f"Click mouse on {self.button}")
                        self.mouse.click(self.button)
                elif cur_time < self.runtime + self.breaktime:
                    pass
                else:
                    self.timer = datetime.now()
                    self.first_round = True
                
            # time.sleep(0.01)

class ClickKey(Action):            
    def __init__(self, actionOn: str, keyboard = "", *args, **kwargs):
        self.key = KeyCode.from_char(actionOn)
        self.keyboard = keyboard
        logger.info(f"{self.__class__.__name__} on {self.key}.")
        super(ClickKey, self).__init__(*args, **kwargs)

    def run(self):
        print(f"{ClickKey.__name__}: threading.current_thread()")
        while self.program_running:
            while self.running:
                # if self.timer == -1 or (datetime.now() - self.timer).total_seconds() > self.runtime:
                #     self.keyboard.press(self.key)
                #     self.timer = datetime.now()
                #     if not self.hold:
                #         logger.info("Hoding is 'No'. Press only once per round.")
                #         self.stop_action()
            # time.sleep(0.01)
                cur_time = (datetime.now() - self.timer).total_seconds()
                if self.first_round:
                    self.keyboard.press(self.key)
                    self.first_round = False
                elif cur_time < self.runtime:
                    if self.hold:
                        self.keyboard.press(self.key)
                elif cur_time < self.runtime + self.breaktime:
                    pass
                else:
                    self.timer = datetime.now()
                    self.first_round = True
class ActControl(threading.Thread):
    def __init__(self, content = "", *args, **kwargs):
        super(ActControl, self).__init__()
        self.content = content
        self.running = False
        self.program_running = True
        self.actions = []
        for act in self.content:
            action = self.create_action(act, *args, **kwargs)
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
        if not self.actions:
            logger.info("No action to run. Quit.")
            self.exit()
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

    def create_action(self, action, *args, **kwargs):
        items = action.keys()
        try:
            assert all(i in items for i in ["action", "actionOn", "runtime", "holding", "breaktime", "duration"])
        except AssertionError:
            logger.error(f'An act must contains ["action", "actionOn", "runtime", "holding", "breaktime", "duration"].')
            sys.exit(1)

        if action["action"] == "mouse":
            # Check the other args are numbers
            return ClickMouse(button = action['actionOn'], *args, **action, **kwargs)
        elif action["action"] == "key":
            return ClickKey(key = action['actionOn'], *args, **action, **kwargs)
        else:
            logger.error("action must be 'button' or 'key'")
            sys.exit(1)
        return None
                

class AutoClicker():
    def __init__(self, content = ""):
        self.content = content
        self.start_stop_key = KeyCode(char='s')
        self.exit_key = KeyCode(char='e')

    def on_press(self, key):
        if key == self.start_stop_key:
            if self.actControl.running:
                self.actControl.stop_action()
            else:
                self.actControl.start_action()

        elif key == self.exit_key:
            self.actControl.exit()
            self.listener.stop()

    def run_from_keys(self):
        self.mouse = mController()
        self.keyboard = kController()
        self.actControl = ActControl(self.content, keyboard = self.keyboard, mouse = self.mouse)
        self.actControl.start()

        with Listener(on_press=self.on_press) as self.listener:
            self.listener.join()
    
    def run(self):
        self.mouse = mController()
        self.keyboard = kController()
        self.actControl = ActControl(self.content, keyboard = self.keyboard, mouse = self.mouse)
        self.actControl.start()
        if self.actControl.running:
            self.actControl.stop_action()
        else:
            self.actControl.start_action()

    def stop(self):
        self.actControl.exit()
        if hasattr(self, "listener"):
            self.listener.stop()

    def serialize(self):
        return {
            'autoclicker':"abc",
        }
        

if __name__ == "__main__":
    with open("C:\\Jerry doc\\Jerry_prac\\python\\auto\\instance\\config.json", 'r') as f:
        content = json.load(f)
    autoclicker = AutoClicker(content)
    autoclicker.run_from_keys()
  