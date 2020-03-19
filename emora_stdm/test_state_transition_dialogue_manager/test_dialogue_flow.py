
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
    E = 4

def test_constructor():
    df = DialogueFlow(States.A)
    assert df.state() == States.A
    assert df.speaker() == Speaker.SYSTEM

def test_add_transitions():
    df = DialogueFlow('States.A')
    df.add_system_transition('States.A', 'States.B', 'hello')
    df.add_user_transition('States.B', 'States.C', '[{hi, hello, hey, [how, you]}]')
    df.add_user_transition('States.B', 'States.D', '[{dog, cat, parrot}]')
    df.add_system_transition('States.D', 'States.A', 'so')
    assert df.graph().arcs() == {
        ('States.A', 'States.B', DialogueFlow.Speaker.SYSTEM),
        ('States.B', 'States.C', DialogueFlow.Speaker.USER),
        ('States.B', 'States.D', DialogueFlow.Speaker.USER),
        ('States.D', 'States.A', DialogueFlow.Speaker.SYSTEM)
    }
    assert isinstance(df.transition_natex('States.A', 'States.B', Speaker.SYSTEM), NatexNLG)
    assert isinstance(df.transition_natex('States.B', 'States.C', Speaker.USER), NatexNLU)

def test_single_system_transition():
    df = DialogueFlow(States.A)
    df.add_system_transition(States.A, States.B, 'hello')
    assert df.system_transition(df.state()) == ('hello', States.B)

def test_single_user_transition():
    df = DialogueFlow(States.B)
    df.add_user_transition(States.B, States.C, '[{hi, hello, hey, [how, you]}]')
    assert df.user_transition('oh hey there', df.state()) == States.C

def test_system_transition():
    for _ in range(20):
        df = DialogueFlow(States.A)
        df.add_system_transition(States.A, States.B, 'hello', score=2.0)
        df.add_system_transition(States.A, States.C, 'hey')
        assert df.system_transition(df.state()) == ('hello', States.B)
        df = DialogueFlow(States.A)
        df.add_system_transition(States.A, States.B, 'hello')
        df.add_system_transition(States.A, States.C, 'hey', score=2.0)
        assert df.system_transition(df.state()) == ('hey', States.C)

def test_user_transition():
    df = DialogueFlow(States.B)
    df.add_user_transition(States.B, States.C, '[{hi, hello, hey, [how, you]}]')
    df.add_user_transition(States.B, States.D, '[{bye, goodbye, see you, see ya, later}]')
    assert df.user_transition('oh hey there', df.state()) == States.C
    assert df.user_transition('well see ya later', df.state()) == States.D

def test_check():
    df = DialogueFlow(States.A)
    df.add_state(States.B, error_successor=States.C)
    df.add_state(States.D, error_successor=States.A)
    df.add_system_transition(States.A, States.B, 'hello')
    df.add_user_transition(States.B, States.C, '[{hi, hello, hey, [how, you]}]')
    df.add_user_transition(States.B, States.A, '[{bye, goodbye, see you, see ya, later}]')
    df.add_system_transition(States.C, States.D, 'ok')
    assert df.check()
    df = DialogueFlow(States.A)
    df.add_state(States.B, error_successor=States.C)
    df.add_system_transition(States.A, States.B, 'hello')
    df.add_user_transition(States.B, States.C, '[{hi, hello, hey, [how, you]}]')
    df.add_user_transition(States.B, States.A, '[{bye, goodbye, see you, see ya, later}]')
    df.add_system_transition(States.C, States.D, 'ok')
    assert not df.check()
    df = DialogueFlow(States.A)
    df.add_state(States.B, error_successor=States.C)
    df.add_state(States.D, error_successor=States.A)
    df.add_system_transition(States.A, States.B, 'hello')
    df.add_user_transition(States.B, States.C, '[{hi, hello, hey, [how, you]}]')
    df.add_user_transition(States.B, States.A, '[{bye, goodbye, see you, see ya, later}]')
    df.add_system_transition(States.C, States.D, 'ok then $X alright')
    assert not df.check()

