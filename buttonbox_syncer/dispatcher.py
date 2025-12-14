from . import logger as _logger

class EventDispatcher:
    def __init__(self):
        self._listeners = {}

    def register(self, event_name, callback):
        _logger.debugDeep(f"Registering listener for event '{event_name}': {callback}")
        self._listeners.setdefault(event_name, []).append(callback)

    def unregister(self, event_name, callback):
        _logger.debugDeep(f"Unregistering listener for event '{event_name}': {callback}")
        if event_name in self._listeners:
            try:
                self._listeners[event_name].remove(callback)
            except ValueError:
                pass

    def dispatch(self, event_name, *args, **kwargs):
        _logger.debugDeep(f"Dispatching event '{event_name}' to {len(self._listeners.get(event_name, []))} listeners")
        for cb in list(self._listeners.get(event_name, [])):
            try:
                _logger.debugDeep(f"Calling listener for event '{event_name}': {cb}")
                cb(*args, **kwargs)
            except Exception:
                # listener errors should not break dispatcher
                pass
