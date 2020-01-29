import json
import pytest
from emora_stdm.state_transition_dialogue_manager.natex_nlu import NatexNLU
from emora_stdm.state_transition_dialogue_manager.knowledge_base import KnowledgeBase
from emora_stdm.state_transition_dialogue_manager.dialogue_flow import DialogueFlow, Speaker
from enum import Enum


def test_flexible_sequence():
    natex = NatexNLU('[quick, fox, brown, dog]')
    assert natex.match('the quick fox jumped over the brown dog')
    assert not natex.match('fox quick brown dog')
    assert not natex.match('')

def test_rigid_sequence():
    natex = NatexNLU('[!quick, fox, brown, dog]')
    assert natex.match('quick fox brown dog')
    assert not natex.match('the quick fox brown dog')

def test_disjunction():
    natex = NatexNLU('{quick, fox, brown, dog}')
    assert natex.match('fox', debugging=False)
    assert natex.match('dog')
    assert not natex.match('the dog')

def test_conjunction():
    natex = NatexNLU('<quick, fox, brown, dog>')
    assert natex.match('the quick fox and the brown dog', debugging=False)
    assert natex.match('the brown fox and the quick dog')
    assert not natex.match('the fox and the quick dog')

def test_optional():
    natex = NatexNLU('[!i, really?, love sports]')
    assert natex.match('i really love sports', debugging=True)
    assert natex.match('i love sports')
    assert not natex.match('i sports')

def test_negation():
    natex = NatexNLU('-{bad, horrible, not}')
    assert natex.match('i am good')
    assert not natex.match('i am not good')
    assert not natex.match('i am horrible')
    assert not natex.match('bad')

def test_regex():
    natex = NatexNLU('/[a-c]+/')
    assert natex.match('abccba', debugging=False)
    assert not natex.match('abcdabcd', debugging=False)

def test_reference():
    v1 = {'A': 'apple', 'B': 'brown', 'C': 'charlie'}
    v2 = {'C': 'candice'}
    natex = NatexNLU('[!i saw $C today]')
    assert natex.match('i saw charlie today', vars=v1, debugging=False)
    assert natex.match('i saw charlie today', debugging=False) is None
    assert not natex.match('i saw candice today', vars=v1)
    assert natex.match('i saw candice today', vars=v2)

def test_assignment():
    v = {'A': 'apple'}
    natex = NatexNLU('[!i ate a $A={orange, raddish} today]')
    assert natex.match('i ate a orange today', vars=v)
    assert v['A'] == 'orange'
    assert natex.match('i ate a raddish today', vars=v)
    assert v['A'] == 'raddish'
    assert natex.match('i ate a raddish today')
    assert not natex.match('i ate a carrot today', vars=v)
    natex = NatexNLU('[!i ate a $B={orange, raddish} today]')
    assert natex.match('i ate a raddish today', vars=v)
    assert v['B'] == 'raddish'


def test_backreference():
    natex = NatexNLU('[!$A good eat $A={apple, banana}]')
    v = {'A': 'apple'}
    assert natex.match('apple good eat banana', vars=v, debugging=False)
    assert v['A'] == 'banana'
    natex = NatexNLU('[!$A={apple, banana} good eat $A]')
    v = {'A': 'apple'}
    assert natex.match('banana good eat banana', vars=v, debugging=False)
    assert v['A'] == 'banana'
    assert not natex.match('apple good eat banana', debugging=False)
    assert v['A'] != 'apple'

def SIMPLE(ngrams, vars, args):
    return {'foo', 'bar', 'bat', 'baz'}

def HAPPY(ngrams, vars, args):
    if ngrams & {'yay', 'hooray', 'happy', 'good', 'nice', 'love'}:
        vars['SENTIMENT'] = 'happy'
        return True
    else:
        return False

def FIRSTS(ngrams, vars, args):
    firsts = ''
    for arg in args:
        firsts += arg[0]
    return {firsts, firsts[::-1]}

def SET(ngrams, vars, args):
    return set(args)

def INTER(ngrams, vars, args):
    return set.intersection(*args)

macros = {'SIMPLE': SIMPLE, 'HAPPY': HAPPY, 'FIRSTS': FIRSTS, 'INTER': INTER, 'SET': SET}

def test_simple_macro():
    natex = NatexNLU('[!i #SIMPLE]', macros=macros)
    assert natex.match('i foo')
    assert natex.match('i bar')
    assert not natex.match('i err')
    natex = NatexNLU('[!i #SIMPLE()]', macros=macros)
    assert natex.match('i foo')
    assert natex.match('i bar')
    assert not natex.match('i err')

def test_macro_with_args():
    v = {'X': 'carrot'}
    natex = NatexNLU('#FIRSTS(apple, banana, $X)', macros=macros)
    assert natex.match('abc', vars=v, debugging=False)
    assert natex.match('cba', vars=v)

def test_macro_with_assignment():
    v = {}
    natex = NatexNLU('#HAPPY', macros=macros)
    assert natex.match('i am good today', vars=v, debugging=False)
    assert v['SENTIMENT'] == 'happy'
    assert not natex.match('i am bad')

def test_nested_macro():
    natex = NatexNLU('#INTER(#SET(apple, banana), #SET(apple, orange))', macros=macros)
    assert natex.match('apple', debugging=False)
    assert not natex.match('orange')

class States(Enum):
    A = 0
    B = 1
    C = 2
    D = 3
    E = 4

def test_ontology():
    kb = KnowledgeBase()
    ontology = {
        "ontology": {
            "season": [
                "fall",
                "spring",
                "summer",
                "winter"
            ],
            "month": [
                "january",
                "february",
                "march",
                "april",
                "may",
                "june",
                "july",
                "august",
                "september",
                "october",
                "november",
                "december"
            ]
        }
    }
    kb.load_json(ontology)
    df = DialogueFlow(States.A, Speaker.USER, kb=kb)
    df.add_state(States.A)
    df.add_state(States.B)
    df.add_state(States.C)
    df.add_state(States.D)
    df.add_state(States.E)
    df.set_error_successor(States.A, States.E)
    df.set_error_successor(States.B, States.E)
    df.set_error_successor(States.C, States.E)
    df.set_error_successor(States.D, States.E)
    df.add_user_transition(States.A, States.B, "[#ONT(month)]")
    df.add_system_transition(States.B, States.C, "B to C")
    df.add_user_transition(States.C, States.D, "[$m=#ONT(month), $s=#ONT(season)]")

    df.user_turn("january")
    assert df.state() == States.B
    assert df.system_turn() == "B to C"
    df.user_turn("october is in the fall season")
    assert df.state() == States.D
    assert df._vars["m"] == "october"
    assert df._vars["s"] == "fall"

    df._state = States.A
    df.set_speaker(Speaker.USER)
    df.user_turn("hello there")
    assert df.state() == States.E