def test_global_transitions():
    df = DialogueFlow(States.A)
    df.add_state(States.A, global_nlu='{hi, hey, hello}')
    df.add_state(States.B, error_successor=States.C)
    df.add_state(States.D, error_successor=States.D)
    df.add_system_transition(States.A, States.B, 'hello')
    df.add_user_transition(States.B, States.C, '[how, you]')
    df.add_user_transition(States.B, States.A, '[{bye, goodbye, see you, see ya, later}]')
    df.add_system_transition(States.C, States.D, 'ok')
    assert df.transition_natex(States.D, States.A, Speaker.USER).expression() == '{hi, hey, hello}'
    df = DialogueFlow(States.A)
    df.add_state(States.B, error_successor=States.C)
    df.add_state(States.D, error_successor=States.D)
    df.add_system_transition(States.A, States.B, 'hello')
    df.add_user_transition(States.B, States.C, '[how, you]')
    df.add_user_transition(States.B, States.A, '[{bye, goodbye, see you, see ya, later}]')
    df.add_system_transition(States.C, States.D, 'ok')
    df.update_state_settings(States.A, global_nlu='{hi, hey, hello}')
    assert df.transition_natex(States.D, States.A, Speaker.USER).expression() == '{hi, hey, hello}'

def test_user_multi_hop():
    df = DialogueFlow(States.A, initial_speaker=Speaker.USER)
    df.add_state(States.B, error_successor=States.B, user_multi_hop=True)
    df.add_state(States.C, error_successor=States.A, user_multi_hop=True)
    df.add_state(States.D, error_successor=States.A)
    df.add_state(States.E, error_successor=States.A)
    df.add_user_transition(States.A, States.B, '[{hey, hello}]')
    df.add_user_transition(States.A, States.C, '[{excuse, pardon}]')
    df.add_user_transition(States.B, States.D, '[how, you]')
    df.add_user_transition(States.C, States.E, '[{where, how, what}]')
    df.set_state(States.A)
    df.user_turn('hey', debugging=False)
    assert df.state() == States.B
    df.set_state(States.A)
    df.set_speaker(Speaker.USER)
    df.user_turn('hey how are you')
    assert df.state() == States.D
    df.set_state(States.A)
    df.set_speaker(Speaker.USER)
    df.user_turn('excuse me where do i go')
    assert df.state() == States.E
    df.set_state(States.A)
    df.set_speaker(Speaker.USER)
    df.user_turn('excuse me')
    assert df.state() == States.A

def test_system_multi_hop():
    df = DialogueFlow(States.A, initial_speaker=Speaker.SYSTEM)
    df.add_state(States.B, error_successor=States.B, system_multi_hop=True)
    df.add_state(States.C, error_successor=States.A, system_multi_hop=True)
    df.add_state(States.D, error_successor=States.A)
    df.add_state(States.E, error_successor=States.A)
    df.add_system_transition(States.A, States.B, '{hey, hello}')
    df.add_system_transition(States.A, States.C, 'excuse me')
    df.add_system_transition(States.B, States.D, 'how are you')
    df.add_system_transition(States.C, States.E, 'what')
    for _ in range(100):
        df.set_state(States.A)
        df.set_speaker(Speaker.SYSTEM)
        response = df.system_turn()
        assert response in {'hey how are you', 'hello how are you',
                            'excuse me what'}

