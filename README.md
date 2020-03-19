# State Transition Dialogue Manager

Defines a dialogue management framework based on state machines and 
regular expressions. 

## Installation

Users install using `pip install emora_stdm`

Developers install using:
```
git clone https://github.com/emora-chat/emora_stdm.git
pip install -r emora_stdm/requirements.txt
```

## Example usage

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

Literals can be formed in three ways:

```
hello there
```
sequences of alphabetical characters and whitespace are interpreted as literals.
The above matches "hello there".

```
"Hello there!"
```
quotes can also be used to escape from natex syntax, allowing any characters
inside the quotes to be interpreted as a literal. The above term matches 
'Hello there!' exactly.

```
`she said "hi" 3 times!`
```
If you want to use quotes as part of the literal, wrap literal in `` instead.

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
'[!i am -bad]'
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
'[!why are you $f today]'
```
using `$` references a previously assigned variable. If no such
variable exists, the expression as a whole returns with no match.
The example would match "why are you good today" if `f="good"`, 
but would not match if `f="bad"`

### Macros

Macros define arbitrary functions that can run within NatexNLU or NatexNLG evaluation.
Create a Macro as follows:

```python
from emora_stdm import Macro


class MyMacro(Macro):

    # optionally, define constructor if macro needs access to additional data
    def __init__(self, x):
        self.x = x

    # define method to run when macro is evaluated in Natex
    def run(self, ngrams, vars, args):
        """
        :param ngrams: an Ngrams object defining the set of all ngrams in the
                       input utterance (for NLU) or vocabulary (for NLG). Treat
                        like a set for all ngrams, or get a specific ngram set
                        using ngrams[n]. Get original string using .text()
        :param vars: a reference to the dictionary of variables
        :param args: a list of arguments passed to the macro from the Natex
        :returns: string, set, boolean, or arbitrary object
                  returning a string will replace the macro call with that string
                  in the natex
                  returning a set of strings replaces macro with a disjunction
                  returning a boolean will replace the macro with wildcards (True)
                  or an unmatchable character sequence (False)
                  returning an arbitrary object is only used to pass data to other macros
        """
        return ' '.join(['hello ' + args[0]] * self.x)


from emora_stdm import NatexNLU

if __name__ == '__main__':
    natex = NatexNLU('[!oh #MyMacro(there) how are you]', macros={'MyMacro': MyMacro(2)})
    assert natex.match('oh hello there hello there how are you')
```

## NatexNLG

NatexNLG objects work very similarly to NatexNLU objects, but they are used to create a 
response string instead of match a user utterance.

```python
from emora_stdm import NatexNLG

natex = NatexNLG('[!{this, here} is a {example, test}, `, testing! 1, 2, 3...`]')
print(natex.generate())
```

The above example might print "this is a test, testing! 1, 2, 3..."

Options (disjunctions) in a NatexNLG will result in one of the set of options to be selected
to generate the response. 

Some constructs (e.g. conjunction, negation) don't make sense in NatexNLGs. Here is the full
list of supported constructs for NatexNLGs:

1. literal
2. rigid sequence [!...]
3. disjunction {...}
4. variable reference $var
5. variable assignment $var=...
6. macro call #MACRO(...)

All the above constructs share the same syntax as the NatexNLU syntax.

# Built-In Macros

### Ontology reference

### `#NER(ner_tag)`
runs SpaCy Named Entity Recognizer to tag the user utterance, and returns a set representing
all named entities present in the user utterance. Optionally, a ner_tag from the below set
of tags can be provided to filter by entity type.


PERSON, NORP, FAC, ORG, GPE, LOC, PRODUCT, EVENT, WORK_OF_ART, LAW, LANGUAGE,
DATE, TIME, PERCENT, MONEY, QUANTITY, ORDINAL, CARDINAL

https://spacy.io/api/annotation

### `#GATE(var1, var2, ...)`
records the values of the provided variables, and returns `True` if that set of variable:value
pairs has not yet been recorded while taking the transition. If the transition is evaluated
with the specified variable signature matching a previously recorded one, `False` is returned.

Note that using no arguments, `#GATE()`, will avoid the transition being taken more than once
regardless of variable values.

Optionally, an argument can be written of the form `variable:value`. 
This notation requires `variable` to be set to `value` for the macro to return `True`.

### `#ONTE(ontology_node_1, ontology_node_2, ...)` 
gets all expressions of all nodes that are ontology descendents of the nodes provided as arguments,
and returns them as a set of strings.

### `#KBQ(node, relation1, relation2, ...)`
defines a knowledge base traversal starting at `node`,
and traversing relations labeled `relation1`, then `relation2`, and so on. All nodes that can be reached
by the specified relation path from `node` are returned as a set of strings.

### `#EXP(node)`
returns the set of all expressions associated with a node.

### `#NOT(term1, term2, ...)`
returns `False` if any term string matches any ngram of the user utterance, 
`True` otherwise.

### `#U(set_or_str_1, set_or_str_2, ...)`
returns a set representing the union of all arguments. 
String arguments are converted to a set containing the string as a single element.

### `#I(set1, set2, ...)`
returns a set representing the intersection of all arguments.

### `#ALL($var1=val1, $var2=val2, ...)`
returns `True` if all variables are set to their provided values, 
where each argument is a string of the form `$var=val`

### `#ANY($var1=val1, $var2=val2, ...)`
returns `True` if any of the variables are set to their provided values, 
where each argument is a string of the form `$var=val`

### `#EQ(arg1, arg2, ...)`
returns `True` if all arguments are equal, `False` otherwise

