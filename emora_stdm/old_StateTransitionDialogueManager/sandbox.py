from emora_stdm.old_StateTransitionDialogueManager.dialogue_flow import DialogueFlow

if __name__ == '__main__':
    df = DialogueFlow('start')

    df.add_transition(
        'start', 'hobbies_start',
        '{hobby, hobbies, things to do}',
        ["lets talk about hobbies", "do you want to talk about fun things to do"]
    )
    df.add_transition(
        'hobbies_start', 'hobby_pref_req',
        '{you, your} {like, favorite, enjoy}',
        [
            'well what do you like to do',
            'what is your favorite hobby'
        ]
    )
    df.add_transition(
        'hobby_pref_req', 'hobby_appraise',
        'i, {like, enjoy, favorite}, %hobby={talking, reading, sports, piano}, you, {like, enjoy, favorite}',
        [
            'i enjoy talking to people what do you like to do'
        ]
    )
    df.add_transition(
        'hobby_appraise', 'start',
        '{i, like, too}',
        [
            'i like $hobby too'
        ]
    )
    df.add_transition(
        'hobby_pref_req', 'hobbies_start',
        '{sports, reading, piano, violin}',
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


