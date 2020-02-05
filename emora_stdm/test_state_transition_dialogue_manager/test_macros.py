
import pytest

from emora_stdm import NatexNLU, NatexNLG
from emora_stdm.state_transition_dialogue_manager.macros_common import *
from emora_stdm.state_transition_dialogue_manager.knowledge_base import KnowledgeBase
from time import time


kb = KnowledgeBase([
    ('lion', 'type', 'cat'),
    ('panther', 'type', 'cat'),
    ('cat', 'type', 'animal'),
    ('animal', 'type', 'thing'),
    ('lion', 'sound', 'roar'),
    ('roar', 'quality', 'loud'),
    ('panther', 'sound', 'growl'),
    ('growl', 'quality', 'scary'),
    ('also', 'type', 'also_syns'),
    ('too', 'type', 'also_syns'),
    ('basketball', 'type', 'unknown_hobby'),
    ('basketball', 'expr', 'bball')
])

macros = {
    'ONT': ONTE(kb),
    'KBQ': KBE(kb),
    'EXP': EXP(kb),
    'U': UnionMacro(),
    'I': Intersection(),
    'DIF': Difference(),
    'SET': SetVars(),
    'ALL': CheckVarsConjunction(),
    'ANY': CheckVarsDisjunction(),
    'NOT': NOT()
}

def test_ONT():
    natex = NatexNLU('[!look its a #ONT(cat)]', macros=macros)
    assert natex.match('look its a lion', debugging=False)
    assert natex.match('look its a panther')
    assert not natex.match('look its a animal')

def test_ONT_lemmatizer():
    natex = NatexNLU('[!look at the #ONT(cat)]', macros=macros)
    assert natex.match('look at the lions', debugging=False)

def test_KBQ():
    natex = NatexNLG('[!hear the lion #KBQ(lion, sound)]', macros=macros)
    assert natex.generate(debugging=False) == 'hear the lion roar'
    natex = NatexNLG('[!the panther is #KBQ(panther, sound, quality)]', macros=macros)
    assert natex.generate(debugging=False) == 'the panther is scary'

def test_EXP():
    natex = NatexNLU('[!i play #EXP(basketball)]', macros=macros)
    assert natex.match('i play bball')
    assert natex.match('i play basketball')
    assert not natex.match('i play soccer')

def test_WN():
    debugging = True
    if debugging:
        macro = WN()
        print(macro(None, {}, ['emotion']))
    natex = NatexNLU('[!i feel #WN(emotion)]', macros={'WN': WN()})
    assert natex.match('i feel happy')
    assert natex.match('i feel sad')
    assert natex.match('i feel joyful')
    assert natex.match('i feel worrying')
    assert natex.match('i feel worried')
    assert not natex.match('i am person')
    assert not natex.match('i am green')

def test_NOT():
    natex = NatexNLU('[!#NOT(#U(hello, there)) [dog]]', macros=macros)
    assert natex.match('hi dog', debugging=True)
    assert not natex.match('hello dog')
    assert not natex.match('hi there dog')
    assert not natex.match('oh dog hello')

def test_UNION():
    natex = NatexNLU('#U(hello, there, world)', macros=macros)
    assert natex.match('hello')
    assert natex.match('world')
    assert not natex.match('something')
    natex = NatexNLU('#U(hello, there, #U(world, earth), #U(you, me))', macros=macros)
    assert natex.match('there', debugging=False)
    assert natex.match('world')
    assert natex.match('you')
    assert not natex.match('something')

def test_INTERSECTION():
    natex = NatexNLU('#I(#U(hello, there, you), #U(hello, are, you))', macros=macros)
    assert natex.match('hello')
    assert natex.match('you')
    assert not natex.match('there')
    assert not natex.match('are')

def test_DIFFERENCE():
    natex = NatexNLU('#DIF(#U(hello, there, you), #U(there))', macros=macros)
    assert natex.match('hello')
    assert natex.match('you')
    assert not natex.match('there')

def test_SET():
    vars = {'a': 'apple', 'b': 'banana'}
    natex = NatexNLU('[!#SET($a=pie, $c=cookie, $d=dog), hello world]', macros=macros)
    assert natex.match('hello world', vars=vars, debugging=False)
    assert vars['a'] == 'pie'
    assert vars['b'] == 'banana'
    assert vars['c'] == 'cookie'
    assert vars['d'] == 'dog'
    assert len(vars) == 4
    vars = {'a': 'apple', 'b': 'banana'}
    natex = NatexNLU('[!#SET($a=pie, $c=cookie), hello $d=dog]', macros=macros)
    assert natex.match('hello dog', vars=vars)
    assert vars['d'] == 'dog'
    assert vars['a'] == 'pie'
    assert vars['c'] == 'cookie'

def test_ALL():
    natex = NatexNLU('[!#ALL($a=apple, $b=banana), hello]', macros=macros)
    assert natex.match('hello', vars={'a': 'apple', 'b': 'banana'})
    assert not natex.match('hello', vars={'a': 'apple', 'b': 'bog'})
    assert not natex.match('hello', vars={'b':'banana'})

def test_ANY():
    natex = NatexNLU('[!#ANY($a=apple, $b=banana), hello]', macros=macros)
    assert natex.match('hello', vars={'a': 'apple', 'b': 'banana'})
    assert natex.match('hello', vars={'a': 'apple', 'b': 'bog'})
    assert natex.match('hello', vars={'b': 'banana'})
    assert not natex.match('hello', vars={'c': 'cat'})



########################################## BUG TESTS ###############################################

def test_bug_1_ONT():
    natex = NatexNLU("[[! #ONT(also_syns)?, i, #ONT(also_syns)?, like, $like_hobby=#ONT(unknown_hobby), #ONT(also_syns)?]]",
                     macros=macros)
    assert natex.match('i also like basketball', debugging=False)

kb2 = KnowledgeBase()
import os
print(os.getcwd())
kb2.load_json_file("../modules/hobbies.json")
macros2 = {
    'ONT': ONTE(kb2),
    'KBQ': KBE(kb2),
    'EXP': EXP(kb2)
}

def test_bug_2_EXP():
    natex = NatexNLU('[[! -{not,dont} {#EXP(yes),#ONT(yes_qualifier),#EXP(like)}]]', macros=macros2)
    assert natex.match('i like', debugging=False)
    assert natex.match('i love')
