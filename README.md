# State Transition Dialogue Manager

Defines a dialogue management framework based on state machines and 
regular expressions. 

Class `DialogueFlow` is the main class to initialize. It defines
a state machine that drives natural language conversation.

`dialogue_manager = DialogueFlow('start')`
initializes a new `DialogueFlow` object with `'start'` as the 
initial state of the state machine.

To add transitions, use the `.add_transition` method like the 
following:
```
component.add_transition(
    'feelings_pos', 'feelings_pos_reason',
    '{(what, &feelings_positive, {part, most, best}),'
    '(you, &feelings_positive)}',
    ['what excites you the most']
)
```


####################################################################
GIT SUBTREE SETUP FOR STRUCTPY REPO:
####################################################################

git remote add -f structpy https://github.com/jdfinch/structpy.git
git subtree add --prefix structpy structpy master --squash

####################################################################
GIT SUBTREE UPDATE COMMAND FOR STRUCTPY REPO:
####################################################################

git subtree pull --prefix structpy structpy master --squash
