import keyboard
import time
from .utils import get_nested_value

class SyncManager:
    def __init__(self, cfg, dispatcher, joystick_index_correction=0):
        self.cfg = cfg
        self.dispatcher = dispatcher
        self.telemetry = None
        self.button_states = {}
        self.joystick_index_correction = joystick_index_correction
        dispatcher.register('telemetry', self._on_telemetry)
        dispatcher.register('button_changed', self._on_button_changed)

    def _on_telemetry(self, data):
        self.telemetry = data

    def _on_button_changed(self, joystick_index, button_index, pressed):
        # apply correction for indexing if config requires
        mapping_list = self.cfg.get('JOYSTICK_BUTTON_MAPPINGS', [])
        for cfg in mapping_list:
            cfg_button = cfg.get('joystickButtonNumber') + (self.joystick_index_correction or 0)
            if cfg_button == button_index:
                telemetry_path = cfg.get('telemetryPathToSync')
                desired_game_state = None
                if self.telemetry:
                    desired_game_state = get_nested_value(self.telemetry, telemetry_path)
                # if telemetry says the same as physical, do nothing
                if desired_game_state is None:
                    # cannot compare — ignore
                    return
                # if mismatch then press key
                if bool(pressed) != bool(desired_game_state):
                    self._press_key(cfg.get('keyToPress'))

    def _press_key(self, key):
        try:
            if isinstance(key, (list, tuple)):
                combo = f"{key[0]}+{key[1]}"
                keyboard.send(combo)
            elif isinstance(key, str):
                keyboard.press_and_release(key)
            time.sleep(0.15)
        except Exception:
            pass
