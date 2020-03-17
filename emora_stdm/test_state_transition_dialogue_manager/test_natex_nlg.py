
import pytest
from emora_stdm.state_transition_dialogue_manager.natex_nlg import NatexNLG


def test_disjunction():
    ng = NatexNLG('this is {a, the} test case')
    outputs = set()
    for i in range(100):
        outputs.add(ng.generate())
    assert outputs == {'this is a test case', 'this is the test case'}

def test_rigid_sequence():
    ng = NatexNLG('[!this, test, case]')
    assert ng.generate() == 'this test case'

def test_reference():
    v = {'A': 'apple'}
    ng = NatexNLG('i like $A')
    assert ng.generate(vars=v) == 'i like apple'

def test_assignment():
    v = {}
    ng = NatexNLG('i like $X={apple, banana}')
    ng.generate(vars=v, debugging=False)
    assert v['X'] == 'apple' or v['X'] == 'banana'

def test_backreference():
    v = {'X': 'apple'}
    ng = NatexNLG('$X is $X=banana')
    assert ng.generate(vars=v) == 'apple is banana'
    assert v['X'] == 'banana'
    ng = NatexNLG('$X=apple, is $X')
    assert ng.generate(vars=v) == 'apple is apple'

def test_completion():
    v = {'X': 'apple'}
    natex = NatexNLG('i have $X in my $Y')
    assert natex.generate(vars=v) is None
    natex = NatexNLG('i have $X')
    assert not natex.is_complete()


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
    natex = NatexNLG('i have a #SIMPLE', macros=macros)
    forms = set()
    for i in range(100):
        forms.add(natex.generate())
    assert forms == {'i have a foo', 'i have a bar', 'i have a bat', 'i have a baz'}

def test_empty_string_nlg():
    natex = NatexNLG('')
    assert natex.generate() == ''


################################ Bugs ##########################################

# test for markup in nlg literal

def test_nlg_markup():
    natex = NatexNLG('`She said, "hi there!" 10. <tag>`')
    assert natex.generate() == 'She said, "hi there!" 10. <tag>'