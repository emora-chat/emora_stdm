
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
        'this $animal has, %adapt=|$animal:has|',
        ['this thing is cool']
    )
    print(t.expression)
    vars = {'animal': 'bird'}
    score, vars = t.user_transition_check('this bird has wings', vars)
    assert score
    assert vars['adapt'] == 'wings'
    vars = {'animal': 'dog'}
    score, vars = t.user_transition_check('this dog has a tail', vars)
    assert score
    assert vars['adapt'] == 'tail'
    score, vars = t.user_transition_check('this dog has wings', vars)
    assert not score

def test_unsure_answer():
    arcs = [
        ('feeling_positive', 'feeling', 'type'),
        ('feeling_negative', 'feeling', 'type'),
        ('family_sinular', 'family_all', 'type'),
        ('family_plural', 'family_all', 'type')
    ]
    family = ['brother', 'mother', 'son', 'daughter', 'sister', 'father',
              'dad', 'mom', 'grandma', 'grandpa', 'wife', 'husband',
              'niece', 'nephew', 'aunt', 'uncle', 'cousin', 'grandson',
              'granddaughter']
    family_plural = ['brothers', 'sons', 'daughters', 'sisters',
                     'grandparents', 'parents', 'siblings', 'kids', 'children',
                     'cousins', 'aunts', 'uncles', 'grandchildren', 'grandsons',
                     'granddaughters', 'family']
    feelings_positive = ['happy', 'excited', 'joyful', 'joy', 'thrilled', 'ready']
    feelings_negative = ['sad', 'nervous', 'stress', 'stressed', 'stressful', 'worried',
                         'anxious', 'scared', 'fearful', 'annoyed', 'bothered',
                         'terrible', 'horrible', 'awful', 'depressed', 'lonely',
                         'disgusted', 'crazy', 'insane']
    feelings_relax = ['relax', 'decompress', 'calm down', 'chill out']
    holiday = ['christmas', 'new year', 'new years', 'christmas eve', 'hanukkah', 'kwanzaa']
    yn_qw = ['do', 'is', 'are', 'was', 'were', 'did', 'will']
    q_word = ['what', 'when', 'where', 'why', 'how', 'who']
    affirmative = ['yes', 'yeah', 'yea', 'of course', 'sure', 'yep', 'yup', 'absolutely',
                   'you bet', 'right']
    negative = ['no', 'nope', 'absolutely not', 'of course not']
    unsure = ['dont know', 'uncertain', 'not sure']
    activity = ['watching']
    item = ['movie', 'movies', 'show', 'shows', 'tv', 'television']

    arcs.extend([(a, 'affirmative', 'type') for a in affirmative])
    arcs.extend([(q, 'yn_qw', 'type') for q in yn_qw])
    arcs.extend([(f, 'feelings_positive', 'type') for f in feelings_positive])
    arcs.extend([(f, 'feelings_negative', 'type') for f in feelings_negative])
    arcs.extend([(q, 'question_word', 'type') for q in q_word])
    arcs.extend([(x, 'holiday', 'type') for x in holiday])
    arcs.extend([(x, 'feelings_relax', 'type') for x in feelings_relax])
    arcs.extend([(x, 'unsure', 'type') for x in unsure])
    arcs.extend([(x, 'activity', 'type') for x in activity])
    arcs.extend([(x, 'item', 'type') for x in item])
    arcs.extend([(x, 'negative', 'type') for x in negative])

    # yes
    t = DialogueTransition(
        KnowledgeBase(arcs), 'feelings_q', 'feelings_pos',
        '({&affirmative, &feelings_positive})',
        ['i am very excited']
    )

    print(t.expression)
    vars = {}
    score, vars = t.user_transition_check('i dont know', vars)
    assert not score

    # not sure
    t = DialogueTransition(
        KnowledgeBase(arcs), 'feelings_q', 'feelings_unsure',
        '&unsure',
        ['i dont know']
    )

    print(t.expression)
    vars = {}
    score, vars = t.user_transition_check('i dont know', vars)
    assert score

