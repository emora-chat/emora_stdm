
import pytest
from dialogue_flow import DialogueTransition
from knowledge_base import KnowledgeBase


def test_simple_nlg():
    t = DialogueTransition(
        None, 'x', 'y',
        None,
        [
            'how are ya'
        ]
    )
    assert t.system_transition_check()[0]
    assert t.response() == 'how are ya'


def test_variable_nlg():
    t = DialogueTransition(
        None, 'x', 'y', None,
        [
            'i am $feeling'
        ]
    )
    assert t.response({'feeling': 'good'}) == 'i am good'
    assert t.response({'feeling': 'bad'}) == 'i am bad'


def test_kb_nlg():
    t = DialogueTransition(
        KnowledgeBase([
            ('avengers', 'chris evans', 'stars')
        ]), 'x', 'y', None,
        [
            'it has <$movie:stars> in it'
        ]
    )
    assert t.response({'movie': 'avengers'}) == 'it has chris evans in it'

def test_kb_nlg_query():
    t = DialogueTransition(
        KnowledgeBase([
            ('avengers', 'chris evans', 'stars'),
            ('avengers', 'scarlett johansson', 'stars'),
            ('chris evans', 'quality', 'good'),
            ('chris evans', 'steve rogers', 'plays'),
            ('scarlett johansson', 'black widow', 'plays')
        ]), 'x', 'y', None,
        [
            '%actor=<$movie:stars, $role:/plays> plays $role'
        ]
    )
    vars = {'role': 'black widow', 'movie': 'avengers'}
    assert t.response(vars) == 'scarlett johansson plays black widow'
    assert vars['actor'] == 'scarlett johansson'
    vars['role'] = 'steve rogers'
    assert t.response(vars) == 'chris evans plays steve rogers'
    assert vars['actor'] == 'chris evans'

def test_nlg_preprocessing():
    t = DialogueTransition(
        KnowledgeBase([
            ('avengers', 'chris evans', 'stars'),
            ('avengers', 'scarlett johansson', 'stars'),
            ('chris evans', 'quality', 'good'),
            ('chris evans', 'steve rogers', 'plays'),
            ('scarlett johansson', 'black widow', 'plays')
        ]), 'x', 'y', None,
        [
            '%actor=<$movie:stars, $role:/plays> plays $role that $actor'
        ]
    )
    vars = {'role': 'black widow', 'movie': 'avengers', 'actor': 'bob'}
    assert t.response(vars) == 'scarlett johansson plays black widow that scarlett johansson'
    assert vars['actor'] == 'scarlett johansson'
    vars['role'] = 'steve rogers'
    assert t.response(vars) == 'chris evans plays steve rogers that chris evans'
    assert vars['actor'] == 'chris evans'


