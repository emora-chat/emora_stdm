
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
transitions = {
    'Hello!: {
        'hi': 'end'
    }
}
```
This nested dictionary will represent the content of your dialogue agent.
It is structured similar to social media discussion threads, where responses are nested inside the utterance they respond to.
The conversation specified by this dictionary looks like this:
```
A: Hello!
B: hi
```
It's too short: let's add another turn.


```python3
transitions = {
    'Hello!: {
        'hi': {
            'How are you?': 'end'
        }
    }
}
```
We have added a response to the "hi" utterance, so the conversation flow looks like this now:
```
A: Hello!
B: hi
A: How are you?
```
Of course in true conversation, people can say more than one thing. Let's add some options:

```python3
transitions = {
    'Hello!: {
        'hi': {
            'How are you?': 'end'
        },
        'tell me the weather': 'end'
    }
}
```

Now there are two potential conversation pathways:
```
A: Hello!
B: hi
A: How are you?
```
```
A: Hello!
B: tell me the weather
```

However, the example is actually invalid as it stands: we will fix it in the following step.

```python3
transitions = {
    'state': 'start',  # !!!
    'Hello!: {
        'hi': 'end'
    }
}
```
The top-level dictionary needs a `'state'` entry with a value corresponding to the initial state of the DialogueFlow object. 
This allows DialogueFlow to know where to put the content you specified in the dictionary.

```python3
chatbot.load_transitions(transitions)
```
Okay! We just need to load the transition dictionary we made into the DialogueFlow object.
Now we can run our chatbot to test it.

### Running the Chatbot

```python3
chatbot.run()
```
... and run the chatbot! 
This allows you to interact with the chatbot.
But, you will notice the conversation is not interesting.
The bot says "Hello!", then crashes if you say anything other than 'hi' back.
Let's fix that.


## Not enough information?

See if what you're trying to do is covered by one of the outlined [use cases](https://github.com/emora-chat/emora_stdm/blob/master/README.md#specific-use-cases).

Or, learn more from the other [tutorials](https://github.com/emora-chat/emora_stdm/blob/master/README.md#tutorials).
