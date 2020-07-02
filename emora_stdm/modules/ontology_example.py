
from emora_stdm import DialogueFlow
import json


df = DialogueFlow('start')
df.knowledge_base().load_json_file('ontology_example.json')
df.load_transitions({
    'state': 'start',

    '`What is your favorite animal?`': {

        '[#ONT(mammal)]': {

            '`I think mammals are cool too!`': 'start'
        },

        '[#ONT(reptile)]': {

            '`Reptiles are cool.`': 'start'
        },

        '[$animal=#ONT(animal)]': {
            'score': 0.5,

            '`I like` $animal `too.`': 'start'
        },

        'error': {

            '`I\'ve never heard of that animal.`': 'start'
        }
    }
})

if __name__ == '__main__':
    df.run()


