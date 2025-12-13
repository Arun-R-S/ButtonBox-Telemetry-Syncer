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
