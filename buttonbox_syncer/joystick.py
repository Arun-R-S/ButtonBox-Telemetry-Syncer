import threading
import pygame
import time
from . import logger as _logger

class JoystickMonitor(threading.Thread):
    def __init__(self, cfg, dispatcher, selected_index=0, poll_interval=0.05):
        _logger.debugDeep(f"Initializing JoystickMonitor with selected_index={selected_index}, poll_interval={poll_interval}")
        super().__init__(daemon=True)
        self.cfg = cfg
        self.dispatcher = dispatcher
        self.selected_index = selected_index
        self.poll_interval = poll_interval
        self._stop = threading.Event()
        self._states = {}
        _logger.debug("JoystickMonitor initialized")

    def stop(self):
        self._stop.set()
        _logger.debug("JoystickMonitor stop signal set")

    def list_joysticks(self):
        pygame.init()
        _logger.debug("Listing joysticks")
        # Some test fakes may not provide a `init` function; call if present.
        try:
            init_fn = getattr(pygame.joystick, 'init', None)
            _logger.debugDeep(f"Joystick init function: {init_fn}")
            if callable(init_fn):
                init_fn()
                _logger.debug("Pygame joystick module initialized")
        except Exception:
            pass
        count = pygame.joystick.get_count()
        _logger.debugDeep(f"Number of joysticks detected: {count}")
        joysticks = []
        for i in range(count):
            j = pygame.joystick.Joystick(i)
            j.init()
            joysticks.append({'index': i, 'name': j.get_name(), 'num_buttons': j.get_numbuttons()})
        return joysticks

    def run(self):
        pygame.init()
        _logger.debug("JoystickMonitor thread started")
        try:
            init_fn = getattr(pygame.joystick, 'init', None)
            _logger.debugDeep(f"Joystick init function: {init_fn}")
            if callable(init_fn):
                init_fn()
        except Exception:
            pass
        try:
            js = pygame.joystick.Joystick(self.selected_index)
            _logger.info(f"Selected joystick: {js.get_id()} - {js.get_name()} with {js.get_numbuttons()} buttons")
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
