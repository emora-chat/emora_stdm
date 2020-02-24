
from emora_stdm import DialogueFlow
from emora_stdm.state_transition_dialogue_manager import natex_common as natexes
import os

df = DialogueFlow(initial_state="system_root", kb=os.path.join('modules','family.json'))


'''
birthday_friend: told user friend's bday is coming
birthday_friend_name: told user friend's name
birthday_friend_gift: told user planned gift
birthday_friend_gift_rec: planned gift to get friend
birthday_friend_no_help: user is not helping emora

'''

flow = {
    'state': 'system_root',

    '"Oh, did i tell you? My friend\'s birthday is coming up. I\'m thinking of getting her a music box. What do you think, is it a good gift?"': {
        'prepend': '#GATE(birthday_friend:None) #SET($birthday_friend=True, $birthday_friend_gift=True)',

        'error': 'user_root',

        natexes.agree: {
            '"Ok, great! I hope she really likes it. Thanks for your help!"': {
                'error': 'user_root'
            }
        },
        natexes.disagree:{
            '"Oh alright. Well, what do you think I should get her?"': {
                'error': 'user_root'
            }
        }
    }
}

user_flow = {
    'state': 'user_root',
    'error': 'system_root'
}

df.load_transitions(flow)
df.load_transitions(user_flow, speaker=DialogueFlow.Speaker.USER)

df.state_settings('user_root').update(user_multi_hop=True)
df.state_settings('system_root').update(system_multi_hop=True)

if __name__ == '__main__':

    df.run(debugging=True)

