def test_nlg_novelty():
    df = DialogueFlow(States.A, initial_speaker=Speaker.SYSTEM)
    df.add_state(States.B, error_successor=States.A)
    df.add_state(States.C, error_successor=States.A)
    df.add_system_transition(States.A, States.B, 'B')
    df.add_system_transition(States.A, States.C, 'C')

    for _ in range(100):
        df.reset()
        df.set_state(States.A)
        df.set_speaker(Speaker.SYSTEM)
        response = df.system_turn()
        df.user_turn("")
        response2 = df.system_turn()
        assert response != response2

    df = DialogueFlow(States.A, initial_speaker=Speaker.SYSTEM)
    df.add_state(States.B, error_successor=States.A)
    df.add_state(States.C, error_successor=States.A)
    df.add_state(States.D, error_successor=States.A)
    df.add_state(States.E, error_successor=States.A)
    df.add_system_transition(States.A, States.B, 'B')
    df.add_system_transition(States.A, States.C, 'C')
    df.add_system_transition(States.A, States.D, 'D')
    df.add_system_transition(States.A, States.E, 'E')

    for _ in range(100):
        df.reset()
        df.set_state(States.A)
        df.set_speaker(Speaker.SYSTEM)
        response = df.system_turn()
        df.user_turn("")
        response2 = df.system_turn()
        assert response != response2

    mem_val = 2

    df = DialogueFlow(States.A, initial_speaker=Speaker.SYSTEM)
    df.add_state(States.A, memory=mem_val)
    df.add_state(States.B, error_successor=States.A)
    df.add_state(States.C, error_successor=States.A)
    df.add_state(States.D, error_successor=States.A)
    df.add_state(States.E, error_successor=States.A)
    df.add_system_transition(States.A, States.B, 'B')
    df.add_system_transition(States.A, States.C, 'C')
    df.add_system_transition(States.A, States.D, 'D')
    df.add_system_transition(States.A, States.E, 'E')

    prev_turns = [None,None]
    idx = 0
    for _ in range(100):
        df.set_state(States.A)
        df.set_speaker(Speaker.SYSTEM)
        response = df.system_turn()
        assert response not in prev_turns
        prev_turns[idx] = response
        idx = (idx + 1) % mem_val
        df.user_turn("")
        response2 = df.system_turn()
        assert response2 not in prev_turns
        prev_turns[idx] = response2
        idx = (idx + 1) % mem_val

def test_reset():
    df = DialogueFlow(States.A, initial_speaker=Speaker.SYSTEM)
    df.add_state(States.B, error_successor=States.E)
    df.add_state(States.C, error_successor=States.E)
    df.add_system_transition(States.A, States.B, 'B')
    df.add_system_transition(States.A, States.C, 'C')
    df.add_system_transition(States.E, States.E, 'E')

    response = df.system_turn()
    df.user_turn("")
    assert df.state() == States.E

    df.reset()
    assert df.state() == States.A
    assert df.speaker() == Speaker.SYSTEM
    response = df.system_turn()
    df.user_turn("")
    assert df.state() == States.E
    df.system_turn()
    assert df.state() == States.E

    df.reset()
    assert df.state() == States.A
    assert df.speaker() == Speaker.SYSTEM
    response = df.system_turn()
    df.user_turn("")
    assert df.state() == States.E
    df.system_turn()
    assert df.state() == States.E


def test_information_state_based_dialogue():
    df = DialogueFlow('root', initial_speaker=Speaker.USER)
    df.add_user_transition('root', 'one', '$x=[{cat, dog}]')
    df.set_error_successor('root', 'one')
    df.add_system_transition('one', 'root', 'i am a stupid state machine')
    df.add_update_rule('[$x={ice cream, candy}]')
    df.add_update_rule('#ANY($x=candy)', '$y=blah')
    df.add_update_rule('#ANY($y=blah)', 'i am a smart info state manager (2.0)')

    df.user_turn('candy')
    assert df.system_turn().strip() == 'i am a smart info state manager'
    df.user_turn('ice cream', debugging=True)
    assert df.system_turn(debugging=True).strip() == 'i am a stupid state machine'
    df.user_turn('ice cream', debugging=True)
    assert df.system_turn(debugging=True).strip() == 'i am a stupid state machine'
    df.user_turn('ice cream', debugging=True)
    assert df.system_turn(debugging=True).strip() == 'i am a stupid state machine'
    df.user_turn('ice cream', debugging=True)
    assert df.system_turn(debugging=True).strip() == 'i am a stupid state machine'



