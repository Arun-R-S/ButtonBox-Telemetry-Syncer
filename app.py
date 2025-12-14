"""Slim orchestrator that wires modular components together."""
import buttonbox_syncer.config as _config
import buttonbox_syncer.logger as _logger
from buttonbox_syncer.dispatcher import EventDispatcher
from buttonbox_syncer.telemetry import TelemetryPoller
from buttonbox_syncer.joystick import JoystickMonitor
from buttonbox_syncer.syncer import SyncManager
import time
from colorama import Fore, Style, init as _color_init

# --- Console Color codes ---
COLOR_RESET = "\033[0m"

_color_init(autoreset=True)

ascii_art = f"""
{Fore.RED}   ░███                                      ░█████████       ░██████   {COLOR_RESET}
{Fore.RED}  ░██░██                                     ░██     ░██     ░██   ░██  {COLOR_RESET}
{Fore.RED} ░██  ░██  ░██░████ ░██    ░██ ░████████     ░██     ░██    ░██         {COLOR_RESET}
{Fore.YELLOW}░█████████ ░███     ░██    ░██ ░██    ░██    ░█████████      ░████████  {COLOR_RESET}
{Fore.YELLOW}░██    ░██ ░██      ░██    ░██ ░██    ░██    ░██   ░██              ░██ {COLOR_RESET}
{Fore.RED}░██    ░██ ░██      ░██   ░███ ░██    ░██    ░██    ░██      ░██   ░██  {COLOR_RESET}
{Fore.RED}░██    ░██ ░██       ░█████░██ ░██    ░██    ░██     ░██      ░██████   {COLOR_RESET}
{Fore.GREEN}🚛 Welcome to ETS2 ButtonBox Syncer 🚛
"""


def print_table(headers, rows):
    # ANSI Colors
    HEADER = "\033[1;36m"  # bright cyan
    RESET  = "\033[0m"

    # Double-line table borders
    TL = "╔"; TM = "╦"; TR = "╗"
    ML = "╠"; MM = "╬"; MR = "╣"
    BL = "╚"; BM = "╩"; BR = "╝"
    VL = "║"; HL = "═"

    # Compute column widths (auto-size)
    col_widths = []
    for col in range(len(headers)):
        max_len = len(headers[col])
        for row in rows:
            max_len = max(max_len, len(str(row[col])))
        col_widths.append(max_len)

    # Build border lines
    def border(left, mid, right):
        line = left
        for i, w in enumerate(col_widths):
            line += HL * (w + 2)
            line += mid if i < len(col_widths) - 1 else right
        return line

    top_border    = border(TL, TM, TR)
    middle_border = border(ML, MM, MR)
    bottom_border = border(BL, BM, BR)

    # Print table
    print(top_border)

    # Header row (colored)
    header_line = VL
    for i, h in enumerate(headers):
        header_line += f" {HEADER}{h}{RESET}{' ' * (col_widths[i] - len(h))} {VL}"
    print(header_line)

    print(middle_border)

    # Rows
    for row in rows:
        row_line = VL
        for i, col in enumerate(row):
            col = str(col)
            row_line += f" {col}{' ' * (col_widths[i] - len(col))} {VL}"
        print(row_line)

    print(bottom_border)


def main():
    print(ascii_art)
    time.sleep(2)
    cfg = _config.load_config()
    #_logger.configure(cfg)
    _logger.info('Info Logging initialized')
    _logger.warn('Warn Logging initialized')
    _logger.error('Error Logging initialized')
    _logger.debug('Debug Logging initialized')
    _logger.debugWarn('Debug-Warn Logging initialized')
    _logger.debugDeep('Debug-Deep Logging initialized')
    dispatcher = EventDispatcher()

    # joystick index correction: if config uses 1-based numbering convert to 0-based
    joystick_index_correction = -1 if not cfg.get('isButtonNumberIndex', True) else 0

    tp = TelemetryPoller(cfg, dispatcher, interval=0)

    # prompt for joystick selection
    jm = JoystickMonitor(cfg, dispatcher, telemetry_poller=tp, poll_interval=0)
    joysticks = jm.list_joysticks()
    if not joysticks:
        _logger.warn('No joysticks detected. Connect one and restart.')
        return
    rows = [[f"[{j['index']}]", j['name'], str(j['num_buttons'])] for j in joysticks]
    print_table(headers=["ID", "NAME", "NumButtons"], rows=rows)

    # allow refresh of joystick list with 'R' and exit with 'X'
    selected = None
    while selected is None:
        try:
            val = input('Select joystick by ID number (or X to exit, R to refresh): ')
            if val.lower() == 'x':
                return
            if val.lower() == 'r':
                joysticks = jm.list_joysticks()
                rows = [[f"[{j['index']}]", j['name'], str(j['num_buttons'])] for j in joysticks]
                print_table(headers=["ID", "NAME", "NumButtons"], rows=rows)
                continue
            idx = int(val)
            if any(j['index'] == idx for j in joysticks):
                selected = idx
            else:
                _logger.warn('Invalid selection')
        except ValueError:
            _logger.info('Enter a number')

    # small loading animation to match original UX
    def loading_animation(duration=1):
        print('Loading', end='', flush=True)
        start_time = time.time()
        while (time.time() - start_time) < duration:
            for dot_count in range(1, 4):
                print('\rLoading' + '.' * dot_count + ' ' * (3 - dot_count), end='', flush=True)
                time.sleep(0.25)
        print('\rLoading... Done! ')

    loading_animation(2)
    # start components
    jm.selected_index = selected
    local_poller_interval = cfg.get('Poller_Interval',0.3)
    _logger.info(f"Using poller interval: {local_poller_interval} seconds")
    sync = SyncManager(cfg, dispatcher, joystick_index_correction=joystick_index_correction, poll_interval=local_poller_interval)
    _logger.info('Starting telemetry poller and joystick monitor')
    # tp.start()
    jm.start()

    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        _logger.info('Shutting down...')
        # tp.stop()
        jm.stop()


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        _logger.error('Fatal error in main loop', exc=e)
    