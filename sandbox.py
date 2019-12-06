
from expression import Expression as E
from dialogue_flow import DialogueFlow, DialogueTransition


if __name__ == '__main__':
    df = DialogueFlow('start')

    df.add_transition(
        'start', 'hobbies_start',
        E('hobby', 'hobbies', 'activity', 'activities', 'things to do',
           'like to do', 'stuff to do'),
        ["lets talk about hobbies", "do you want to talk about fun things to do"]
    )
    df.add_transition(
        'hobbies_start', 'hobby_pref_req',
        E(
            ('you', E('like', 'favorite', 'usually'), E('to do', 'hobby', 'hobbies', 'activity'))
        ),
        [
            'well what do you like to do',
            'what is your favorite hobby'
        ]
    )
    df.add_transition(
        'hobby_pref_req', 'hobbies_start',
        E(
            'sports',
            'reading',
            'piano',
            'violin'
        ),
        [
            'i like sports',
            'reading',
            'my favorite hobby is to play piano'
        ]
    )

    i = input('U: ')
    while True:
        df.user_transition(i)
        print('S:', df.system_transition())
        i = input('U: ')


