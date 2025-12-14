import threading
import requests
import time
from . import logger as _logger

class TelemetryPoller(threading.Thread):
    def __init__(self, cfg, dispatcher, interval=0.5):
        _logger.debugDeep(f"Initializing TelemetryPoller with interval={interval}")
        super().__init__(daemon=True)
        self.cfg = cfg
        self.dispatcher = dispatcher
        self.interval = interval
        self._stop = threading.Event()

    def stop(self):
        _logger.debug("TelemetryPoller stop signal set")
        self._stop.set()

    def run(self):
        addr = self.cfg.get('TelemetryAPIAddress')
        _logger.info(f"Starting TelemetryPoller with address: {addr}")
        while not self._stop.is_set():
            try:
                r = requests.get(addr, timeout=2)
                if r.status_code == 200:
                    data = r.json()
                    self.dispatcher.dispatch('telemetry', data)
            except Exception:
                # swallow — syncer will handle missing telemetry
                pass
            time.sleep(self.interval)

    def fetch_now(self):
        """Perform a single telemetry fetch synchronously and dispatch result.

        This can be called by other components (for example, before a
        button-state check) so the latest telemetry is available immediately.
        """
        addr = self.cfg.get('TelemetryAPIAddress')
        _logger.info(f"fetchN_now TelemetryPoller with address: {addr}")
        try:
            r = requests.get(addr, timeout=2)
            if r.status_code == 200:
                data = r.json()
                self.dispatcher.dispatch('telemetry', data)
                return data
            else:
                _logger.warn(f"fetch_now received non-200 status code: {r.status_code}")
        except Exception as e:
            _logger.error(f"fetch_now telemetry fetch failed:",e)
            pass
        return None
