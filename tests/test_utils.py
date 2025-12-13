import pytest
from buttonbox_syncer.utils import get_nested_value

def test_get_nested_value_found():
    data = {'truck': {'electricOn': True, 'nested': {'val': 5}}}
    assert get_nested_value(data, 'truck/electricOn') is True
    assert get_nested_value(data, 'truck/nested/val') == 5

def test_get_nested_value_missing():
    data = {'a': {'b': 1}}
    assert get_nested_value(data, 'a/c') is None
    assert get_nested_value({}, 'x/y/z') is None
