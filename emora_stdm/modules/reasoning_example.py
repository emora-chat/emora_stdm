
from emora_stdm import DialogueFlow


system = DialogueFlow('start', initial_speaker=DialogueFlow.Speaker.USER)
system.load_transitions({'state': 'start'})

system.load_update_rules({
    '[my, {husband, wife, kids}]': '#SET($is_adult=True)',
    '{[i, work]}': '#SET($is_adult=True)',
    '#IF($is_adult=True)': '`How is you job going?` (2.0)',
    '/.*/ (0.1)': '`I\'m not sure I understand.` (1)',
})

if __name__ == '__main__':
    system.run()