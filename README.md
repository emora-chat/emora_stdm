# State Transition Dialogue Manager

Defines a dialogue management framework based on state machines and 
regular expressions. 

Class `DialogueFlow` is the main class to initialize. It defines
a state machine that drives natural language conversation. State
transitions in the state machine (alternately) represent either 
system or user turns.

`dialogue_manager = DialogueFlow('start')`
initializes a new `DialogueFlow` object with `'start'` as the 
initial state of the state machine.

To add transitions, use:
```.add_transition(source, target, NLU, NLG_list)``` method like the 
following:
```
dialogue_manager.add_transition(
    'feelings_pos', 'feelings_pos_reason',
    '{(what, &feelings_positive, {part, most, best}),'
    '(you, &feelings_positive)}',
    ['what excites you the most']
)
```
where the first two arguments are the source and target states of 
the transition, the third argument is a string that defines a set 
of natural language expressions given by a user that satisfy the 
transition (see below), and the fourth argument is a list of natural 
language expressions that the system selects as a response when
taking this transition during its turn.

A user turn can be taken, updating state, using
```
dialogue_manager.user_transition(input)
```
where input is a string representing the user utterance.

A system turn can be taken using
```
dialogue_manager.system_transition()
```


## NLU Expressions

Strings created for transition NLU define a set of user expressions
that satisfy the transition by compiling into regular expressions.
These expressions can be formed using the below constructs, which
are all arbitrarily nestable and concatenable:

### Literal
```
'hello there'
```
directly match the user utterance "hello there"

### Disjunction
```
'{hello there, hi}'
```
matches if the utterance contains any term inside `{}`, in this case 
"hello there", "hi", "hi hello there", and "oh hi bob" all match

### Conjunction
```
'<bob, hi>'
```
matches as long as the utterance contains all terms inside `<>`,
in this case, "hi bob" and "oh bob hi" both would match, but not
"hi"

### Flexible sequence
```
'(hi, bob, how, you)'
```
matches as long as the utterance contains all terms inside `()`,
and the terms are ordered properly within the utterance. Matches
in the example include "hi bob how are you", but not "how are you 
bob"

### Inflexible sequence
```
'[how, are, you]'
```
matches an exact sequence of terms with no words inserted between
terms. The only utterance matching the example is "how are you"

### Nesting
```
'[{hi, hello}, (how, is, weekend)]'
```
would match "hi how is your weekend", "oh hello, so how is the
weekend going", ...

### Ontology reference
```
'i am &feeling'
```
Using a prepended `&` references a node in the ontology. Any 
subtype of the referenced node can be matched in the expression.

### Knowledge base reference
```
'
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
