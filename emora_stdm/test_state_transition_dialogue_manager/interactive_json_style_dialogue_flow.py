
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

df.state_settings('root').update(system_multi_hop=True)
df.add_state('recovery_question', global_nlu='[!{do, who, what, when, where, why, how, is, can, should}, /.*/]')
df.add_system_transition('recovery_question', 'root', '"Hmm.. I\'m not sure."')

df.add_user_transition('x', 'y', '#ANY($myvar=something, $other=somethingelse) [hello]')

while True:
    df.system_turn()
    v = input()
    var, val = v.split('=')
    df.vars().update({var: val})
    df.user_turn(input())


if __name__ == '__main__':
    df.run(debugging=True)