import time
from types import SimpleNamespace

from buttonbox_syncer.telemetry import TelemetryPoller
from buttonbox_syncer.dispatcher import EventDispatcher


def test_telemetry_poller_dispatches(monkeypatch):
    # fake requests.get
    responses = []

    class FakeResp:
        def __init__(self, data):
            self._data = data
            self.status_code = 200

        def json(self):
            return self._data

    def fake_get(url, timeout=1):
        return FakeResp({'ok': True, 'from': url})

    monkeypatch.setattr('buttonbox_syncer.telemetry.requests', SimpleNamespace(get=fake_get))

    disp = EventDispatcher()
    received = []
    disp.register('telemetry', lambda d: received.append(d))

    tp = TelemetryPoller({'TelemetryAPIAddress': 'http://x'}, disp, interval=0.01)
    tp.start()
    time.sleep(0.05)
    tp.stop()
    # allow thread to finish
    time.sleep(0.02)
    assert len(received) >= 1
    assert received[0].get('ok') is True
