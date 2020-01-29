
import pytest
from emora_stdm.state_transition_dialogue_manager.knowledge_base import KnowledgeBase


def test_constructor():
    kb = KnowledgeBase([
        ('i', 'like', 'cookies'),
        ('i', 'like', 'milk'),
        ('i', 'type', 'person'),
        ('i', 'type', 'living_thing'),
        ('cookies', 'quality', 'good')
    ])

def test_query():
    kb = KnowledgeBase([
        ('i', 'like', 'cookies'),
        ('i', 'like', 'milk'),
        ('i', 'type', 'person'),
        ('i', 'type', 'living_thing'),
        ('cookies', 'quality', 'good')
    ])
    assert kb.query('i', 'like', 'quality') == {'good'}

def test_ontology():
    kb = KnowledgeBase([
        ('i', 'like', 'cookies'),
        ('i', 'like', 'milk'),
        ('i', 'type', 'person'),
        ('i', 'type', 'living_thing'),
        ('cookies', 'quality', 'good')
    ])
    assert kb.types('i') == {'person', 'living_thing'}

def test_expressions():
    kb = KnowledgeBase([
        ('i', 'like', 'cookies'),
        ('i', 'like', 'milk'),
        ('i', 'type', 'person'),
        ('i', 'type', 'living_thing'),
        ('cookies', 'quality', 'good')
    ])
    assert kb.expressions('i') == {'i'}
    assert kb.expressions('living_thing') == set()
    kb.add_expression('living_thing', 'life')
    kb.add_expression('living_thing', 'alive')
    assert kb.expressions('living_thing') == {'life', 'alive'}