
import pytest
from dialogue_flow import DialogueTransition
from knowledge_base import KnowledgeBase


def test_basic_nlu():
    t = DialogueTransition(
        None, 'x', 'y',
        'this {is, was} a test',
        ['testing one two three']
    )
    assert t.user_transition_check('this is a test')[0]
    assert t.user_transition_check('this was a test')[0]
    assert not t.user_transition_check('this could be a test')[0]


def test_var_capturing_nlu():
    t = DialogueTransition(
        None, 'x', 'y',
        'this {is, was} a %obj={test, win, case}',
        ['testing one two three']
    )
    score, vars = t.user_transition_check('this is a test')
    assert score
    assert vars['obj'] == 'test'
    score, vars = t.user_transition_check('this was a win')
    assert score
    assert vars['obj'] == 'win'
    score, vars = t.user_transition_check('this was a loss')
    assert not score


def test_var_setting_nlu():
    t = DialogueTransition(
        None, 'x', 'y',
        'this {is, was} a $obj',
        ['testing one two three']
    )
    score, vars = t.user_transition_check('this was a test', {'obj': 'test'})
    assert score
    score, vars = t.user_transition_check('this was a test', {'obj': 'fail'})
    assert not score


def test_virtual_nlu():
    t = DialogueTransition(
        KnowledgeBase([
            ('bird', 'animal', 'type'),
            ('dog', 'animal', 'type')
        ]), 'x', 'y',
        'this (&animal) is cool',
        ['this thing is cool']
    )
    print(t.expression)
    score, vars = t.user_transition_check('this bird is cool')
    assert score
    score, vars = t.user_transition_check('this dog is cool')
    assert score
    score, vars = t.user_transition_check('this cat is cool')
    assert not score


def test_kb_nlu():
    t = DialogueTransition(
        KnowledgeBase([
            ('bird', 'wings', 'has'),
            ('bird', 'tail', 'has'),
            ('dog', 'tail', 'has'),
            ('bird', 'animal', 'type'),
            ('dog', 'animal', 'type')
        ]), 'x', 'y',
        'this $animal has, |$animal:has|',
        ['this thing is cool']
    )
    print(t.expression)
    vars = {'animal': 'bird'}
    score, vars = t.user_transition_check('this bird has wings', vars)
    assert score
    vars = {'animal': 'dog'}
    score, vars = t.user_transition_check('this dog has a tail', vars)
    assert score
    score, vars = t.user_transition_check('this dog has wings', vars)
    assert not score
