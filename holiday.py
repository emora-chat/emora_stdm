

from dialogue_flow import DialogueFlow


component = DialogueFlow('start')

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
feelings_negative = ['sad', 'nervous', 'stress', 'stressed', 'worried',
                     'anxious', 'scared', 'fearful', 'annoyed', 'bothered',
                     'terrible', 'horrible', 'awful', 'depressed', 'lonely',
                     'disgusted', 'crazy', 'insane']
holiday = ['christmas', 'new year', 'new years', 'christmas eve', 'hanukkah', 'kwanzaa']
yn_qw = ['do', 'is', 'are', 'was', 'were', 'did', 'will']
q_word = ['what', 'when', 'where', 'why', 'how', 'who']
affirmative = ['yes', 'yeah', 'yea', 'of course', 'sure', 'yep', 'yup', 'absolutely',
               'you bet', 'right']
negative = ['no', 'nope', 'absolutely not', 'of course not']

arcs.extend([(a, 'affirmative', 'type') for a in affirmative])
arcs.extend([(q, 'yn_qw', 'type') for q in yn_qw])
arcs.extend([(f, 'feeling_positive', 'type') for f in feelings_positive])
arcs.extend([(f, 'feeling_negative', 'type') for f in feelings_negative])
arcs.extend([(q, 'question_word', 'type') for q in q_word])
arcs.extend([])
for arc in arcs:
    component.knowledge_base().add(*arc)

component.add_transition(
    'start', 'feelings_q',
    '&yn_qw, you, &feelings_positive, &holiday',
    ['are you excited for the holidays']
)

component.add_transition(
    'feelings_q', 'feelings_pos',
    '({&affirmative, &feelings_positive})',
    ['i am very excited']
)

component.add_transition(
    'feelings_q', 'feelings_neg',
    '({&negative, &feelings_negative})',
    ['no the holidays stress me out']
)

component.add_transition(
    'feelings_q', 'feelings_unsure', None,
    ['i dont know'], settings='e'
)

component.add_transition(
    'feelings_pos', 'feelings_pos_r',
    '{(what, &feelings_positive, {part, most, best}),'
    '(you, &feelings_positive)}',
    ['what excites you the most']
)

component.add_transition(
    'feelings_neg', 'feelings_neg_r',
    '',
    ['']
)





if __name__ == '__main__':
    print(component.system_transition())
    i = input('U: ')
    while True:
        confidence = component.user_transition(i) / 10
        print(component.system_transition())
        i = input('U: ')
