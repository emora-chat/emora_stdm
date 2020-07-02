
# Natex

Natex is an extension and reimagining of regular expression.
It is tailored specifically to natural language pattern matching, 
supports integration of pattern matching with arbitrary code, 
and also can be used for natural language generation (NLG).

# NatexNLU

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

### Macro call
```
'[i, live, #NER(location)]'
```
using `#M(a1, a2, ...)` in a Natex calls function `M` with arguments `a1, a2, ...`.
The return value of the function is used to evaluate what substrings match the call term.
For example, if a macro `NER` is defined to match substrings returned from a named entity
recognition model, the above natex would match inputs like "I live in Italy" or "Right now I live in Atlanta".
See the section below for more information on defining and using macros.

# Macros

The most powerful aspect of Natex is the ability to integrate pattern matching with arbitrary code.
This allows regular expressions to be combined with database lookups, NLP models, or custom algorithms.

Macros can be defined by developers by subclassing `Macro`:

```python
from emora_stdm import Macro

class MyMacro(Macro):
    def run(self, ngrams, vars, args):
```

When a natex attempts to match a call term like `#MyMacro(...)`, 
`.run` will be passed the following arguments:
* `ngrams`: a set of strings representing every ngram of the string being matched by the natex.
  The full original string input can be accessed by calling `ngrams.text()`.
* `vars`: a dictionary of <string: object> pairs. This corresponds to the variable dictionary 
  maintained by a `DialogueFlow` object during a conversation.
* `args`: a list of strings representing arguments specified in the natex's macro call term.

The following example shows the definition and usage of a Macro for a contrived use case,
where the goal is to match utterances with a specific number of repeated tokens:

```python
class Repeated(Macro):
    def run(self, ngrams, vars, args):
        word_to_repeat = args[0]
        number_of_repetitions = int(args[1])
        return ' '.join([word_to_repeat] * number_of_repetitions)

natex = NatexNLU('[!oh hello #Rep(there, 3) how are you]', macros={'Rep': Repeated()})
assert natex.match('oh hello there there there how are you')
```

Let's break down this example.

```python
class Repeated(Macro):
    def run(self, ngrams, vars, args):
```

The first two lines of the macro definition subclass `Macro` and set up method `.run`
that will be called when macro call term `#Rep(there, 3)` is compiled into a regex.

```python
    def run(self, ngrams, vars, args):
        word_to_repeat = args[0]
        number_of_repetitions = int(args[1])
        return ' '.join([word_to_repeat] * number_of_repetitions)
```

The above method is what is called during the execution of `.match` in the above code, 
when the natex is compiled into a regular expression for matching.

In other words, when the expression 
```natex.match('oh hello there there there how are you')``` gets executed,
the natex gets compiled into a regular expression. 
The term `#Rep(there, 3)` is translated into a regular expression term by calling `Repeated.run`,
with the following parameter-argument assignments:
* `ngrams.text()`: `"oh hello there there there how are you"`
* `vars`: `{}` (empty, since the natex is not evaluated as part of a `DialogueFlow` conversation)
* `args`: `["there", "3"]`

The return value of calling `natex.match` on this input would result in the macro `.run` method returning
the string `"there there there"`.

This string `"there there there"` represents the substring that matches the `#Rep(there, 3)` natex term
during pattern matching.

If you call the match method with debugging on:
```python
natex.match('oh hello there there there how are you', debugging=True)
```
you will notice the following trace printed from the natex compiler:

```
  Steps             ------------------------------------------------------------
    Original        [!oh hello #Rep(there, 3) how are you]
    Rep             [!oh hello, there there there, how are you]
    Rigid sequence  \boh hello\b\W*\bthere there there\b\W*\bhow are you\b
  Final           \boh hello\b\W*\bthere there there\b\W*\bhow are you\b _END_
```

From this trace, you can see the transformation of `#Rep(there, 3)` --> `there there there`
and how this literal substring fits into the final regular expression on the last line of the trace.

Note that how the return value fits into the final regular expression is dependent on the type of 
the object returned, with the following return types supported:

* `string`: directly inserted as a regex term
* `set of strings`: converted to a regex disjunction, i.e. `(?:e1|e2|e3|...)`
* `boolean`:   `True` converts to `.*?` and `False` converts to `__FALSE__`
 
The internal logic of a macro is dependent on the developer's needs.
In the case of the above example,
the logic is to build a string representing a word repeated `number_of_repetitions` times,
where `number_of_repetitions` is provided by the second item of the `args` list. 
Although this example is highly contrived, it demonstrates how arbitrary logic is made
interoperable with pattern matching with the natex compiler.

Below is an example of the built-in `#NER` macro that uses SpaCy's NER, to illustrate how an NLP model can be
incorportated into pattern matching.

```python
class NamedEntity(Macro):
    def run(self, ngrams, vars, args):
        doc = nlp(ngrams.text())
        entities = set()
        for ent in doc.ents:
            if not args or ent.label_.lower() in {x.lower() for x in args}:
                entities.add(ent.text)
        return entities
```

# Built-In Macros

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


# NatexNLG

NatexNLG objects work very similarly to NatexNLU objects, but they are used to create a 
response string instead of match a user utterance.

```python
from emora_stdm import NatexNLG

natex = NatexNLG('[!{this, here} is a {example, test}, `, testing! 1, 2, 3...`]')
print(natex.generate())
```

The above example might print `"this is a test, testing! 1, 2, 3..."`

Options (disjunctions) in a NatexNLG will result in one of the set of options to be selected
to generate the response. 

Some constructs (e.g. conjunction, negation) don't make sense in NatexNLGs. Here is the full
list of supported constructs for NatexNLGs:

1. literal `"..."`
2. rigid sequence `[!...]`
3. disjunction `{...}`
4. variable reference `$var`
5. variable assignment `$var=...`
6. macro call `#MACRO(...)`

All the above constructs share the same syntax as the NatexNLU syntax.

