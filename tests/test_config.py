import json
from pathlib import Path

from buttonbox_syncer.config import load_config


def test_load_config_prefers_cwd(tmp_path, monkeypatch):
    cfg = {"foo": "bar"}
    p = tmp_path / 'config.json'
    p.write_text(json.dumps(cfg))
    monkeypatch.chdir(tmp_path)
    loaded = load_config()
    assert isinstance(loaded, dict)
    assert loaded.get('foo') == 'bar'
