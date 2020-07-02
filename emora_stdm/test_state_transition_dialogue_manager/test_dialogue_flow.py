
import pytest, json
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
    for _ in range(6):
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

def test_user_transition_list_disjunction():
    df = DialogueFlow('root', initial_speaker=Speaker.USER)
    nlu = [
        'hello',
        'hi',
        'how are you'
    ]
    df.add_user_transition('root', 'x', nlu)
    df.update_state_settings('root', error_successor='y')
    df.user_turn('hi')
    assert df.state() == 'x'

def test_global_transition_list_disjunction():
    df = DialogueFlow('root', initial_speaker=Speaker.USER)
    nlu = [
        'hi',
        'hello'
    ]
    df.add_state('root', 'x')
    df.add_system_transition('x', 'y', 'hello')
    df.add_global_nlu('x', nlu)
    df.user_turn('ok')
    df.system_turn()
    df.user_turn('hi')
    assert df.state() == 'x'

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
    assert df.state() == 'States.A'
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
    df.add_update_rule('#ANY($x=ice cream)', '$y=None')
    df.add_update_rule('#ANY($y=blah)', 'i am a smart info state manager (2.0)')

    df.user_turn('candy', debugging=True)
    assert df.system_turn().strip() == 'i am a smart info state manager'
    df.user_turn('ice cream', debugging=True)
    assert df.system_turn(debugging=True).strip() == 'i am a stupid state machine'
    df.user_turn('ice cream', debugging=True)
    assert df.system_turn(debugging=True).strip() == 'i am a stupid state machine'
    df.user_turn('ice cream', debugging=True)
    assert df.system_turn(debugging=True).strip() == 'i am a stupid state machine'
    df.user_turn('ice cream', debugging=True)
    assert df.system_turn(debugging=True).strip() == 'i am a stupid state machine'


def test_transitions_to_transitions():
    df = DialogueFlow('root', initial_speaker=Speaker.SYSTEM)
    transitions = {
        'state': 'root',

        '"Hello World!"': {
            'state': 'state_2',

            'error': {
                '"Hi,"': 'root->state_2'
            }
        }
    }
    df.load_transitions(transitions, speaker=Speaker.SYSTEM)
    assert df.system_turn() == 'Hello World!'
    df.user_turn('blah')
    assert df.system_turn() == 'Hi, Hello World!'


# def test_dialogue_flow_modular_transition():
#     # test to ensure dialogue flow module with transition to other
#     # component does not crash when tested independently
#     df = DialogueFlow('root', initial_speaker=Speaker.SYSTEM)
#     transitions = {
#         'state': 'root',
#
#         '"Hello World!"': {
#             'state': 'state_2',
#
#             'error': {
#                 '"How are you?"': {
#                     'state': 'mystate',
#                     'error': 'root'
#                 },
#                 '"External thing"':{
#                     'state': 'external_component:external_state',
#                     'score': 2.0
#                 }
#             }
#         }
#     }
#     df.load_transitions(transitions, speaker=Speaker.SYSTEM)
#     assert df.system_turn() == 'Hello World!'
#     df.user_turn('blah')
#     assert df.system_turn() == 'How are you?'
#     assert df.state() == 'mystate'


def test_information_state_state_set():
    df = DialogueFlow('root', initial_speaker=Speaker.USER)
    transitions = {
        'state': 'root',
        'error': {
            'state': 'one',
            'okay': {
                'state': 'two',
                'error': {
                    'state': 'three',
                    'sure': 'root'
                }
            }
        },
        'something': {
            'state': 'special',
            'that is great': 'root'
        }
    }
    df.add_update_rule('[{read, watched}]', '#TRANSITION(special, 2.0)')
    df.load_transitions(transitions, speaker=Speaker.USER)
    df.user_turn('hi')
    assert df.system_turn() == 'okay'
    df.user_turn('i read a book')
    assert df.state() == 'special'
    assert df.system_turn() == 'that is great'
    assert df.state() == 'root'


def test_unexpected_input_macro():
    df = DialogueFlow('root', initial_speaker=Speaker.USER)
    df.add_user_transition('root', 'x', '#UNX')
    df.add_system_transition('x', 'y', '"So, whats for dinner?"')
    df.user_turn('blah blah blah blah blah blah')
    tokens = df.system_turn().split()
    assert len(tokens) > 4 and 'So, whats for dinner?' == ' '.join(tokens[-4:])


