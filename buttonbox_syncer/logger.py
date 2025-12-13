from datetime import datetime
import colorama
colorama.init()

# --- Console Color codes ---
COLOR_RESET = "\033[0m"
COLOR_DEBUG = "\033[36m"        # Cyan
COLOR_DEBUG_DEEP = "\033[36m"   # Cyan
COLOR_DEBUG_WARN = "\033[95m"   # Bright Magenta
COLOR_INFO  = "\033[32m"        # Green
COLOR_WARN  = "\033[33m"        # Yellow
COLOR_ERROR = "\033[31m"        # Red

DEFAULT_CONFIG = {
    "LoggingLevels": {
        "INFO": True,
        "WARN": True,
        "ERROR": True,
        "DEBUG": False,
        "DEBUGWARN": False,
        "DEBUGDEEP": False,
    }
}

# start with a safe copy of defaults
_config = DEFAULT_CONFIG.copy()


def configure(config_dict):
    """Accept a config dict and merge it with sane defaults.

    This function tolerates None or malformed input and ensures
    `_config` is always a dict with a `LoggingLevels` mapping.
    """
    global _config
    if not isinstance(config_dict, dict):
        return
    # start from defaults and merge
    new_conf = DEFAULT_CONFIG.copy()
    lvl = config_dict.get('LoggingLevels')
    if isinstance(lvl, dict):
        new_conf['LoggingLevels'].update(lvl)
    # copy other top-level keys through
    for k, v in config_dict.items():
        if k != 'LoggingLevels':
            new_conf[k] = v
    _config = new_conf

def _timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def _log(level, color, message, exc=None):
    try:
        enabled = bool(_config.get('LoggingLevels', {}).get(level, False))
    except Exception:
        enabled = False
    # always show WARN/ERROR unless explicitly disabled
    if enabled or level in ('ERROR', 'WARN'):
        print(f"[{_timestamp()}] {color}{level:<7}{COLOR_RESET} {message} {f'Exception: {exc}' if exc else ''}")

def info(msg):
    try:
        if bool(_config.get('LoggingLevels', {}).get('INFO', False)):
            _log('INFO', COLOR_INFO, msg)
    except Exception:
        # on any config error, default to printing info
        _log('INFO', COLOR_INFO, msg)

def debug(msg):
    try:
        if bool(_config.get('LoggingLevels', {}).get('DEBUG', False)):
            _log('DEBUG', COLOR_DEBUG, msg)
    except Exception:
        pass

def debugWarn(msg):
    try:
        if bool(_config.get('LoggingLevels', {}).get('DEBUGWARN', False)):
            _log('DEBUG-WARN', COLOR_DEBUG_WARN, msg)
    except Exception:
        pass

def debugDeep(msg):
    try:
        if bool(_config.get('LoggingLevels', {}).get('DEBUGDEEP', False)):
            _log('DEBUG-DEEP', COLOR_DEBUG_DEEP, msg)
    except Exception:
        pass

def warn(msg):
    try:
        if bool(_config.get('LoggingLevels', {}).get('WARN', False)):
            _log('WARN', COLOR_WARN, msg)
    except Exception:
        _log('WARN', COLOR_WARN, msg)

def error(msg, exc=None):
    try:
        if bool(_config.get('LoggingLevels', {}).get('ERROR', True)):
            _log('ERROR', COLOR_ERROR, msg, exc)
    except Exception:
        _log('ERROR', COLOR_ERROR, msg, exc)
