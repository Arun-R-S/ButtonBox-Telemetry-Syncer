import threading
import pygame
import time

class JoystickMonitor(threading.Thread):
    def __init__(self, cfg, dispatcher, selected_index=0, poll_interval=0.05):
        super().__init__(daemon=True)
        self.cfg = cfg
        self.dispatcher = dispatcher
        self.selected_index = selected_index
        self.poll_interval = poll_interval
        self._stop = threading.Event()
        self._states = {}

    def stop(self):
        self._stop.set()

    def list_joysticks(self):
        pygame.init()
        pygame.joystick.init()
        count = pygame.joystick.get_count()
        joysticks = []
        for i in range(count):
            j = pygame.joystick.Joystick(i)
            j.init()
            joysticks.append({'index': i, 'name': j.get_name(), 'num_buttons': j.get_numbuttons()})
        return joysticks

    def run(self):
        pygame.init()
        pygame.joystick.init()
        try:
            js = pygame.joystick.Joystick(self.selected_index)
            js.init()
        except Exception:
            return

        # initial state
        for b in range(js.get_numbuttons()):
            self._states[b] = js.get_button(b)

        while not self._stop.is_set():
            pygame.event.pump()
            for b in range(js.get_numbuttons()):
                state = js.get_button(b)
                if state != self._states.get(b):
                    self._states[b] = state
                    # dispatch button change
                    self.dispatcher.dispatch('button_changed', self.selected_index, b, bool(state))
            time.sleep(self.poll_interval)