def test_global_transition_priority():
    df = DialogueFlow('root')
    transitions = {
        'state': 'root',
        'hello':{
            '[oh]':{
                'score': 0.6,
                'okay':{}
            },
            '[wow]':{
                'score': 2.0,
                'alright': {}
            }
        }
    }
    df.add_global_nlu('root', '/.*/', score=0.7)
    df.load_transitions(transitions)
    df.system_turn()
    df.user_turn('oh wow')
    assert df.system_turn() == 'alright'


def test_gate():
    df = DialogueFlow('root')
    transitions = {
        'state': 'root',

        '#GATE hello': {
            'state': 'greet',
            'score': 2.0,

            '#GATE [{hi, hello}]': {
                'how are ya': {'error': 'root'}
            },
            'error': {
                'how are you': {'error': 'root'}
            }
        },
        'hi': 'greet'
    }
    df.load_transitions(transitions)
    assert df.system_turn().strip() == 'hello'
    df.user_turn('hi')
    assert df.system_turn().strip() == 'how are ya'
    df.user_turn('fine')
    assert df.system_turn().strip() == 'hi'
    df.user_turn('oh')
    assert df.system_turn().strip() == 'how are you'

def test_gate_none():
    df = DialogueFlow('root')
    transitions = {
        'state': 'root',

        '#GATE(var:None) hello': {
            'state': 'greet',
            'score': 2.0,

            'hi': {
                '#SET($var=True) how are ya': {'error': 'root'}
            },
            'error': {
                'how are you': {'error': 'root'}
            }
        },
        'hi': 'greet'
    }
    df.load_transitions(transitions)
    assert df.system_turn().strip() == 'hello'
    df.user_turn('hi')
    assert df.system_turn().strip() == 'how are ya'
    df.user_turn('fine')
    assert df.system_turn().strip() == 'hi'
    df.user_turn('oh')
    assert df.system_turn().strip() == 'how are you'


def test_enter_natex():
    df = DialogueFlow('root')
    transitions = {
        'state': 'root',

        'hello': {
            'state': 'one',
            'score': 2.0,
            'enter': '#GATE',

            'error': 'root'
        },
        'hi': {
            'state': 'two',
            'score': 1.0,
            'enter': '#GATE',

            'error': 'root'
        },
        'bye': {
            'state': 'one',
            'score': 1.0,
        },
        'goodbye': {
            'state': 'three',
            'score': 0.0,
            'error': 'end'
        }
    }
    df.load_transitions(transitions)
    assert df.system_turn() == 'hello'
    df.user_turn('hello')
    assert df.system_turn() == 'hi'
    df.user_turn('hi')
    assert df.system_turn() == 'goodbye'

def test_serialization():
    df = DialogueFlow(States.A, initial_speaker=Speaker.SYSTEM)
    df.add_state(States.B, error_successor=States.E)
    df.add_state(States.C, error_successor=States.E)
    df.add_system_transition(States.A, States.B, '#GATE $spoken=B')
    df.add_system_transition(States.A, States.C, '#GATE(spoken) $spoken=C')
    df.add_system_transition(States.E, States.E, '$spoken=E')
    df.add_user_transition(States.B, States.A, '$heard=b')
    df.add_user_transition(States.E, States.A, '$heard=e')

    df.system_turn()
    assert df.state() == States.B
    assert df.vars()["spoken"] == "B"
    df.user_turn('b')
    df.system_turn()
    assert df.state() == States.C
    assert df.vars()["spoken"] == "C"
    expected_gates = {'States.B': [{}], 'States.C': [{'spoken': 'B'}]}
    assert df.gates() == expected_gates
    df.vars()["testing_none"] = None
    d = df.serialize()

    df2 = DialogueFlow(States.A, initial_speaker=Speaker.SYSTEM)
    df2.add_state(States.B, error_successor=States.E)
    df2.add_state(States.C, error_successor=States.E)
    df2.add_system_transition(States.A, States.B, '#GATE $spoken=B')
    df2.add_system_transition(States.A, States.C, '#GATE(spoken) $spoken=C')
    df2.add_system_transition(States.E, States.E, '$spoken=E')
    df2.add_user_transition(States.B, States.A, '$heard=b')
    df2.add_user_transition(States.E, States.A, '$heard=e')
    assert df2.state() == States.A
    assert 'spoken' not in df2.vars() and 'heard' not in df2.vars()
    assert len(df2.gates()) == 0

    df2.deserialize(d)

    assert df.vars() == df2.vars()
    assert df.gates() == df2.gates()
    assert df.state() == df2.state()
    assert df2.vars()["testing_none"] is None

















