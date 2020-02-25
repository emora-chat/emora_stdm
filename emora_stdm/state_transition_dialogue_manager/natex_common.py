
agree = '[!-{not, "don\'t", dont, "isn\'t", isnt} ' \
        '[{yes, yeah, yea, yep, yup, sure, think so, i know, absolutely, certainly, surely, definitely}]]'

disagree = '{' + ', '.join([
    '[{no, nay, nah}]',
    '[{absolutely, surely, definitely, certainly, i think} {not}]',
    'i {dont, "don\'t", do not} think so'
]) + '}'

question = '[!{who, what, when, where, why, how, is, does, can, could, should, ' \
           '"isn\'t", "shouldn\'t", "couldn\'t", "can\'t", "aint", "don\'t", do,' \
           'did, was, were, will, "wasn\'t", "weren\'t", "didn\'t", has, had, have} /.*/]'

