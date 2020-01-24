# State Transition Dialogue Manager

## Quickstart example

```python
from emora_stdm import DialogueFlow
from enum import Enum

# states are typically represented as an enum
class State(Enum):
    START = 0
    FAM_ANS = 1
    FAM_Y = 2
    FAM_N = 3
    FAM_ERR = 4
    WHATEV = 5

# initialize the DialogueFlow object, which uses a state-machine to manage dialogue
df = DialogueFlow(State.START)

# add transitions to create an arbitrary graph for the state machine
df.add_system_transition(State.START, State.FAM_ANS, '[!do you have a $F={brother, sister, son, daughter, cousin}]')
df.add_user_transition(State.FAM_ANS, State.FAM_Y, '[{yes, yea, yup, yep, i do, yeah}]')
df.add_user_transition(State.FAM_ANS, State.FAM_N, '[{no, nope}]')
df.add_system_transition(State.FAM_Y, State.WHATEV, 'thats great i wish i had a $F')
df.add_system_transition(State.FAM_N, State.WHATEV, 'ok then')
df.add_system_transition(State.FAM_ERR, State.WHATEV, 'im not sure i understand')

# each state that will be reached on the user turn should define an error transition if no other transition matches
df.set_error_successor(State.FAM_ANS, State.FAM_ERR)
df.set_error_successor(State.WHATEV, State.START)

if __name__ == '__main__':
    # automatic verification of the DialogueFlow's structure (dumps warnings to stdout)
    df.check()
    # run the DialogueFlow in interactive mode to test
    df.run(debugging=True)
```

Defines a dialogue management framework based on state machines and 
regular expressions. 

Class `DialogueFlow` is the main class to initialize. It defines
a state machine that drives natural language conversation. State
transitions in the state machine (alternately) represent either 
system or user turns.

`dialogue_manager = DialogueFlow(start_state)`
initializes a new `DialogueFlow` object with `start_state` as the 
initial state of the state machine.

To add transitions, use either:
```.add_system_transition(source_state, target_state, NatexNLG)``` method to add a system transition,
 or ```.add_user_transition(source_state, target_state, NatexNLU)``` method to add a user transition.
 
The first two arguments are the source and target states of 
the transition, the third argument is a string that defines a set 
of natural language expressions given by a user that satisfy the 
transition (see NatexNLU/NatexNLG below).

A user turn can be taken, updating state, using
```
dialogue_manager.user_turn(input)
```
where input is a string representing the user utterance.

A system turn can be taken using
```
response = dialogue_manager.system_turn()
```

## NatexNLU

Strings created for transition NLU define a set of user expressions
that satisfy the transition by compiling into regular expressions.

You can also create and test standalone Natex objects:
```python
from emora_stdm import NatexNLU, NatexNLG

natex_nlu = NatexNLU('[{hi, hello} you]')
assert natex_nlu.match('hi there how are you', debugging=True)

natex_nlg = NatexNLG('[!well {hi, hello} there you look {good, fine, great} today]')
print(natex_nlg.generate(debugging=True))
```

Natex expressions can be formed using the below constructs, which
are arbitrarily nestable and concatenable.

### Literal
```
'hello there'
```
directly match a literal substring

### Disjunction
```
'{hello there, hi}'
```
matches a substring containing exactly one term inside `{}`, in this case 
"hello there" and "hi" both match.

### Conjunction
```
'<bob, hi>'
```
matches a substring that contains at least all terms inside `<>`,
in this case, "hi bob" and "oh bob well hi there" both would match, but not
"hi"

### Flexible sequence
```
'[hi, bob, how, you]'
```
matches as long as the substring contains all terms inside `[]`,
and the terms are ordered properly within the utterance. Matches
in the example include "hi bob how are you", but not "how are you 
bob". Note that this expression matches any amount of characters
before and after the requisite sequence.

