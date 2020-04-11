
# Emora STDM for Novices (or people short on time)

This document is meant to be a quick and dirty overview of Emora STDM's most basic features.
It should be especially helpful to people with little programming/dialogue development experience, 
or those who want to do some rapid prototyping of a dialogue agent.

This is the example for the tutorial, which we will break down to see what each part of the syntax does:

```python3
from emora_stdm import DialogueFlow

chatbot = DialogueFlow('start')
transitions = {
    'state': 'start',
    '"Hello."': {
        '#INT(Hi! How are you?)': {
            '"Good. How are you?"': {
                '[{good, great, okay}]': {
                    '"That\'s great!" Bye!': 'end'
                },
                '{[bad, horrible, awful]}': {
                    '"Oh no! Bye!"': 'end'
                },
                'error': {
                    '"I do not understand! Bye!"': 'end'
                }
            }
        },
        '#INT(Tell me the weather.)': {
            '"It is sunny out!"': {
                'error': {
                    '"Bye!"': 'end'
                }
            }
        }
    }
}
chatbot.load_transitions(transitions)
chatbot.run()
```

### Creating a Dialogue Agent

```python3
from emora_stdm import DialogueFlow
chatbot = DialogueFlow('start')
```
Import DialogueFlow class and create a DialogueFlow object.
This object is your dialogue agent, and `'start'` indicates where the conversation begins.

```python3

```

## Not enough information?

See if what you're trying to do is covered by one of the outlined [use cases](https://github.com/emora-chat/emora_stdm/blob/master/README.md#specific-use-cases).

Or, learn more from the other [tutorials](https://github.com/emora-chat/emora_stdm/blob/master/README.md#tutorials).
