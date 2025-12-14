from typing import Any
from . import logger as _logger
def get_nested_value(data: Any, path: str):
    try:
        keys = path.split('/') if path else []
        _logger.debugDeep(f"Getting nested value for path '{path}' with keys {keys} from data {data}")
        for k in keys:
            data = data[k]
        _logger.debugDeep(f"Retrieved nested value: {data}")
        return data
    except Exception:
        return None

def normalize_key_assignment(key):
    _logger.debugDeep(f"Normalizing key assignment: {key}")
    if isinstance(key, (list, tuple)):
        return key
    _logger.debugDeep(f"Normalized key assignment to single-element list: {[key]}")
    return key
