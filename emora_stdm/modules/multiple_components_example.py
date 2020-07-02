
from emora_stdm import DialogueFlow, CompositeDialogueFlow

A = DialogueFlow('start')
A.load_transitions({
    'state': 'start',
    '`Let\'s talk about books!`': {
        'error': {
            '`What\'s your favorite book?`': {
                'error': {
                    '`Cool!`': 'end',
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

if __name__ == '__main__':
    C.run()