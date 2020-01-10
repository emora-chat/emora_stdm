from src.knowledge_base import KnowledgeBase


def test_constructor():
    kb = KnowledgeBase([
        ('s', 'o', 'r'),
        ('s2', 'o2', 'r')
    ])
    assert kb.len_nodes() == 4


def test_types():
    kb = KnowledgeBase()
    kb.add_type('bird', 'animal')
    kb.add_type('bird', 'flying')
    kb.add_type('animal', 'living')
    kb.add_type('dog', 'animal')
    assert kb.types('bird') == {'animal', 'flying', 'living'}


def test_subtypes():
    kb = KnowledgeBase()
    kb.add_type('bird', 'animal')
    kb.add_type('bird', 'flying')
    kb.add_type('animal', 'living')
    kb.add_type('dog', 'animal')
    assert kb.subtypes('animal') == {'bird', 'dog'}


def test_attribute():
    kb = KnowledgeBase([
        ('avengers', 'chris evans', 'stars'),
        ('avengers', 'scarlett johansson', 'stars'),
        ('chris evans', 'quality', 'good'),
        ('scarlett johansson', 'black widow', 'plays')
    ])
    assert kb.attribute({
        'avengers': (False, [(False, 'stars')])
    }) == {'chris evans', 'scarlett johansson'}
    assert kb.attribute({
        'avengers': (False, [(False, 'stars'), (False, 'plays')])
    }) == {'black widow'}
    assert kb.attribute({
        'avengers': (False, [(False, '*')]),
        'black widow': (False, [(True, 'plays')])
    }) == {'scarlett johansson'}




