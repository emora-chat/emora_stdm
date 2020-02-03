
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
    'EXP': EXP(kb)
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

def test_bug_1():
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

def test_EXP_bug():
    natex = NatexNLU('[[! -{not,dont} {#EXP(yes),#ONT(yes_qualifier),#EXP(like)}]]', macros=macros2)
    assert natex.match('i like', debugging=False)
    assert natex.match('i love')
