

from emora_stdm.state_transition_dialogue_manager.chat_flow import ChatFlow
import emora_stdm.state_transition_dialogue_manager.natex_common as natexes

df = ChatFlow()

system_loop = {
    'state': 'sr',
    '"Have you heard about the corona virus?"':{
        natexes.agree:{
            '"Are you scared?"':{
                'error': 'ur'
            }
        },
        natexes.disagree:{
            '"It\'s gonna kill us all!"':{
                'error': 'ur'
            }
        },
        'error': 'ur'
    }
}

user_loop = {
    'state': 'ur',
    '[how many, died]':{
        '"Millions. We\'re screwed."': 'dinit'
    }
}

df.load_transitions(system_loop, ChatFlow.Speaker.SYSTEM)
df.load_transitions(user_loop, ChatFlow.Speaker.USER)

if __name__ == '__main__':
    df.run(debugging=True)
