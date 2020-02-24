
agree = '[!-{not, "don\'t", dont, "isn\'t", isnt} [{yes, yeah, yea, yep, yup, sure, think so, i know, absolutely, certainly, surely, definitely}]]'

disagree = '{' + ', '.join([
    '[{no, nay, nah}]',
    '[{absolutely, surely, definitely, certainly, i think} {not}]',
    'i {dont, "don\'t", do not} think so'
]) + '}'

