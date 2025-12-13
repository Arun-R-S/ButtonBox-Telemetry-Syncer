import time
from types import SimpleNamespace

from buttonbox_syncer.joystick import JoystickMonitor
from buttonbox_syncer.dispatcher import EventDispatcher


def test_list_joysticks_with_fake_pygame(monkeypatch):
    # fake pygame module
    class FakeJS:
        def __init__(self, idx):
            self._idx = idx

        def init(self):
            pass

        def get_name(self):
            return f"JS-{self._idx}"

        def get_numbuttons(self):
            return 2

    fake_joystick = SimpleNamespace(
        get_count=lambda: 1,
        Joystick=lambda i: FakeJS(i)
    )

    fake_pygame = SimpleNamespace(
        init=lambda: None,
        joystick=fake_joystick
    )

    monkeypatch.setattr('buttonbox_syncer.joystick.pygame', fake_pygame)

    jm = JoystickMonitor({}, EventDispatcher())
    lst = jm.list_joysticks()
    assert isinstance(lst, list)
    assert lst[0]['name'] == 'JS-0'


def test_run_dispatches_button_change(monkeypatch):
    # create a fake joystick that changes state once
    class FakeJSRun:
        def __init__(self):
            self._calls = 0

        def init(self):
            pass

        def get_numbuttons(self):
            return 1

        def get_button(self, b):
            # first call: 0, second: 1, then always 1
            self._calls += 1
            return 0 if self._calls == 1 else 1

    fake_joystick = SimpleNamespace(
        get_count=lambda: 1,
        Joystick=lambda i: FakeJSRun()
    )

    fake_pygame = SimpleNamespace(
        init=lambda: None,
        joystick=fake_joystick,
        event=SimpleNamespace(pump=lambda: None)
    )

    monkeypatch.setattr('buttonbox_syncer.joystick.pygame', fake_pygame)

    disp = EventDispatcher()
    events = []
    disp.register('button_changed', lambda js_idx, b_idx, state: events.append((js_idx, b_idx, state)))

    jm = JoystickMonitor({}, disp, selected_index=0, poll_interval=0.01)
    # run in background
    jm.start()
    time.sleep(0.05)
    jm.stop()
    time.sleep(0.02)
    assert any(evt[1] == 0 and evt[2] is True for evt in events)
