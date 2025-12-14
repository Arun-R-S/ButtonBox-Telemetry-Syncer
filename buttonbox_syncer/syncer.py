import keyboard
import time
from .utils import get_nested_value
from . import logger as _logger
from . import telemetry

class SyncManager:
    def __init__(self, cfg, dispatcher, joystick_index_correction=0, poll_interval=0.05):
        _logger.debugDeep(f"Initializing SyncManager with joystick_index_correction={joystick_index_correction}")
        self.cfg = cfg
        self.dispatcher = dispatcher
        self.telemetry = None
        self.button_states = {}
        self.joystick_index_correction = joystick_index_correction
        self.poll_interval = poll_interval
        dispatcher.register('telemetry', self._on_telemetry)
        dispatcher.register('button_changed', self._on_button_changed)
        dispatcher.register('cycle', self._on_cycle)

    def _on_telemetry(self, data):
        self.telemetry = data
        #_logger.debugDeep(f"Telemetry updated: {data}")

    def _on_button_changed(self, joystick_index, button_index, pressed):
        # apply correction for indexing if config requires
        mapping_list = self.cfg.get('JOYSTICK_BUTTON_MAPPINGS', [])
        _logger.debugDeep(f"_on_button_changed Mapping List {mapping_list}")
        _logger.debug(f"Button changed event received: joystick_index={joystick_index}, button_index={button_index}, pressed={pressed}")
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
                    _logger.info(f"Button {button_index} pressed state {pressed} does not match desired game state {desired_game_state} for telemetry path '{telemetry_path}'. Pressing key.")
                    self._press_key(cfg.get('keyToPress'))

    def _on_cycle(self, joystick_index, states):
        _logger.info(f"Cycle check tick : telemetry_present={bool(self.telemetry)} mappings={len(self.cfg.get('JOYSTICK_BUTTON_MAPPINGS', []))}")
        # For each configured mapping, compare the current telemetry value
        # with the physical joystick state for this cycle and press the
        # configured key when there's a mismatch. This ensures every
        # mapping is checked each iteration even when no physical change
        # event occurs.
        mapping_list = self.cfg.get('JOYSTICK_BUTTON_MAPPINGS', [])
        _logger.debugDeep(f"_on_cycle Mapping List {mapping_list}")
        for cfg in mapping_list:
            cfg_button = cfg.get('joystickButtonNumber') + (self.joystick_index_correction or 0)
            _logger.debug(f"Cycle check for button {cfg_button}")
            physical_state = states.get(cfg_button)
            _logger.debug(f"Physical state for button {cfg_button}: {physical_state}")
            telemetry_path = cfg.get('telemetryPathToSync')
            desired_game_state = None
            self.telemetry = telemetry.fetch
            if self.telemetry:
                desired_game_state = get_nested_value(self.telemetry, telemetry_path)
            else:
                _logger.debug(f"No telemetry data available during cycle check")
            _logger.debug(f"Cycle check: button {cfg_button}, physical_state={physical_state}, desired_game_state={desired_game_state} for telemetry path '{telemetry_path}'")
            # if telemetry value is not available or the physical button
            # is not present in states, skip this mapping
            if desired_game_state is None:
                _logger.warn(f"Cycle check: skipping button {cfg_button} due to missing telemetry.")
                continue
            if physical_state is None:
                _logger.warn(f"Cycle check: skipping button {cfg_button} due to missing physical state.")
                continue
            if bool(physical_state) != bool(desired_game_state):
                _logger.info(f"Cycle check: button {cfg_button} state {physical_state} != desired {desired_game_state} for '{telemetry_path}'. Pressing key.")
                self._press_key(cfg.get('keyToPress'))
        time.sleep(self.poll_interval)

    def _press_key(self, key):
        try:
            if isinstance(key, (list, tuple)):
                combo = f"{key[0]}+{key[1]}"
                _logger.debug(f"Pressing key combo: {combo}")
                keyboard.send(combo)
            elif isinstance(key, str):
                _logger.debug(f"Pressing key: {key}")
                keyboard.press_and_release(key)
            time.sleep(0.15)
        except Exception:
            raise
