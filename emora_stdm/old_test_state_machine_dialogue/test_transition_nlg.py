from emora_stdm.old_StateTransitionDialogueManager.dialogue_flow import DialogueTransition, DialogueFlow
from emora_stdm.old_StateTransitionDialogueManager.knowledge_base import KnowledgeBase

df = DialogueFlow()
df._kb = KnowledgeBase([
            ('avengers', 'chris evans', 'stars'),
            ('avengers', 'scarlett johansson', 'stars'),
            ('chris evans', 'quality', 'good'),
            ('chris evans', 'steve rogers', 'plays'),
            ('scarlett johansson', 'black widow', 'plays')
        ])

df.add_states(list('xy12345678'))

def test_simple_nlg():
    t = DialogueTransition(
        None, 'x', 'y',
        None,
        {
            'how are ya'
        }
    )
    result = t.eval_system_transition()
    assert result[0]
    assert result[1] == 'how are ya'


def test_variable_nlg():
    t = DialogueTransition(
        None, 'x', 'y', None,
        {
            'i am $feeling'
        }
    )
    result = t.eval_system_transition({'feeling': 'good'})
    assert result[1] == 'i am good'
    result = t.eval_system_transition({'feeling': 'bad'})
    assert result[1] == 'i am bad'


def test_kb_nlg():
    df.add_transition('1', '2', None,
        {
            'it has #$movie:stars# in it'
        })
    result = df.get_transition('1', '2').eval_system_transition({'movie': 'avengers'})
    assert result[1] == 'it has chris evans in it' or result[1] == 'it has scarlett johansson in it'

def test_kb_nlg_query():
    df.add_transition( '3', '4', None,
        {
            '%actor=#$movie:stars, $role:/plays# plays $role'
        }
    )
    vars = {'role': 'black widow', 'movie': 'avengers'}
    result = df.get_transition('3', '4').eval_system_transition(vars)
    assert result[1] == 'scarlett johansson plays black widow'
    assert vars['actor'] == 'scarlett johansson'
    vars['role'] = 'steve rogers'
    result = df.get_transition('3', '4').eval_system_transition(vars)
    assert result[1] == 'chris evans plays steve rogers'
    assert vars['actor'] == 'chris evans'

def test_nlg_preprocessing():
    df.add_transition( '5', '6', None,
        {
            '%actor=#$movie:stars, $role:/plays# plays $role, that $actor'
        }
    )
    vars = {'role': 'black widow', 'movie': 'avengers', 'actor': 'bob'}
    result = df.get_transition('5', '6').eval_system_transition(vars)
    assert result[1] == 'scarlett johansson plays black widow that bob'
    assert vars['actor'] == 'scarlett johansson'
    vars['role'] = 'steve rogers'
    result = df.get_transition('5', '6').eval_system_transition(vars)
    assert result[1] == 'chris evans plays steve rogers that scarlett johansson'
    assert vars['actor'] == 'chris evans'


