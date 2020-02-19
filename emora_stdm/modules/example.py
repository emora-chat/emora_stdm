
from emora_stdm import DialogueFlow



df = DialogueFlow('start', initial_speaker=DialogueFlow.Speaker.SYSTEM)

df.add_system_transition('start', 'greet', '"Hello, how are you?"')
df.add_user_transition('greet', 'good', '[{good, great, wonderful, fantastic, spectacular, nice, fine}]')
df.add_user_transition('greet', 'bad', '[!-not {bad, horrible, sad, depressing}]')
df.set_error_successor('greet', 'greet end')
df.add_system_transition('bad', 'sympathy', '"Sorry to hear that. Do you want to tell me about it?"')
df.add_user_transition('sympathy', 'greet end', 'no')
df.set_error_successor('sympathy', 'more sympathy')
df.add_system_transition('greet end', 'day', '"Ok. So, what have you been up to?"')
df.add_system_transition('good', 'day', '"That\'s great, what have you been doing today?"')
df.set_error_successor('day', 'reaction')
df.add_system_transition('reaction', 'end', '"Alright, it sounds like you had an interesting day."')
df.add_system_transition('more sympathy', 'end', '"That\'s awful. I hope your day gets better."')

if __name__ == '__main__':

    df.run()
