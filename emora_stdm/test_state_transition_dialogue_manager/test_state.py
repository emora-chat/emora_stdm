
from emora_stdm.state_transition_dialogue_manager.state import State
from enum import Enum


def test_enum_string_state():
    class MyStates(Enum):
        A = 0
        B = 1
    s1 = State(MyStates.A)
    s2 = State('MyStates.A')
    assert s1 == s2
    assert s1 == 'MyStates.A'
    assert s1 == MyStates.A
    assert s2 == s1
    assert s2 == 'MyStates.A'
    assert s2 == MyStates.A

def test_enum_tuple_state():
    class MyStates(Enum):
        A = 0
        B = 1
    s1 = State(MyStates.B)
    s2 = State('MyStates.B')
    s3 = State(('hello', 'MyStates.B'))
    assert s3[1] == s2
    assert s3[1] == s1
