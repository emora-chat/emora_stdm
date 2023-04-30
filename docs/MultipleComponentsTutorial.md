
# Composite DialogueFlow

This shows an example of using multiple components in a single dialogue system.

Here are two separate dialogue agents:

```python
from emora_stdm import DialogueFlow, CompositeDialogueFlow

A = DialogueFlow('start')
A.load_transitions({
    'state': 'start',
    '`Let\'s talk about books!`': {
        'error': {
            '`What\'s your favorite book?`': {
                'error': {
                    '`Cool!`': '__end__',
                    '`Okay.`': 'movies:movie_question'
                }
            }
        }
    }
})

B = DialogueFlow('start')
B.load_transitions({
    '`Let\'s talk about movies!`': {
        'state': 'start',
        'error': {
            'state': 'movie_question',
            '`What is your favorite movie?`': {
                'error': {
                    '`That\'s a good one!`': {}
                }
            }
        }
    }
})
```

They can be combined using `CompositeDialogueFlow`:

```python
C = CompositeDialogueFlow('start', system_error_state='start', user_error_state='greet')
C.add_component(A, 'books')
C.add_component(B, 'movies')
C.component('SYSTEM').load_transitions({
    'state': 'start',
    '`Hello!`': {
        'state': 'greet',
        'error': 'books:start'
    }
})

C.run()
```

Here is an example conversation made by running the above system:

```
S: Hello!
U: Hi!
S: Let's talk about books!
U: Sure
S: What's your favorite book?
U: Harry Potter
S: Okay. What is your favorite movie?
U: Avengers.
S: That's a good one!
U: Yeah.
S:  Hello!       <-- Crash recovery
U: 
```