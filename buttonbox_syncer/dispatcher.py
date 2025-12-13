class EventDispatcher:
    def __init__(self):
        self._listeners = {}

    def register(self, event_name, callback):
        self._listeners.setdefault(event_name, []).append(callback)

    def unregister(self, event_name, callback):
        if event_name in self._listeners:
            try:
                self._listeners[event_name].remove(callback)
            except ValueError:
                pass

    def dispatch(self, event_name, *args, **kwargs):
        for cb in list(self._listeners.get(event_name, [])):
            try:
                cb(*args, **kwargs)
            except Exception:
                # listener errors should not break dispatcher
                pass
