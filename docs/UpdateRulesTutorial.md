
# Update Rules

Update rules affect the state of the dialogue before (and possibly exclusively from)
the Dialogue Graph is updated. The purpose of this is to allow abstract reasoning on
the dialogue state and user input to support more complex dialogue interactions.

Update rules are <precondition, postcondition> tuples where
the precondition is a NatexNLU object and the postcondition is a NatexNLG object.

Here is an example of update rules being used in Emora-STDM to drive dialogue management:

```python
system = DialogueFlow('start', initial_speaker=DialogueFlow.Speaker.USER)
system.load_transitions({'state': 'start', 'error': {'` `': {'score': -1, 'state': 'start'}}})

system.load_update_rules({
    '[news]': '`Coronavirus, argh!` (1)',
    '[{movie, movies}]': '`Avengers is a good one.` (1)',
    '/.*/': '`I\'match not sure I understand.` (1)',
})

system.run()
```

The core of this code is the middle three lines, which define 3 update rules.
These rules form a reactionary chatbot that responds to certain patterns.
Note that the `.load_transitions` line is just creating a placeholder loop in the Dialogue Graph:
in future updates to Emora-STDM this will not be necessary for Update Rule-driven chatbots.

Each turn, the user input is matched against each rule's precondition natex, top to bottom.
If the input matches, the rule "fires", applying the postcondition.
For all the above rules, a postcondition score (the `(1)`'s on the right) is specified, 
so applying the postcondition means responding with natural language and ending the turn.

For example, the rule ```'[news]': '`Coronavirus, argh!`'``` means that if the user's 
utterance contains "news", the system replies by saying "Coronavirus, argh!".

Here is an example conversation produced by the above system:

```
U: Hi
S: I'm not sure I understand.
U: Have you seen any movies?
S: Avengers is a good one.
U: What about movies based on recent news?
S: Coronavirus, argh!
```




The order of these rules matters, since update rule evaluation stops as soon as a 
rule successfully outputs a natural language response.
Note that you can manually specify priority scores if you wish
using parentheses notation at the end of the precondition:

 ```python
{
    '/.*/ (0.1)': '`I\'match not sure I understand.` (1)',
    '[news]': '`Coronavirus, argh!` (1)',
    '[{movie, movies} (2.0)]': '`Avengers is a good one.` (1)'
}
```

Precondition priority scores all default to 1.0 and will override the declaration order.

You may be wondering why specifying priorities of `(1)` for each postcondition.
The reason is that the update rules are completely interoperable with the Dialogue Graph.
After Update Rules finish processing, the Dialogue Graph is updated.
If both the Dialogue Graph and an Update Rule output a response, the response with the 
higher score will be selected as the true system output.

Consider an example system using both the Dialogue Graph and Update Rules to drive dialogue:

```python
system.load_transitions({
    'state': 'start',

    '[{hi, hello}]': {
        'state': 'greet',

         '`Hi!`':{
             'score': 3.0,

             'error': { '`Bye.`': 'end' }
         }
    },

    'error': { '`Bye`': 'end' }
})

system.load_update_rules({
    '[news]': '`Coronavirus, argh!` (4.0)',
    '[{movie, movies}]': '`Avengers is a good one.` (4.0)',
    '/.*/ (0.1)': '`I\'match not sure I understand.` (2.0)',
})
```

In this example, the conversation begins in the state `'start'`. 
If the user says "Hello", the third update rule _and_ the dialogue graph natex `[{hi, hello}]`
will both match.
The update rule produces candidate response "I'm not sure I understand", 
and the Dialogue Graph produces candidate response "Hi!" as a transition from the `'greet'` state.
Since there are two candidate responses, the response with the higher score is selected as 
the system output. In this case, the update rule has a response score of 2.0, whereas the "Hi!" 
transition has a 3.0 score, so it is selected as the system output and the Dialogue Graph state
is updated by taking this transition.

Suppose instead, at the start of the conversation the user says "Hi, tell me news" instead of "Hello". 
In this case, the Dialogue graph natex `[{hi, hello}]` would still match, but the update rule
candidate response score for "Coronavirus, argh!" is 4.0, meaning it would be selected as the 
true system output. When an update rule's output is selected as the final system response, the 
Dialogue Graph state does *not* update. Therefore, this interaction would still end in the `'start'` state.

### Reasoning with Update Rules

In the above section we saw how Update Rules can drive dialogue, and how they can combine with the Dialogue Graph
based dialogue management to incorporate global handling of certain interactions. 
This section shows the true power of update rules to perform abstract reasoning on the dialogue state.

As an example, suppose our goal is to ask the user about their job if we learn they are an adult.
We can construct a set of logical implications that reason about the user's age, and encode them as update rules:

```python
{
    '[my, {husband, wife, kids}]': '#SET($is_adult=True)',
    '{[i, work]}': '#SET($is_adult=True)',
    '#IF($is_adult=True)': '`How is you job going?` (2.0)',
    '/.*/ (0.1)': '`I\'match not sure I understand.` (1)',
}
```

With these update rules, if the user says something like "I met my husband five years ago",
the variable `$is_adult` will be set to `"True"` when postcondition `#SET($is_adult=True)` is applied.
Note that, since no priority score is marked on this postcondition, it is not treated as a candidate
system response.
Instead, the postcondition is applied, and the Update Rules continue to be evaluated.
This would, _within the same turn_, case the rule 
```'#IF($is_adult=True)': '`How is you job going?` (2.0)'```
to fire, producing a system response.

Notice that a variety of patterns could flag `$is_adult=True` to be set, allowing the response
"How is your job going?" to appropriately abstract to any situation in which the user gives a
signal that they are an adult. These kinds of commonsense reasoning rules can be
chained together arbitrarily to further abstract reasoning. 
