
import pytest

from emora_stdm.state_transition_dialogue_manager.utilities import AlterationTrackingDict


def test_alteration_tracking_dict():
    d = AlterationTrackingDict({'x': 1, 'y': 2})
    assert d.altered() == set()
    d['x'] = 2
    assert d.altered() == {'x'}
    d.update({'y': 2, 'z': 3})
    assert d.altered() == {'x', 'y', 'z'}