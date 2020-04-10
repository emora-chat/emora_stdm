from emora_stdm import DialogueFlow

df = DialogueFlow('root')

transitions = {
    'state': 'root',

    '"So, what have you been up to today?"':{
        'error': {
            '"That\'s interesting. Today, I went on a hike in the woods near my house. There\'s a beautiful nature trail there."':{
                'error':{

                }
            }
        }
    }
}

df.load_transitions(transitions, speaker=DialogueFlow.Speaker.SYSTEM)

if __name__ == '__main__':
    df.run(debugging=False)
