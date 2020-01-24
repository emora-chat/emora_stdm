
import pytest
from emora_stdm.state_transition_dialogue_manager.settings import Settings

def test_constructor():
    s = Settings(x=1.0, y='hello')
    assert s == {'x': 1.0, 'y': 'hello'}

def test_update():
    s = Settings(x=1.0, y='hello')
    s.update(x=2.0, z='dog')
    assert s == {'x': 2.0, 'z': 'dog', 'y': 'hello'}

def test_getitem():
    s = Settings(x=1.0, y='hello')
    assert s.x == 1.0
    assert s.y == 'hello'