
import os
print(os.getcwd())

from emora_stdm import DialogueFlow

df = DialogueFlow('start')
df.add_user_transition('start', 'success', '/.*/')
df.set_error_successor('start', 'fail')
df.add_system_transition('success', 'start', 'success')
df.add_system_transition('fail', 'start', 'fail')

df.knowledge_base().load_json_file('_common.json')

if __name__ == '__main__':
    while True:
        i = input('>> ')
        if 'natex ' in i[:len('natex ')]:
            df.set_transition_natex('start', 'success', DialogueFlow.Speaker.USER, i[len('natex '):])
        else:
            df.set_speaker(DialogueFlow.Speaker.USER)
            df.user_turn(i, debugging=True)
            df.set_speaker(DialogueFlow.Speaker.SYSTEM)
            print(df.system_turn(debugging=False))