### Inflexible sequence
```
'[!how, are, you]'
```
matches an exact sequence of terms with no words inserted between
terms. The only utterance matching the example is "how are you".
This construct is helpful with nested constructs inside of it that
require an exact ordering, with no extra characters between each
element.

### Negation
```
[!i am -bad]
```
prepend `-` to negate the next term in the expression. The example
will match any expression starting with "i am" where "bad" does NOT
follow. Note that the scope of the negation extends to the end
of the substring due to limitations in regex.

### Regular expression
```
'/[A-Z a-z]+/'
```
substrings within `//` define a python regex directly.

### Nesting
```
'[!{hi, hello} [how, weekend]]'
```
would match "hi how was your weekend", "oh hello so how is the
weekend going", ...

### Variable assignment
```
'[!i am $f={good, bad}]'
```
using `$var=` will assign variable `var` to the next term in
the expression. The variable will persist until overwritten,
and can be referenced in future NLU or NLG expressions.
The example would match either "i am good" or "i am bad", and
assigns variable "f" to either "good" or "bad" depending
on what the user said.

### Variable reference
```
[!why are you $f today]
```
using `$` references a previously assigned variable. If no such
variable exists, the expression as a whole returns with no match.
The example would match "why are you good today" if `f="good"`, 
but would not match if `f="bad"`

### Macros



## Knowledge base and ontology (doc out of date)

The Knowledge Base and Ontology are optional components of the 
dialogue manager that allow you to write more generalizable
transitions. 

The Knowledge Base and Ontology are modeled as a unified (single)
directed graph. You specify the knowledge and ontology elements you 
need by updating the `database.json` file.

The Knowledge Base is defined as a list of predicates, 
where a predicate is stored as a list `[subject, relation, object]`.

```
'predicates': [
    ['dog', 'sound', 'bark'],
    ['bark', 'quality', 'annoying'],
    ['scarlett johansson', 'plays', 'black widow']
]
```

The Ontology is defined as a mapping between categories and a list of elements of that category. 
The category string must always begin with the ampersand symbol: `&`.

```
'ontology': {
    '&feeling': ['sad', 'happy', 'angry'],
    '&animal': ['dog', 'cat', 'bird']
}
```

Taking these two structures together, the final `database.json` for this example would look 
like the following:

```
{
'predicates': [
        ['dog', 'sound', 'bark'],
        ['bark', 'quality', 'annoying'],
        ['scarlett johansson', 'plays', 'black widow']
    ],
'ontology': {
        '&feeling': ['sad', 'happy', 'angry'],
        '&animal': ['dog', 'cat', 'bird']
    }
}
```

### Ontology reference
```
'i am &feeling'
```
Using a prepended `&` references a node in the ontology. Any 
subtype of the referenced node can be matched in the expression.

### Knowledge base reference
```
'a dog can #dog:sound#'
```
substrings encapsulated within `##` reference a set of nodes in the knowledge
graph. The set is created by starting at the node defined before
the initial `:`, then traversing arcs labeled by each subsequent
term following `:`. In this case, all nodes related to "dog" by
a "sound" arc are valid matches. For example, the utterances "a
dog can bark" and "a dog can growl" might be matched if "bark" and
"growl" were present in the knowledge graph.

```
'a dog is #dog:sound:quality#'
```
knowledge base expressions can chain multiple predicates together.
suppose the predicates `sound(dog, bark)` and `quality(bark, annoying)`
were present in the knowledge base. The expression would match 
"a dog is annoying"

```
'black widow is played by #black widow:/plays#'
```
using `/` reverses the direction of a knowledge graph relation. If
`plays(scarlett johansson, black widow)` is present in the KB, then
the above expression matches "black widow is played by scarlett 
johansson"

```
'a %a=&animal, can #$a:sound#'
```
knowledge graph expressions can be built using veriable references.
Together with ontology reference, highly generalizable expressions
can be written. Given an appropriately constructed KB and ontology,
this example might match "a cow can moo", "a dog can bark", and
everything in between.
