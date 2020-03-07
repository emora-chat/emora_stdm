
import pytest

from emora_stdm import NatexNLU, NatexNLG
from emora_stdm.state_transition_dialogue_manager.macros_common import *
from emora_stdm.state_transition_dialogue_manager.knowledge_base import KnowledgeBase
from emora_stdm.state_transition_dialogue_manager.dialogue_flow import DialogueFlow
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
    ('basketball', 'expr', 'bball'),
    ('john', 'type', 'male'),
    ('mary', 'type', 'female'),
    ('male', 'type', 'person'),
    ('female', 'type', 'person'),
    ('friend', 'type', 'person')
])

df = DialogueFlow(initial_state='start')
df.add_state('start', 'start')
df.add_system_transition('start', 'start', 'hello')

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
    'NOT': NOT(),
    'ISP': IsPlural(),
    'FPP': FirstPersonPronoun(kb),
    'PSP': PossessivePronoun(kb),
    'TPP': ThirdPersonPronoun(kb),
    'EQ': Equal(),
    'GATE': Gate(df),
    'CLR': Clear(),
    'NER': NamedEntity(),
    'LEM': Lemma()
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

def test_ISP():
    natex = NatexNLU('#ISP($X)', macros=macros)
    assert natex.match('hello', vars={'X': 'dogs'}, debugging=True)
    assert not natex.match('hello', vars={'X': 'dog'})

def test_FPP():
    natex = NatexNLG('[!#FPP(john) went to the store]', macros=macros)
    assert natex.generate() == 'he went to the store'
    natex = NatexNLG('[!#FPP(mary) went to the store]', macros=macros)
    assert natex.generate() == 'she went to the store'
    natex = NatexNLG('[!#FPP(friends) went to the store]', macros=macros)
    assert natex.generate() == 'they went to the store'
    natex = NatexNLG('[!#FPP(cat) went to the store]', macros=macros)
    assert natex.generate() == 'it went to the store'

def test_PSP():
    natex = NatexNLG('[!#PSP(john) book]', macros=macros)
    assert natex.generate() == 'his book'
    natex = NatexNLG('[!#PSP(mary) book]', macros=macros)
    assert natex.generate() == 'her book'
    natex = NatexNLG('[!#PSP(friends) book]', macros=macros)
    assert natex.generate() == 'their book'
    natex = NatexNLG('[!#PSP(cat) book]', macros=macros)
    assert natex.generate() == 'its book'

def test_TPP():
    natex = NatexNLG('[!killed #TPP(john)]', macros=macros)
    assert natex.generate() == 'killed him'
    natex = NatexNLG('[!killed #TPP(mary)]', macros=macros)
    assert natex.generate() == 'killed her'
    natex = NatexNLG('[!killed #TPP(friends)]', macros=macros)
    assert natex.generate() == 'killed them'
    natex = NatexNLG('[!killed #TPP(cat)]', macros=macros)
    assert natex.generate() == 'killed it'

def test_EQ():
    vars = {'animal': 'cat', 'focus': 'dog'}
    natex = NatexNLG('#EQ($animal, $focus)', macros=macros)
    assert natex.generate(vars=vars) is None
    vars['focus'] = 'cat'
    assert natex.generate(vars=vars) == ''

def test_NER():
    natex = NatexNLU('[this is a test for #NER()]', macros=macros)
    match = natex.match('this is a test for America by Mike', debugging=False)
    assert match
    natex = NatexNLU('[this is a test for #NER(person)]', macros=macros)
    match = natex.match('this is a test for America', debugging=False)
    assert not match
    natex = NatexNLU('[this is a test for #NER(person)]', macros=macros)
    match = natex.match('this is a test for Mike', debugging=False)
    assert match
    natex = NatexNLU('[this is a test for #NER(person)]', macros=macros)
    match = natex.match('this is a test for someone', debugging=False)
    assert not match

def test_LEM():
    natex = NatexNLU('[Swimming has same lemma as #LEM(swim)]', macros=macros)
    match = natex.match('Swimming has same lemma as swim', debugging=True)
    assert match
    match = natex.match('Swimming has same lemma as swims', debugging=False)
    assert match
    match = natex.match('Swimming has same lemma as running', debugging=False)
    assert not match
    natex = NatexNLU('[good lemmas #LEM(good)]', macros=macros)
    match = natex.match('good lemmas are good', debugging=False)
    assert match
    match = natex.match('good lemmas are better', debugging=False)
    assert match
    match = natex.match('good lemmas are wonderful', debugging=False)
    assert not match



########################################## BUG TESTS ###############################################

def test_bug_1_ONT():
    natex = NatexNLU("[[! #ONT(also_syns)?, i, #ONT(also_syns)?, like, $like_hobby=#ONT(unknown_hobby), #ONT(also_syns)?]]",
                     macros=macros)
    assert natex.match('i also like basketball', debugging=False)
