from emora_stdm import KnowledgeBase


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


def test_json():
    kb = KnowledgeBase()
    kb.add_type('bird', 'animal')
    kb.add_type('bird', 'flying')
    kb.add_type('animal', 'living')
    kb.add_type('dog', 'animal')
    kb.add('dog', 'bark', 'sound')
    kb.add('bark', 'annoying', 'is')
    saved = kb.to_json()

    kb2 = KnowledgeBase()
    kb2.load_json(saved)
    assert kb2.types('bird') == {'animal', 'flying', 'living'}
    assert kb2.subtypes('animal') == {'bird', 'dog'}
    assert kb2.has_arc('bark', 'annoying', 'is')
    assert kb2.has_arc('dog', 'bark', 'sound')



