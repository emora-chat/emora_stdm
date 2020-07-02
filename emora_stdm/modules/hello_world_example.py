
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

chatbot = DialogueFlow('start')
transitions = {
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

chatbot = DialogueFlow('start')
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
chatbot.load_transitions(transitions)

if __name__ == '__main__':
    chatbot.run()