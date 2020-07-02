
# Introduction to Emora STDM

This document is meant to be an introduction to making a simple chatbot with Emora STDM.
Other tutorials cover advanced features that handle more complex interactions.

This guide should be especially helpful to people with little programming/dialogue development experience, 
or those who want to do some rapid prototyping of a dialogue agent.

<details>
  <summary>Finished Example</summary>
  
  This tutorial builds towards the following example.
  
  ```python3
  from emora_stdm import DialogueFlow

  chatbot = DialogueFlow('start')
  transitions = {
      'state': 'start',
      '"Hello."': {
          '#INT(Hi! How are you?, How are you doing?)': {
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
  
</details>

### Creating a Dialogue Agent

```python3
from emora_stdm import DialogueFlow
chatbot = DialogueFlow('start')
```
Import DialogueFlow class and create a DialogueFlow object.
This object is your dialogue agent, and `'start'` indicates where the conversation begins.

```python3
transitions = {
    '"Hello!"': {
        '"Hi!"': 'end'
    }
}
```
This nested dictionary will represent the content of your dialogue agent.
It is structured similar to social media discussion threads, where responses are nested inside the utterance they respond to.
The conversation specified by this dictionary looks like this:
```
A: Hello!
B: Hi!
```
It's too short: let's add another turn.


```python3
transitions = {
    '"Hello!"': {
        '"Hi!"': {
            '"How are you?"': 'end'
        }
    }
}
```
We have added a response to the "hi" utterance, so the conversation flow looks like this now:
```
A: Hello!
B: Hi!
A: How are you?
```
Of course in true conversation, people can say more than one thing. Let's add some options:

```python3
transitions = {
    '"Hello!"': {
        '"Hi!"': {
            '"How are you?"': 'end'
        },
        '"Tell me the weather."': 'end'
    }
}
```

Now there are two potential conversation pathways:
```
A: Hello!
B: Hi!
A: How are you?
```
```
A: Hello!
B: Tell me the weather.
```

However, the example is actually invalid as it stands. This update is required to make it work:

```python3
transitions = {
    'state': 'start',  # !!!!
    '"Hello!"': {
        '"Hi!"': {
            '"How are you?"': 'end'
        },
        '"Tell me the weather."': 'end'
    }
}
```
The top-level dictionary needs a `'state'` entry with a value corresponding to the initial state of the DialogueFlow object. 
This allows DialogueFlow to know where to put the content you specified in the dictionary.

Okay! We just need to load the transition dictionary we made into the DialogueFlow object.
```python3
chatbot.load_transitions(transitions)
```
Now we can run our chatbot to test it.

### Running the Chatbot

Run a DialogueFlow object in interactive mode like this:
```python3
chatbot.run()
```
When testing, you will notice the conversation is not interesting.
The bot says "Hello!", then crashes if you say anything other than "Hi!" or "Tell me the weather." back.
Let's fix that by adding some Natural Language Understanding (NLU).

### Natural Language Understanding

Emora STDM supports many approaches to NLU, but let's start off with a simple approach: intent classification.

```python3
'#INT(Hi! How are you?)'
```
This string defines an intent that will match user input that is similar to the phrase "Hi! How are you?".
The `#INT()` syntax is a Natex macro that invokes a pre-built intent classifer.
The `Hi! How are you?` phrase is used by this intent classifier to evaluate user input.

Let's add some intents to speaker B in our transition dictionary, and make sure we have responses to both:
```python3
transitions = {
    'state': 'start',
    '"Hello!"': {
        '#INT(Hi! How are you?)': {
            '"Good! Bye bye!"': 'end'
        },
        '#INT(Tell me about the weather.)': {
            '"It is sunny!"': 'end'
        }
    }
}
```

Now if you run the system, the bot will appropriately distinguish between you asking the bot how it's doing and asking about the weather:
```
S: Hello!
U: Hey, how do you feel today?
S: Good! Bye bye!
```
```
S: Hello!
U: Is it cloudy outside?
S: It is sunny!
```



## Want to learn more?

Check out the other [tutorials](https://github.com/emora-chat/emora_stdm/blob/master/README.md#tutorials).
