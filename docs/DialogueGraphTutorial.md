
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

  chatbot = DialogueFlow('start', end_state='end')
  transitions = {
      'state': 'start',

      '"Hello."': {
          '#INT(Hi! How are you?, How are you doing?)': {

              '"Good. How are you?"': {
                  'state': 'asking-user-mood',
    
                  '[{good, great, okay}]': {    
            
                      '"That\'s great! ' 
                      'Know what\'s good about today?"': {
                            'error': 'weather-subconvo'    
                      }
                  },
                  '[{bad, horrible, awful}]': {     
    
                      '"Oh no! Bye!"': 'end'
                  },
                  'error': {            
                    
                      '"I do not understand! Bye!"': 'end'
                  }
              }
          },
          '#INT(Tell me the weather.)': {

              'state': 'weather-subconvo',            
    
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
chatbot = DialogueFlow('start', end_state='end')
```
Import DialogueFlow class and create a DialogueFlow object.
This object is your dialogue agent, and `'start'` indicates where the conversation begins.
`end_state='end'` means that the dialouge will exit once it reaches the `'end'` state.

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

You can load transitions dictionaries such as this into your `DialogueFlow` object by calling `load_transitions`:

```python
chatbot.load_transitions(transitions)
```

or by passing transitions into the constructor using the `transitions` keyword parameter:

```python
chatbot = DialogueFlow('start', end_state='end', transitions=transitions)
```

Our current conversation is too short: let's add another turn.

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

Emora STDM supports many approaches to NLU, but let's start off with a simple approach: keyword matching.

```python3
'[{weather, forecast, outside}]'
```
This string defines keywords that will match any user input, as long as the input contains one of the words "weather", "forecast", or "outside".

Let's add some keyword matching to speaker B in our transition dictionary, and make sure we have responses to both:
```python3
transitions = {
    'state': 'start',
    '"Hello!"': {
        '[{bye, goodbye}]': {
            '"Bye bye!"': 'end'
        },
        '[{weather, forecast, outside}]': {
            '"It is sunny!"': 'end'
        }
    }
}
```

Now when the user responds, the user's utterance will be scored against our two intents.
Depending on whether the user utterance was more similar to the phrase "Hi! How are you?" or "Tell me about the weather", 
the bot will classify the user input differently, and thus have a different response.

If you run the system, the bot will appropriately distinguish between you asking the bot how it's doing and asking about the weather:
```
S: Hello!
U: Bye.
S: Bye bye!
```
```
S: Hello!
U: What is the weather like?
S: It is sunny!
```

Let's make the conversation even longer:

```python3
{
  'state': 'start',
  '"Hello."': {
      '[how, you]': {
          '"Good. How are you?"': {
              '[{good, great, okay}]': {            # !!! key phrase matching!
                  '"That\'s great! Bye!"': 'end'
              },
              '[{bad, horrible, awful}]': {         # !!! key phrase matching!
                  '"Oh no! Bye!"': 'end'
              }
          }
      },
      '[{weather, forecast, outside}]': {
          '"It is sunny out!"': {
              'error': {
                  '"Bye!"': 'end'
              }
          }
      }
  }
}
```

Our bot will now ask the user how they are (but only if the user asks first!)
and can usually understand the user's reply.
Specifically, the user's reply has to exactly contain one of the phrases used
in the key phrase matching, for example:

```
S: Hello!
U: Hey, how do you feel today?
S: Good! How are you?
U: I am great today.             <-- matches key phrase "great"
S: That's great! Bye!
```

But what if the user replies without using any of the key phrases we specified?
With how our bot is currently defined, it actually would crash. 
This is because there is no available transition that matches the user utterance.

```
S: Hello!
U: Hey, how do you feel today?
S: Good! How are you?
U: I'm fine.                     <-- doesn't match any transition
*crash*
```

We can fix this by adding an `error` transition. 
Error transitions are special transitions that are able to match any user utterance,
but they are not chosen to update the dialogue state unless no other transition matches. 
To add an error transition, just use the string `"error"` to mark the user transition in the code: 


```python3
{
  'state': 'start',
  '"Hello."': {
      '[how, you]': {
          '"Good. How are you?"': {
              '[{good, great, okay}]': {            # !!! key phrase matching!
                  '"That\'s great! Bye!"': 'end'
              },
              '[{bad, horrible, awful}]': {         # !!! key phrase matching!
                  '"Oh no! Bye!"': 'end'
              },
              'error': {
                  '"I see. Bye!"': 'end'
              }
          }
      },
      '[{weather, forecast, outside}]': {
          '"It is sunny out!"': {
              'error': {
                  '"Bye!"': 'end'
              }
          }
      }
  }
}
```

With the error transition in place, no matter what the user says in response to the bot's question, the chatbot will have a reply.


To learn about adding more advanced NLU to your chatbot, 
refer to the [Natex Tutorial](https://github.com/emora-chat/emora_stdm/blob/master/docs/NatexTutorial.md).


## State References

So far in this tutorial, we have built a chat bot that uses a tree-like json structure to model dialogue.
However, Emora-STDM chatbots are not restricted to tree structures for state-machine-based dialogue management.
Modelling conversation as an arbitrary graph with cycles and diamonds is easy to do by connecting transitions
directly to other points in the dialogue. Doing this requires two steps.

First, the point in the dialogue you want to connect to needs to have a state identifier. 
Second, we link a transition to this identifier.

In fact, we have already done the first step by naming the initial state in our dialogue graph `"start"`.
Let's say we want the dialogue to repeat itself instead of ending by creating a cycle back to this initial state.
We can do so by simply connecting back to `"start"` using the colon `:` notation after defining a transition:
 

```python3
transitions = {
    'state': 'start',
    '"Hello!"': {
        '[{weather, forecast, outside}]': {
            '"It is sunny out!"': {
                'error': 'start'         # !!! Link back to the start state!
            }
        },
        'error': {
            '"Interesting."': {
                'error': 'start'
            }
        }
    }
}
```

The above transition structure would cause a very repetitive conversation, 
but it illustrates how it is easy to create cycles in the conversation graph:

```
S: Hello!
U: What's the weather like?
S: It is sunny out!
U: Okay.                 <-- Transitions back to "start" state!
S: Hello!
U: Didn't you already say hi?
S: Interesting.
...
```

The reason we are able to link back to the start of the conversation is because the starting state is already named.
This is what the line `'state': 'start'` at the top of the json dictionary means.

We can actually use this notation to name any state we want: 
just put `'state': '<state name>'` at the point of the conversation you want to name:

```python3
{
  'state': 'start',
  '"Hello."': {
      'error': {
          '"Good. How are you?"': {
              'state': 'asking-user-mood',    # !!! Named state

              '[{good, great, okay}]': {    
        
                  '"That\'s great! Bye!"': 'end'
              },
              '[{bad, horrible, awful}]': {         
                  '"Oh no! Bye!"': 'end'
              },
              'error': {                                
                  '"I do not understand! Bye!"': 'end'
              }
          }
      },
      '[{weather, forecast, outside}]': {
          'state': 'weather-subconvo',       # !!! Named state
          '"It is sunny out!"': {
              'error': {
                  '"Bye!"': 'end'
              }
          }
      }
  }
}
```

Note that `'state'` is a special key that indicates a state naming, not a transition.
This is similar to how `'error'` is a string identifying a special type of transition.

In the above example, the state `'asking-user-mood'` is the end state of the transition `'"Good. How are you?"'`
and it is the start state of transitions `'[{good, great, okay}]'`, `'{[bad, horrible, awful]}'`, and the `'error'` transition. 
Similarly, `'weather-subconvo'` is the state entered after taking the user transition `'[{weather, forecast, outside}]'`.

Let's now use one of our newly named states to extend the interaction by linking to it:

```python3
{
  'state': 'start',
  '"Hello."': {
      'error': {
          '"Good. How are you?"': {
              'state': 'asking-user-mood',
              '[{good, great, okay}]': {    
                  '"That\'s great! ' 
                  'Know what\'s good about today?"': {
                        'error': 'weather-subconvo'     # !!! Link to weather-subconvo
                  }
              },
              '[{bad, horrible, awful}]': {         
                  '"Oh no! Bye!"': 'end'
              },
              'error': {                                
                  '"I do not understand! Bye!"': 'end'
              }
          }
      },
      '[{weather, forecast, outside}]': {
          'state': 'weather-subconvo',                 # !!! weather-subconvo
          '"It is sunny out!"': {
              'error': {
                  '"Bye!"': 'end'
              }
          }
      }
  }
}
```

Our chatbot now supports two different conversation paths that lead to talking about weather:

```
S: Hello!
U: What's the weather like?
S: It is sunny out!
...
```

```
S: Hello!
U: Hi! How are ya?
S: Good. How are you?
U: I feel good.
S: That's great! Know what's good about today?
U: What?
S: It is sunny out!
...
```


## Want to learn more?

Check out the other [tutorials](https://github.com/emora-chat/emora_stdm/blob/master/README.md#tutorials).
