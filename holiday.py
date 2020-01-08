from dialogue_flow import DialogueFlow

component = DialogueFlow('prestart')

arcs = [
    ('feeling_positive', 'feeling', 'type'),
    ('feeling_negative', 'feeling', 'type'),
    ('family_sinular', 'family_all', 'type'),
    ('family_plural', 'family_all', 'type')
]
anyfamily = ['singularfamily', 'pluralfamily']
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
holiday = ['christmas', 'new year', 'new years', 'christmas eve', 'hanukkah', 'kwanzaa',
           'holiday', 'holidays', 'winter break', 'winter vacation', 'new years', 'end of the year']
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
arcs.extend([(x, 'holiday_t', 'type') for x in holiday])
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
arcs.extend([])
for arc in arcs:
    component.knowledge_base().add(*arc)

# pre start
component.add_transition(
    'prestart', 'prestart', None, ['x'], settings='e'
)

component.add_transition(
    'prestart', 'start',
    '&holiday_t', ["holiday"]
)

# start: are you excited for the holidays
component.add_transition(
    'start', 'feelings_q',
    '&yn_qw, you, &feelings_positive, &holiday_t',
    ['are you excited for the holidays']
)

# yes
component.add_transition(
    'feelings_q', 'feelings_pos',
    '({&affirmative, &feelings_positive})',
    ['i am very excited']
)

component.add_transition(
    'feelings_pos', 'feelings_pos_reason',
    '{(what, &feelings_positive, {part, most, best}),'
    '(you, &feelings_positive)}',
    ['what excites you the most']
)

# activities
component.add_transition(
    'feelings_pos_reason', 'activities',
    '{'
    '{christmas carols, christmas carolling, carols, carolling},'
    '({bake,baking,cook,cooking,make,making},{treats,cookies,food,(gingerbread,{men,house,houses})}),'
    '(playing, snow),'
    '({build,building,make,making,create,creating},{snowmen,snowman,snowangel,snowangels}),'
    '&winteractivity,'
    '}',
    ['i always thought building a snowman and baking cookies sounds fun']
)

component.add_transition(
    'activities', 'end',
    '({sounds,seems,think},&fun)',
    ['that sounds fun, i really like watching holiday movies']
)

# parties
component.add_transition(
    'feelings_pos_reason', 'parties',
    '{party, parties, extravaganza, bash, get together}',
    ['parties are cool']
)

component.add_transition(
    'parties', 'end',
    '({sounds,seems,think},&fun)',
    ['spending time with people is great, i enjoy watching holiday movies with them']
)

# family
component.add_transition(
    'feelings_pos_reason', 'family',
    '({({spend,spending},time),see,seeing,visit,visiting}, &anyfamily)',
    ['i think its enjoyable to visit relatives during the holidays']
)

component.add_transition(
    'family', 'end',
    '({sounds,seems,think},&fun)',
    ['i think family is important too, one common tradition i hear of is watching holiday movies']
)

# gifts
component.add_transition(
    'feelings_pos_reason', 'gifts',
    '({giving,give,receiving,receive,getting,get,open,opening,wrap,wrapping,unwrap,unwrapping},'
    '{gift,gifts,present,presents})',
    ['i like shopping for my friends and family']
)

component.add_transition(
    'gifts', 'end',
    '({sounds,seems,think},&fun)',
    ['generosity is great, watching holiday movies with people is fun too i think']
)

# atmosphere
component.add_transition(
    'feelings_pos_reason', 'atmosphere',
    '{'
    '({pretty,gorgeous,wonderful,scenic,beautiful,magical},{lights,light,display,displays,house,houses,time,season,snow,landscape,outside,decoration,decorations,ornaments,ornament}),'
    '{pretty,gorgeous,wonderful,scenic,beautiful,magical},'
    '{(christmas,{tree,trees}),tree,trees,fire,fireplace,mantel,decoration,decorations,stockings,stocking,ornaments,ornament},'
    '{santa,santa claus,mrs claus,claus,reindeer,sleigh,chimney}'
    '}',
    ['its a really beautiful time of the year']
)

component.add_transition(
    'atmosphere', 'end',
    '({sounds,seems,think},&fun)',
    ['i think that there are so many magical holiday sights to see, i also really enjoying watching christmas movies']
)

# food
component.add_transition(
    'feelings_pos_reason', 'food',
    '{food,dishes,meals,snacks,treats,chocolate,hot chocolate,cocoa,hot cocoa,sipping}',
    ['there is always such good food']
)

component.add_transition(
    'food', 'end',
    '({sounds,seems,think},&fun)',
    ['holiday food is delicious, i always curl up with a good holiday movie afterwards']
)

# vacation
component.add_transition(
    'feelings_pos_reason', 'vacation',
    '{vacation,({day,days,week,weeks,time},off),break}',
    ['the time off during the holidays is always refreshing']
)

component.add_transition(
    'vacation', 'end',
    '({sounds,seems,think},&fun)',
    ['taking a break is important, i especially like to take breaks by watching holiday movies']
)

# no
component.add_transition(
    'feelings_q', 'feelings_neg',
    '({&negative, &feelings_negative})',
    ['no the holidays stress me out']
)

component.add_transition(
    'feelings_neg', 'end',
    '({holidays, &holiday_t}, &feelings_negative, i, &feelings_relax, {[&activity, &item], &activity})',
    ['the holidays can be stressful, i like to relax by watching movies']
)

# not sure
component.add_transition(
    'feelings_q', 'feelings_unsure',
    '&unsure',
    ['i dont know']
)

component.add_transition(
    'feelings_unsure', 'feelings_pos_reason',
    None,
    ['is there anything about the holiday youre looking forward to']
)

# garbage

component.add_transition(
    'feelings_pos_reason', 'garbage',
    None,
    ['is there anything about the holiday youre looking forward to'],
    settings='e'
)

component.add_transition(
    'garbage', 'end',
    None,
    ['yeah, one thing i always look forward to is holiday movies']
)

component.add_transition(
    'end', 'end', None, ['x'], settings='e'
)

if __name__ == '__main__':
    i = input('U: ')
    while True:
        confidence = component.user_transition(i) / 10 - 0.3
        print(component.state(), component.vars())
        print('({}) '.format(confidence), component.system_transition())
        i = input('U: ')