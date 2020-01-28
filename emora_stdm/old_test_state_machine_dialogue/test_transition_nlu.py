from emora_stdm.old_StateTransitionDialogueManager.dialogue_flow import DialogueFlow
from emora_stdm.old_StateTransitionDialogueManager.knowledge_base import KnowledgeBase

df = DialogueFlow()
df._kb = KnowledgeBase([
            ('bird', '&animal', 'type'),
            ('dog', '&animal', 'type'),
            ('bird', 'wings', 'has'),
            ('bird', 'tail', 'has'),
            ('dog', 'tail', 'has'),
        ])
holiday_states = ['prestart', 'start', 'feelings_q', 'feelings_pos', 'feelings_pos_reason',
          'activities', 'parties', 'family', 'gifts', 'atmosphere', 'food', 'vacation',
          'feelings_neg', 'feelings_unsure', 'end', 'garbage']
df.add_states(list('123456789') + ['10','11','12', '13', '14'] + holiday_states)

def test_basic_nlu():
    df.add_transition('1', '2', 'this {is, was} a test', {'testing one two three'})
    result = df.get_transition('1', '2').eval_user_transition('this is a test')
    assert result[0]
    result = df.get_transition('1', '2').eval_user_transition('this was a test')
    assert result[0]
    result = df.get_transition('1', '2').eval_user_transition('this could be a test')
    assert not result[0]


def test_var_capturing_nlu():
    df.add_transition('3', '4', 'this {is, was} a %obj={test, win, case}', {'testing one two three'})
    result = df.get_transition('3', '4').eval_user_transition('this is a test')
    assert result[0]
    assert result[1]['obj'] == 'test'
    result = df.get_transition('3', '4').eval_user_transition('this was a win')
    assert result[0]
    assert result[1]['obj'] == 'win'
    result = df.get_transition('3', '4').eval_user_transition('this was a loss')
    assert not result[0]


def test_var_setting_nlu():
    df.add_transition('5', '6', 'this {is, was} a $obj', {'testing one two three'})
    result = df.get_transition('5', '6').eval_user_transition('this was a test', {'obj': 'test'})
    assert result[0]
    result = df.get_transition('5', '6').eval_user_transition('this was a test', {'obj': 'fail'})
    assert not result[0]


def test_virtual_nlu():
    df.add_transition('7', '8',
        'this (&animal) is cool',
        {'this thing is cool'}
    )
    result = df.get_transition('7', '8').eval_user_transition('this bird is cool')
    assert result[0]
    result = df.get_transition('7', '8').eval_user_transition('this dog is cool')
    assert result[0]
    result = df.get_transition('7', '8').eval_user_transition('this cat is cool')
    assert not result[0]


def test_kb_nlu():
    df.add_transition('9', '10',
        'this $animal has, %adapt=#$animal:has#',
        {'this thing is cool'}
    )
    vars = {'animal': 'bird'}
    result = df.get_transition('9', '10').eval_user_transition('this bird has wings', vars)
    assert result[0]
    assert result[1]['adapt'] == 'wings'
    vars = {'animal': 'dog'}
    result = df.get_transition('9', '10').eval_user_transition('this dog has a tail', vars)
    assert result[0]
    assert result[1]['adapt'] == 'tail'
    result = df.get_transition('9', '10').eval_user_transition('this dog has wings', vars)
    assert not result[0]

def test_unsure_answer():
    arcs = []
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

    arcs.extend([(a, '&affirmative', 'type') for a in affirmative])
    arcs.extend([(q, '&yn_qw', 'type') for q in yn_qw])
    arcs.extend([(f, '&feelings_positive', 'type') for f in feelings_positive])
    arcs.extend([(f, '&feelings_negative', 'type') for f in feelings_negative])
    arcs.extend([(q, '&question_word', 'type') for q in q_word])
    arcs.extend([(x, '&holiday', 'type') for x in holiday])
    arcs.extend([(x, '&feelings_relax', 'type') for x in feelings_relax])
    arcs.extend([(x, '&unsure', 'type') for x in unsure])
    arcs.extend([(x, '&activity', 'type') for x in activity])
    arcs.extend([(x, '&item', 'type') for x in item])
    arcs.extend([(x, '&negative', 'type') for x in negative])

    df2 = DialogueFlow()
    df2.add_states(list('123456789') + ['10'] + holiday_states)
    df2._kb = KnowledgeBase(arcs)

    # yes
    df2.add_transition('feelings_q', 'feelings_pos',
        '({&affirmative, &feelings_positive})',
        {'i am very excited'}
    )

    vars = {}
    result = df2.get_transition('feelings_q', 'feelings_pos').eval_user_transition('i dont know', vars)
    assert not result[0]

    # not sure
    df2.add_transition('feelings_q', 'feelings_unsure',
        '&unsure',
        {'i dont know'}
    )

    vars = {}
    result = df2.get_transition('feelings_q', 'feelings_unsure').eval_user_transition('i dont know', vars)
    assert result[0]

def test_nlu_list():
    df.add_transition('11','12',['this {is,was} {fun,exciting}', 'that {is,was} {horrible,sad}'], {'sure'})

    result = df.get_transition('11', '12').eval_user_transition('that was horrible')
    assert result[0]

    result = df.get_transition('11', '12').eval_user_transition('this is fun')
    assert result[0]

    result = df.get_transition('11', '12').eval_user_transition('this was not horrible')
    assert not result[0]

    df.add_transition('13', '14', ['<bee, boo, bop>', '{beep, boop}'], {'sure'})

    result = df.get_transition('13', '14').eval_user_transition('beep')
    assert result[0]

    result = df.get_transition('13', '14').eval_user_transition('bee boo bop')
    assert result[0]

    result = df.get_transition('13', '14').eval_user_transition('this was not horrible')
    assert not result[0]