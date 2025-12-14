import os
import sys
import json

def load_config():
    config_path = "config.json"
    if getattr(sys, 'frozen', False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(__file__)
    path = os.path.join(base, 'config.json')
    if not os.path.exists(path):
        # fallback to current working directory
        path = os.path.join(os.getcwd(), 'config.json')
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


# Module-level CONFIG: loaded once on import and reloadable via `reload_config()`.
CONFIG = None

def reload_config():
    """Reload the configuration from disk into the module-level `CONFIG`.

    This wraps `load_config()` and protects callers from exceptions by
    falling back to an empty dict on error.
    """
    global CONFIG
    try:
        CONFIG = load_config()
    except Exception:
        CONFIG = {}


# Load config at import time (best-effort)
reload_config()