#todo - need to parse the regular expression creation to avoid problem with substring matches in ontology (family vs familyplural)
def test_seeing_family():
    arcs = [
        ('feeling_positive', 'feeling', 'type'),
        ('feeling_negative', 'feeling', 'type'),
        ('family_sinular', 'family_all', 'type'),
        ('family_plural', 'family_all', 'type')
    ]
    anyfamily = ['family', 'famplural']
    singularfamily = ['brother', 'mother', 'son', 'daughter', 'sister', 'father',
              'dad', 'mom', 'grandma', 'grandpa', 'wife', 'husband',
              'niece', 'nephew', 'aunt', 'uncle', 'cousin', 'grandson',
              'granddaughter']
    pluralfamily = ['brothers', 'sons', 'daughters', 'sisters',
                     'grandparents', 'parents', 'siblings', 'kids', 'children',
                     'cousins', 'aunts', 'uncles', 'grandchildren', 'grandsons',
                     'granddaughters', 'family', 'relatives']
    feelings_positive = ['happy', 'excited', 'joyful', 'joy', 'thrilled', 'ready']
    feelings_negative = ['sad', 'nervous', 'stress', 'stressed', 'stressful', 'worried',
                         'anxious', 'scared', 'fearful', 'annoyed', 'bothered',
                         'terrible', 'horrible', 'awful', 'depressed', 'lonely',
                         'disgusted', 'crazy', 'insane']
    feelings_relax = ['relax', 'decompress', 'calm down', 'chill out']
    holiday = ['christmas', 'new year', 'new years', 'christmas eve', 'hanukkah', 'kwanzaa']
    yn_qw = ['do', 'is', 'are', 'was', 'were', 'did', 'will']
    q_word = ['what', 'when', 'where', 'why', 'how', 'who']
    affirmative = ['yes', 'yeah', 'yea', 'of course', 'sure', 'yep', 'yup', 'absolutely',
                   'you bet', 'right']
    negative = ['no', 'nope', 'absolutely not', 'of course not']
    unsure = ['dont know', 'uncertain', 'not sure']
    activity = ['watching']
    item = ['movie', 'movies', 'show', 'shows', 'tv', 'television']
    like = ['like', 'enjoy']
    winteractivity = ['ski', 'skiing', 'snowboard', 'snowboarding', 'sled', 'sledding']
    fun = ['fun', 'exciting', 'enjoyable']

    arcs.extend([(a, 'affirmative', 'type') for a in affirmative])
    arcs.extend([(q, 'yn_qw', 'type') for q in yn_qw])
    arcs.extend([(f, 'feelings_positive', 'type') for f in feelings_positive])
    arcs.extend([(f, 'feelings_negative', 'type') for f in feelings_negative])
    arcs.extend([(q, 'question_word', 'type') for q in q_word])
    arcs.extend([(x, 'holiday', 'type') for x in holiday])
    arcs.extend([(x, 'feelings_relax', 'type') for x in feelings_relax])
    arcs.extend([(x, 'unsure', 'type') for x in unsure])
    arcs.extend([(x, 'activity', 'type') for x in activity])
    arcs.extend([(x, 'item', 'type') for x in item])
    arcs.extend([(x, 'negative', 'type') for x in negative])
    arcs.extend([(x, 'like', 'type') for x in like])
    arcs.extend([(x, 'winteractivity', 'type') for x in winteractivity])
    arcs.extend([(x, 'fun', 'type') for x in fun])
    arcs.extend([(x, 'singularfamily', 'type') for x in singularfamily])
    arcs.extend([(x, 'pluralfamily', 'type') for x in pluralfamily])
    arcs.extend([(x, 'anyfamily', 'type') for x in anyfamily])

    # yes
    t = DialogueTransition(
        KnowledgeBase(arcs), 'feelings_pos_reason', 'family',
        '({({spend,spending},time),see,seeing,visit,visiting}, &anyfamily)',
        ['i think its enjoyable to visit relatives during the holidays']
    )

    print(t.expression)
    vars = {}
    score, vars = t.user_transition_check('seeing my family', vars)
    assert score