"""Slim orchestrator that wires modular components together."""
from buttonbox_syncer.config import load_config
from buttonbox_syncer.logger import configure, info, debug, warn, error
from buttonbox_syncer.dispatcher import EventDispatcher
from buttonbox_syncer.telemetry import TelemetryPoller
from buttonbox_syncer.joystick import JoystickMonitor
from buttonbox_syncer.syncer import SyncManager
import time


def main():
    cfg = load_config()
    configure(cfg)

    dispatcher = EventDispatcher()

    # joystick index correction: if config uses 1-based numbering convert to 0-based
    joystick_index_correction = -1 if not cfg.get('isButtonNumberIndex', True) else 0

    tp = TelemetryPoller(cfg, dispatcher, interval=0.5)

    # prompt for joystick selection
    jm = JoystickMonitor(cfg, dispatcher)
    joysticks = jm.list_joysticks()
    if not joysticks:
        warn('No joysticks detected. Connect one and restart.')
        return
    print('Connected joysticks:')
    for j in joysticks:
        print(f"[{j['index']}] {j['name']} ({j['num_buttons']} buttons)")

    selected = None
    while selected is None:
        try:
            val = input('Select joystick by ID number (or X to exit): ')
            if val.lower() == 'x':
                return
            idx = int(val)
            if any(j['index'] == idx for j in joysticks):
                selected = idx
            else:
                print('Invalid selection')
        except ValueError:
            print('Enter a number')

    # start components
    jm.selected_index = selected
    sync = SyncManager(cfg, dispatcher, joystick_index_correction=joystick_index_correction)
    info('Starting telemetry poller and joystick monitor')
    tp.start()
    jm.start()

    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        info('Shutting down...')
        tp.stop()
        jm.stop()


if __name__ == '__main__':
    main()
    