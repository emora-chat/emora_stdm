
agree = '[!-{not, "don\'t", dont, "isn\'t", isnt} {{sure, i know, "I know"}' \
        '[{yes, yeah, yea, yep, yup, think so, i know, absolutely, ' \
        'certainly, surely, definitely, probably, true, of course}]}]'

disagree = '{' + ', '.join([
    '[{no, nay, nah, not really}]',
    '[{absolutely, surely, definitely, certainly, i think} {not}]',
    '[i {dont, "don\'t", do not} think so]'
]) + '}'

question = '{[!/([^ ]+)?/ {who, what, when, where, why, how} /.*/], ' \
           '[!{is, does, can, could, should, ' \
           '"isnt", "shouldnt", "couldnt", "cant", "aint", "dont", do,' \
           'did, was, were, will, "wasnt", "werent", "didnt", has, had, have} /.*/]}'

negation = '{not, "dont", "cant", "wont", "shouldnt", "cannot", "didnt", "doesnt",' \
           ' "isnt", "couldnt", "havent", "arent", "never", "impossible", "unlikely", ' \
           '"no way", "none", "nothing"}'

if __name__ == '__main__':
    from emora_stdm.state_transition_dialogue_manager.natex_nlu import NatexNLU
    print(NatexNLU(question).match("i don't know"))