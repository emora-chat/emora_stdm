
import pytest
from copy import deepcopy
from emora_stdm.state_transition_dialogue_manager.utilities import \
    AlterationTrackingDict, json_deserialize_flexible, json_serialize_flexible


def test_alteration_tracking_dict():
    d = AlterationTrackingDict({'x': 1, 'y': 2})
    assert d.altered() == set()
    d['x'] = 2
    assert d.altered() == {'x'}
    d.update({'y': 2, 'z': 3})
    assert d.altered() == {'x', 'y', 'z'}


def test_json_serialize_flexible():
    special_one = object()
    special_two = object()
    mapping = {
        special_one: 'ONE',
        special_two: 'TWO'
    }
    rmapping = {v: k for k, v in mapping.items()}

    original_obj = [
        {'one': 1, 'two': 2, 'three': [3, 4, 5, special_one, {'hello': 'there'}], 'four': (True, special_two)}
    ]

    to_serialize = [
        {'one': 1, 'two': 2, 'three': [3, 4, 5, special_one, {'hello': 'there'}], 'four': (True, special_two)}
    ]

    idx = 0
    for obj in to_serialize:
        serialization = json_serialize_flexible(obj, mapping)
        deserialization = json_deserialize_flexible(serialization, rmapping)
        assert original_obj[idx] == deserialization
        idx += 1