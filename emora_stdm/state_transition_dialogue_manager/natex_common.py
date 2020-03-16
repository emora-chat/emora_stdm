
agree = '[!-{not, "don\'t", dont, "isn\'t", isnt} ' \
        '[{yes, yeah, yea, yep, yup, sure, think so, i know, absolutely, certainly, surely, definitely}]]'

disagree = '{' + ', '.join([
    '[{no, nay, nah, not really}]',
    '[{absolutely, surely, definitely, certainly, i think} {not}]',
    '[i {dont, "don\'t", do not} think so]'
]) + '}'

question = '[!/([^ ]+)?/ {who, what, when, where, why, how, is, does, can, could, should, ' \
           '"isn\'t", "shouldn\'t", "couldn\'t", "can\'t", "ain\'t", "don\'t", do,' \
           'did, was, were, will, "wasn\'t", "weren\'t", "didn\'t", has, had, have} /.*/]'

negation = '{not, "don\'t" "can\'t" "won\'t" "shouldn\'t" "cannot" "didn\'t" "doesn\'t"' \
           ' "isn\'t" "couldn\'t" "haven\'t" "aren\'t" "never" "impossible" "unlikely" ' \
           '"no way"}'

