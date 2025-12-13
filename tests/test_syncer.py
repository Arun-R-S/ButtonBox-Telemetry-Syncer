import time
from buttonbox_syncer.dispatcher import EventDispatcher
from buttonbox_syncer.syncer import SyncManager


class DummyKeyboard:
    def __init__(self):
        self.sent = []

    def press_and_release(self, key):
        self.sent.append(('press', key))

    def send(self, combo):
        self.sent.append(('send', combo))


def test_sync_manager_presses_key_on_mismatch(monkeypatch):
    cfg = {
        'JOYSTICK_BUTTON_MAPPINGS': [
            {
                'joystickButtonNumber': 0,
                'telemetryPathToSync': 'truck/electricOn',
                'keyToPress': 'k'
            }
        ],
        'isButtonNumberIndex': True
    }

    dispatcher = EventDispatcher()
    kb = DummyKeyboard()
    # monkeypatch keyboard used inside syncer module
    import buttonbox_syncer.syncer as s_mod
    monkeypatch.setattr(s_mod, 'keyboard', kb)
    # speed up sleep
    monkeypatch.setattr(s_mod, 'time', time)

    sync = SyncManager(cfg, dispatcher, joystick_index_correction=0)

    # set telemetry: game state OFF
    sync._on_telemetry({'truck': {'electricOn': False}})

    # physical pressed True != game False -> should press
    sync._on_button_changed(0, 0, True)
    assert ('press', 'k') in kb.sent

def test_sync_manager_sends_combo_for_list_key(monkeypatch):
    cfg = {
        'JOYSTICK_BUTTON_MAPPINGS': [
            {
                'joystickButtonNumber': 1,
                'telemetryPathToSync': 'truck/lightsBeaconOn',
                'keyToPress': ['shift', 'e']
            }
        ],
        'isButtonNumberIndex': True
    }
    dispatcher = EventDispatcher()
    kb = DummyKeyboard()
    import buttonbox_syncer.syncer as s_mod
    monkeypatch.setattr(s_mod, 'keyboard', kb)
    monkeypatch.setattr(s_mod, 'time', time)

    sync = SyncManager(cfg, dispatcher, joystick_index_correction=0)
    sync._on_telemetry({'truck': {'lightsBeaconOn': True}})

    # physical pressed False != game True -> should press key to turn OFF
    sync._on_button_changed(0, 1, False)
    assert any(item[0] == 'send' and item[1] == 'shift+e' for item in kb.sent)
