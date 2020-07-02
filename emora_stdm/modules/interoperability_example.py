
from emora_stdm import DialogueFlow


system = DialogueFlow('start', end_state='end', initial_speaker=DialogueFlow.Speaker.USER)
system.load_transitions({
    'state': 'start',

    '[{hi, hello}]': {

         '`Hi!`':{
             'score': 3.0,

             'error': { '`Bye.`': 'end' }
         }
    },

    'error': { '`Bye`': 'end' }
})

system.load_update_rules({
    '[news]': '`Coronavirus, argh!` (4.0)',
    '[{movie, movies}]': '`Avengers is a good one.` (4.0)',
    '/.*/ (0.1)': '`I\'m not sure I understand.` (2.0)',
})

if __name__ == '__main__':
    system.run(debugging=True)