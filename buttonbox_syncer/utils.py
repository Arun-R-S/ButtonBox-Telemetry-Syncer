from typing import Any
def get_nested_value(data: Any, path: str):
    try:
        keys = path.split('/') if path else []
        for k in keys:
            data = data[k]
        return data
    except Exception:
        return None

def normalize_key_assignment(key):
    if isinstance(key, (list, tuple)):
        return key
    return key
