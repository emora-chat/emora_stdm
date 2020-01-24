
import pytest

from emora_stdm.state_transition_dialogue_manager.ngrams import Ngrams


def test_default_constructor():
    ng = Ngrams("this is a test sentence")
    grams1 =  {'this', 'is', 'a', 'test', 'sentence'}
    grams2 = {'this is', 'is a', 'a test', 'test sentence'}
    grams3 = {'this is a', 'is a test', 'a test sentence'}
    grams4 = {'this is a test', 'is a test sentence'}
    grams5 = {'this is a test sentence'}
    assert ng == set.union(grams1, grams2, grams3, grams4, grams5)
    assert ng[1] == grams1
    assert ng[2] == grams2
    assert ng[3] == grams3
    assert ng[4] == grams4
    assert ng[5] == grams5
    assert ng.text() == 'this is a test sentence'

def test_parameterized_constructor():
    ng = Ngrams('this is a test', 3)
    grams1 = {'this', 'is', 'a', 'test'}
    grams2 = {'this is', 'is a', 'a test'}
    grams3 = {'this is a', 'is a test'}
    assert ng == set.union(grams1, grams2, grams3)
    assert ng[1] == grams1
    assert ng[2] == grams2
    assert ng[3] == grams3
    assert ng.text() == 'this is a test'


