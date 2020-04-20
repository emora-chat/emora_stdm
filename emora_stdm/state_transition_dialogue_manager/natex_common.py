
from emora_stdm.state_transition_dialogue_manager.macro import Macro
from typing import Union, Set, List, Dict, Callable, Tuple, NoReturn, Any
from emora_stdm.state_transition_dialogue_manager.ngrams import Ngrams
from emora_stdm.state_transition_dialogue_manager.natex_nlu import NatexNLU

def CommonNatexMacro(natex_string):
    class _CommonNatex(Macro):

        def __init__(self):
            self.natex = NatexNLU(natex_string)
            self.natex.compile()
            self.natex._regex = self.natex.regex().replace("_END_", "").strip()

        def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
            return self.natex.regex()
    return _CommonNatex


agree = '[!-{not, "don\'t", dont, "isn\'t", isnt} {{sure, i know, "I know"}' \
        '[{yes, yeah, yea, yep, yup, think so, i know, absolutely, ' \
        'certainly, surely, definitely, probably, true, of course}]}]'
Agree = CommonNatexMacro(agree)

disagree = '{' + ', '.join([
    '[{no, nay, nah, not really}]',
    '[{absolutely, surely, definitely, certainly, i think} {not}]',
    '[i {dont, "don\'t", do not} think so]'
]) + '}'
Disagree = CommonNatexMacro(disagree)

question = '{[!/([^ ]+)?/ {who, what, when, where, why, how} /.*/], ' \
           '[!{is, does, can, could, should, ' \
           '"isnt", "shouldnt", "couldnt", "cant", "aint", "dont", do,' \
           'did, was, were, will, "wasnt", "werent", "didnt", has, had, have} /.*/]}'
Question = CommonNatexMacro(question)

negation = '{not, "dont", "cant", "wont", "shouldnt", "cannot", "didnt", "doesnt",' \
           ' "isnt", "couldnt", "havent", "arent", "never", "impossible", "unlikely", ' \
           '"no way", "none", "nothing"}'
Negation = CommonNatexMacro(negation)

confirm = '{%s, [!-{%s, %s} [{okay, ok, alright, i understand, understood}]]}' % (agree, disagree, negation)
Confirm = CommonNatexMacro(confirm)

dont_know = '[{' \
                    'dont know,do not know,unsure,[not,{sure,certain}],hard to say,no idea,uncertain,[!no {opinion,opinions,idea,ideas,thought,thoughts,knowledge}],' \
                    '[{dont,do not}, have, {opinion,opinions,idea,ideas,thought,thoughts,knowledge}],' \
                    '[!{cant,cannot,dont} {think,remember,recall}]' \
                    '}]'
DontKnow = CommonNatexMacro(dont_know)

maybe = '[{maybe,possibly,sort of,kind of,kinda,a little,at times,sometimes,could be,potentially,its possible}]'
Maybe = CommonNatexMacro(dont_know)


if __name__ == '__main__':
    from emora_stdm.state_transition_dialogue_manager.natex_nlu import NatexNLU
    print(NatexNLU(question).match("i don't know"))