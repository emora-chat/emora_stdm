<<<<<<< HEAD:stdm/modules/holiday.py
from emora_stdm import DialogueFlow
=======
from emora_stdm.old_StateTransitionDialogueManager.dialogue_flow import DialogueFlow
>>>>>>> dev:emora_stdm/modules/holiday.py
import os

component = DialogueFlow('prestart', 'holiday')
data_file = ""
cwd = os.getcwd()
data_file = os.path.join(cwd, 'emora_stdm', 'stdm', 'modules', 'holiday_database.json')
with open(data_file, 'r') as json_file:
    component.knowledge_base().load_json(json_file.read())

states = ['prestart', 'start', 'feelings_q', 'feelings_pos', 'feelings_pos_reason',
          'activities', 'parties', 'family', 'gifts', 'atmosphere', 'food', 'vacation',
          'feelings_neg', 'feelings_unsure', 'end', 'garbage']
component.add_states(states)

# pre start
component.add_transition(
    'prestart', 'prestart', None, {'x'}, settings='e'
)

component.add_transition(
    'prestart', 'start',
    '&holiday_t', {}
)

# start: are you excited for the holidays
component.add_transition(
    'start', 'feelings_q',
    '&yn_qw, you, &feelings_positive, &holiday_t',
    {'are you excited for the holidays'}
)

# yes
component.add_transition(
    'feelings_q', 'feelings_pos',
    '({&affirmative, &feelings_positive})',
    {'i am very excited'}
)

component.add_transition(
    'feelings_pos', 'feelings_pos_reason',
    '{(what, &feelings_positive, {part, most, best}),'
    '(you, &feelings_positive)}',
    {'what excites you the most'}
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
    {'i always thought building a snowman and baking cookies sounds fun'}
)

component.add_transition(
    'activities', 'end',
    '({sounds,seems,think},&fun)',
    {'that sounds fun, i really like watching holiday movies'}
)

# parties
component.add_transition(
    'feelings_pos_reason', 'parties',
    '{party, parties, extravaganza, bash, get together}',
    {'parties are cool'}
)

component.add_transition(
    'parties', 'end',
    '({sounds,seems,think},&fun)',
    {'spending time with people is great, i enjoy watching holiday movies with them'}
)

# family
component.add_transition(
    'feelings_pos_reason', 'family',
    '({({spend,spending},time),see,seeing,visit,visiting}, &anyfamily)',
    {'i think its enjoyable to visit relatives during the holidays'}
)

component.add_transition(
    'family', 'end',
    '({sounds,seems,think},&fun)',
    {'i think family is important too, one common tradition i hear of is watching holiday movies'}
)

# gifts
component.add_transition(
    'feelings_pos_reason', 'gifts',
    '{'
    '({giving,give,receiving,receive,getting,get,open,opening,wrap,wrapping,unwrap,unwrapping},{gift,gifts,present,presents}),'
    '({gift,gifts,present,presents})'
    '}',
    {'i like shopping for my friends and family'}
)

component.add_transition(
    'gifts', 'end',
    '({sounds,seems,think},&fun)',
    {'generosity is great, watching holiday movies with people is fun too i think'}
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
    {'its a really beautiful time of the year'}
)

component.add_transition(
    'atmosphere', 'end',
    '({sounds,seems,think},&fun)',
    {'i think that there are so many magical holiday sights to see, i also really enjoying watching christmas movies'}
)

# food
component.add_transition(
    'feelings_pos_reason', 'food',
    '{food,dishes,meals,snacks,treats,chocolate,hot chocolate,cocoa,hot cocoa,sipping}',
    {'there is always such good food'}
)

component.add_transition(
    'food', 'end',
    '({sounds,seems,think},&fun)',
    {'holiday food is delicious, i always curl up with a good holiday movie afterwards'}
)

# vacation
component.add_transition(
    'feelings_pos_reason', 'vacation',
    '{vacation,({day,days,week,weeks,time},off),break}',
    {'the time off during the holidays is always refreshing'}
)

component.add_transition(
    'vacation', 'end',
    '({sounds,seems,think},&fun)',
    {'taking a break is important, i especially like to take breaks by watching holiday movies'}
)

# no
component.add_transition(
    'feelings_q', 'feelings_neg',
    '({&negative, &feelings_negative})',
    {'no the holidays stress me out'}
)

component.add_transition(
    'feelings_neg', 'end',
    '({holidays, &holiday_t}, &feelings_negative, i, &feelings_relax, {[&activity, &item], &activity})',
    {'the holidays can be stressful, i like to relax by watching movies'}
)

# not sure
component.add_transition(
    'feelings_q', 'feelings_unsure',
    '&unsure',
    {'i dont know'}
)

component.add_transition(
    'feelings_unsure', 'feelings_pos_reason',
    None,
    {'is there anything about the holiday youre looking forward to'}
)

# garbage

component.add_transition(
    'feelings_pos_reason', 'garbage',
    None,
    {'is there anything about the holiday youre looking forward to'},
    settings='e'
)

component.add_transition(
    'garbage', 'end',
    None,
    {'yeah, one thing i always look forward to is holiday movies'}
)

component.add_transition(
    'end', 'end', None, {'x'}, settings='e'
)

component.finalize()

if __name__ == '__main__':
    component.run()