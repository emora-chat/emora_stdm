
from emora_stdm import DialogueFlow


system = DialogueFlow('start', initial_speaker=DialogueFlow.Speaker.USER)
system.load_transitions({'state': 'start', 'error': {'` `': {'score': -1, 'state': 'start'}}})

system.load_update_rules({
    '[news]': '`Coronavirus, argh!` (1)',
    '[{movie, movies}]': '`Avengers is a good one.` (1)',
    '/.*/ (0.1)': '`I\'m not sure I understand.` (1)',
})

if __name__ == '__main__':
    system.run()