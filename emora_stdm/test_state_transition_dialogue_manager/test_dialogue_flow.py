
import pytest
from emora_stdm.state_transition_dialogue_manager.dialogue_flow import DialogueFlow, Speaker
from emora_stdm.state_transition_dialogue_manager.natex_nlu import NatexNLU
from emora_stdm.state_transition_dialogue_manager.natex_nlg import NatexNLG
from enum import Enum

class States(Enum):
    A = 0
    B = 1
    C = 2
    D = 3


def test_constructor():
    df = DialogueFlow(States.A)
    assert df.state() == States.A
    assert df.speaker() == Speaker.SYSTEM

def test_add_transitions():
    df = DialogueFlow(States.A)
    df.add_system_transition(States.A, States.B, 'hello')
    df.add_user_transition(States.B, States.C, '[{hi, hello, hey, [how, you]}]')
    df.add_user_transition(States.B, States.D, '[{dog, cat, parrot}]')
    df.add_system_transition(States.D, States.A, 'so')
    assert df.arcs() == {
        (States.A, States.B, DialogueFlow.Speaker.SYSTEM),
        (States.B, States.C, DialogueFlow.Speaker.USER),
        (States.B, States.D, DialogueFlow.Speaker.USER),
        (States.D, States.A, DialogueFlow.Speaker.SYSTEM)
    }
    assert isinstance(df.transition_natex(States.A, States.B, Speaker.SYSTEM), NatexNLG)
    assert isinstance(df.transition_natex(States.B, States.C, Speaker.USER), NatexNLU)

def test_system_transition():
    df = DialogueFlow(States.A)
    df.add_system_transition(States.A, States.B, 'hello')
    assert df.system_transition() == ('hello', States.B)

def test_user_transition():
    df = DialogueFlow(States.B)
    df.add_user_transition(States.B, States.C, '[{hi, hello, hey, [how, you]}]')
    assert df.user_transition('oh hey there') == States.C

