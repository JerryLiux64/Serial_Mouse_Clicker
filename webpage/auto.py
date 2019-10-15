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
    def __init__(self, duration: float , holding: str, repeat: int, breaktime = 0, *args, **kwargs):
        super(Action, self).__init__()
        self.duration = float(duration)
        self.running = False
        self.program_running = True
        self.hold = {"Yes":True, "No":False}[holding]
        self.repeat = int(repeat)
        # self.action = action
        self.breaktime = float(breaktime)
        self.timer = 0

    def start_action(self):
        logger.info(f"Start {self.__class__.__name__}.")
        self.timer = datetime.now()
        self.ready_to_act = True
        self.iterCount = 0
        self.holding = False
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
        super().__init__(*args, **kwargs)
        logger.info(f"{self.__class__.__name__} on \'{actionOn}\', {f'hold for {self.duration}s ' if self.hold else ''}then take a break of {self.breaktime}s. Repeat for {self.repeat} times.")

    def run(self):
        # print(f"{ClickMouse.__class__}: threading.current_thread()")
        while self.program_running:
            while self.running:
                cur_time = (datetime.now() - self.timer).total_seconds()
                if self.ready_to_act:
                    if self.hold:
                        logger.info(f"Press mouse on {self.button}")
                        self.mouse.press(self.button)
                        self.holding = True
                    else:
                        logger.info(f"Click mouse on {self.button}")
                        self.mouse.click(self.button)
                    self.ready_to_act = False
                elif cur_time < self.duration:
                    pass
                elif cur_time < self.duration + self.breaktime:
                    # release hoding after self.duration
                    if self.holding:
                        logger.info(f"Release mouse on {self.button}")
                        self.mouse.release(self.button)
                        self.holding = False
                else:
                    # release hoding in case self.breaktime = 0
                    if self.holding:
                        logger.info(f"Release mouse on {self.button}")
                        self.mouse.release(self.button)
                        self.holding = False
                    self.iterCount = self.iterCount + 1
                    if self.iterCount >= self.repeat:
                        self.stop_action()
                    else:
                        self.ready_to_act = True
                        self.timer = datetime.now()
            time.sleep(0.01)

class ScrollMouse(Action):
    def __init__(self, actionOn: int, mouse = "", *args, **kwargs):
        self.mouse = mouse
        self.scroll_range = int(actionOn)
        super().__init__(*args, **kwargs)
        logger.info(f"{self.__class__.__name__} \'{actionOn}\', then take a break of {self.breaktime}s. Repeat for {self.repeat} times.")

    def run(self):
        # print(f"{ClickMouse.__class__}: threading.current_thread()")
        while self.program_running:
            while self.running:
                cur_time = (datetime.now() - self.timer).total_seconds()
                if self.ready_to_act:
                    logger.info(f"Scroll mouse {self.scroll_range}")
                    self.mouse.scroll(0, self.scroll_range)
                    self.ready_to_act = False
                elif cur_time < self.duration + self.breaktime:
                    pass
                else:
                    self.iterCount = self.iterCount + 1
                    if self.iterCount >= self.repeat:
                        self.stop_action()
                    else:
                        self.ready_to_act = True
                        self.timer = datetime.now()
            time.sleep(0.01)

class ClickKey(Action):            
    def __init__(self, actionOn: str, keyboard = "", *args, **kwargs):
        self.key = KeyCode.from_char(actionOn)
        self.keyboard = keyboard
        super().__init__(*args, **kwargs)
        logger.info(f"{self.__class__.__name__} on \'{actionOn}\', {f'hold for {self.duration}s ' if self.hold else ''}then take a break of {self.breaktime}s. Repeat for {self.repeat} times.")


    def run(self):
        # print(f"{ClickKey.__name__}: threading.current_thread()")
        while self.program_running:
            while self.running:
                cur_time = (datetime.now() - self.timer).total_seconds()
                if self.ready_to_act:
                    if self.hold:
                        logger.info(f"Press key on {self.key}")
                        self.keyboard.press(self.key)
                        self.holding = True
                    else:
                        logger.info(f"Click keyboard on {self.key}")
                        self.keyboard.press(self.key)
                        self.keyboard.release(self.key)
                    self.ready_to_act = False
                elif cur_time < self.duration:
                    pass
                elif cur_time < self.duration + self.breaktime:
                    # release hoding after self.duration
                    if self.holding:
                        logger.info(f"Release keyboard on {self.key}")
                        self.keyboard.release(self.key)
                        self.holding = False
                else:
                    # release hoding in case self.breaktime = 0
                    if self.holding:
                        logger.info(f"Release keyboard on {self.key}")
                        self.keyboard.release(self.key)
                        self.holding = False
                    self.iterCount = self.iterCount + 1
                    if self.iterCount >= self.repeat:
                        self.stop_action()
                    else:
                        self.ready_to_act = True
                        self.timer = datetime.now()
            time.sleep(0.01)

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
        self.nextAction = True 
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
                if self.nextAction: 
                    self.nextAction = False
                    cur_action.start_action()

                elif not cur_action.running and cur_action.iterCount == cur_action.repeat:
                    self.actCount = (self.actCount + 1)%len(self.actions)
                    self.nextAction = True
            # time.sleep(0.1)

    def create_action(self, action, *args, **kwargs):
        items = action.keys()
        try:
            assert all(i in items for i in ["action", "actionOn", "duration", "holding", "breaktime", "repeat"])
        except AssertionError:
            logger.error(f'An act must contains ["action", "actionOn", "duration", "holding", "breaktime", "repeat"].')
            sys.exit(1)

        if action["action"] == "mouse":
            # Check the other args are numbers
            # return ClickMouse(button = action['actionOn'], *args, **action, **kwargs)
            return ClickMouse(*args, **action, **kwargs)
        elif action["action"] == "mouse_scroll":
            return ScrollMouse(*args, **action, **kwargs)
            # return ScrollMouse(key = action['actionOn'], *args, **action, **kwargs)
        elif action["action"] == "key":
            # return ClickKey(key = action['actionOn'], *args, **action, **kwargs)
            return ClickKey(*args, **action, **kwargs)
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
  