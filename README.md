# State Transition Dialogue Manager

Emora State Transition Dialogue Manager (Emora STDM) is a dialogue system development framework that seamlessly integrates intent classification, pattern recognition, state machine, and information state approaches to dialogue management and natural language understanding. This allows Emora STDM to support both rapid prototyping and long-term, team-based development workflows, catering to a wide range of developer expertise.

Novice developers, or those who just want to develop a dialogue agent as quickly as possible, can [easily create a state machine based chatbot](/docs/NoviceTutorial.md) using built-in functionality for intent classification and keyword matching. 

Emora STDM also affords a high degree of controllability to experts: it is easy to [integrate NLP models, database queries, and custom logic](), and chatbots can be [created entirely from state update rules](), following [an information state approach to dialogue](https://people.ict.usc.edu/~traum/Papers/traumlarsson.pdf). Although we provide a host of built-in NLP models and useful functionality, your imagination is the limit when extending Emora STDM.

# Quick Start

## Installation

```
pip install emora_stdm
python -m spacy download en_core_web_sm
```

## Hello World Example

```python3
from emora_stdm import DialogueFlow

chatbot = DialogueFlow('start')
transitions = {
    'state': 'start',
    '"Hello. How are you?"': {
        '[{good, okay, fine}]': {
            '"Good. I am doing well too"': {
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

## Overview

![overview image](https://github.com/emora-chat/emora_stdm/blob/master/docs/Approach_%20Demo_%20emora_stdm.svg)

## Tutorials

* [Tutorial for novices](/docs/NoviceTutorial.md), or those with little programming experience
* [MAIN TUTORIAL](), explaining the core functionality of Emora STDM
* [Advanced Tutorial](), explaining advanced and experimental features of the framework
