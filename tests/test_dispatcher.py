from buttonbox_syncer.dispatcher import EventDispatcher


def test_dispatch_calls_listener():
    ev = EventDispatcher()
    calls = []

    def cb(a, b=0):
        calls.append((a, b))

    ev.register('foo', cb)
    ev.dispatch('foo', 123, b=9)
    assert calls == [(123, 9)]

def test_unregister_listener():
    ev = EventDispatcher()
    calls = []

    def cb():
        calls.append(1)

    ev.register('x', cb)
    ev.unregister('x', cb)
    ev.dispatch('x')
    assert calls == []
