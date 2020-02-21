
from emora_stdm import DialogueFlow


df = DialogueFlow('root', initial_speaker=DialogueFlow.Speaker.SYSTEM)

flow = {
    'state': 'root',

    'hello': {
        '[hi]': {
            'have you seen a good movie recently':{
                '[yes]': {
                    'cool what is it':{
                        'error': 'root'
                    }
                },
                '[no]':{
                    'ok then': {
                        'error': 'root'
                    }
                }
            },
            'how are you': {
                '[good]': {
                    'thats good': {
                        'error': 'root'
                    }
                },
                '[bad]': {
                    'sorry to hear that':{
                        'error': 'root'
                    }
                }
            }
        },
        '[how, you]': {
            'good': {
                'error': 'root'
            }
        }
    }
}

df.load_transitions(flow, DialogueFlow.Speaker.SYSTEM)

if __name__ == '__main__':
    df.run(debugging=True)