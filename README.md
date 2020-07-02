# State Transition Dialogue Manager

Emora State Transition Dialogue Manager (Emora STDM) is a dialogue system development framework that seamlessly integrates intent classification, pattern recognition, state machine, and information state approaches to dialogue management and natural language understanding. This allows Emora STDM to support both rapid prototyping and long-term, team-based development workflows, catering to a wide range of developer expertise.

Novice developers, or those who just want to develop a dialogue agent as quickly as possible, can easily create a state machine based chatbot using built-in functionality for intent classification and keyword matching. 

Emora STDM also affords a high degree of controllability to experts: it is easy to integrate NLP models, database queries, and custom logic, and chatbots can be created entirely from state update rules, following an information state approach ([ref](https://people.ict.usc.edu/~traum/Papers/traumlarsson.pdf)) to dialogue. Although we provide a host of built-in NLP models and useful functionality, your imagination is the limit when extending Emora STDM.

Links: [Github](https://github.com/emora-chat/emora_stdm)  [Paper](https://arxiv.org/abs/2006.06143)

# Quick Start

## Installation
```
pip install emora_stdm
python -m spacy download en_core_web_md
```

Once installed, see if you can run the Hello World example below, and check out the [tutorials](https://github.com/emora-chat/emora_stdm/blob/master/README.md#tutorials).

## Hello World Example

Below is an example of a simple chatbot created with Emora STDM.
The easiest way to add content to a chatbot is to use this nested dictionary syntax.

```python3
from emora_stdm import DialogueFlow

chatbot = DialogueFlow('start')
transitions = {
    'state': 'start',
    '"Hello. How are you?"': {
        '[{good, okay, fine}]': {
            '"Good. I am doing well too."': {
                'error': {
                    '"See you later!"': 'end'
                }
            }
        },
        'error': {
            '"Well I hope your day gets better!"': {
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
Running the above code will allow you to interact with this chatbot.
It asks how you are doing, and will respond differently depending on whether or not you included one of the keywords {"good", "fine", "okay"} in your answer. Below is a sample conversation produced by running the above code 
(S for system, U for user utterance):

```
S: Hello. How are you?
U: I'm good. How are you?
S: Good. I am doing well too.
U: Great!
S: See you later!
```

# Description

![overview image](https://github.com/emora-chat/emora_stdm/blob/master/docs/Approach_%20Demo_%20emora_stdm.svg)

Dialogue management in Emora STDM is performed in two ways: 
1) updating the state machine defined by the *Dialogue Graph* and 
2) applying information state *Update Rules*, which are structured as if...then... conditionals. 

Each turn of conversation,the Dialogue Graph is updated to interpret the user input and provide an appropriate response.
The Dialogue Graph is a state machine describing possible "pathways" of conversation, where each transition/edge represents either a sysem or user turn, and each state/node represents a set of options for what could be said next.
A full turn of conversation (user input + system response) results in two Dialogue Graph State updates--one representing an interpretation of the user turn, and the second representing a decision of the system for how to respond.

**On the user's turn**, each transition out of the current Dialogue Graph State (node) represents a unique interpretation of the user input.
The user input is evaluated against each out transition, and when a transition matches, the Dialogue Graph State is updated to the target of the transition.
(Note that the user input will *always* match a transition marked as `'error'`, but this transition is only accepted if no other transitions match the input).

**During the system turn**, each outgoing transition from the current Dialogue Graph State is a possible response. 
The system will select one of these response options based on a priority score of each transition, or randomly if the priorities of all the options are the same.
The selected transition will be used to produce the system response, and update the Dialogue Graph State.


Most simple dialogue agents will not have any update rules.
However, Update Rules can very useful to maninpulate state variables and perform complex interactions.
Before updating the Dialogue Graph, Update Rules are iteratively applied by evaluating each of their precondition Natexes on the user input, and applying the postcondition if the precondition succeeds.
The iteration continues until no more rules preconditions pass, at which point the Dialogue Graph update is performed.
You can read more about Update Rules in the [Update Rules Tutorial](/docs/UpdateRulesTutorial.md).

# Tutorials

* [**Dialogue Graph Tutorial**](/docs/DialogueGraphTutorial.md), explaining the core dialogue management functionality of Emora STDM
* [**Natex Tutorial**](/docs/NatexTutorial.md), explaining the framework's core natural language understanding and generation functionality
* [**Update Rules Tutorial**](/docs/UpdateRulesTutorial.md), explaining how to create dialogue agents using Update Rules instead of the Dialogue Graph 
* [Ontology Example](/docs/OntologyTutorial.md), showing how to use an ontology to efficiently categorize entities.
* [Multiple Components Example](/docs/MultipleComponentsTutorial.md), a quick example of multiple dialogue agents being combined into a single larger system.