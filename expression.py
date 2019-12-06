
import regex
from structpy import I
from lark import Lark, Transformer

_expression_grammar = """
root: expression
expression: literal | (term | literal term | (literal ",")+ literal
                    | literal term literal | term literal)+
term: " "* (flex_seq | sequence | conjunction | disjunction | negation | regex) ","? " "*
flex_seq: "(" expression ")" 
sequence: "[" expression "]"
conjunction: "<" expression ">"
disjunction: "{" expression "}"
negation: "-" term | "-" literal
regex: "/" REGEX "/"
REGEX: /[a-z A-Z0-9_(+*)\-\\\^?!={}\[\]:;<>#]+/
literal: " "* (WORD " ")* WORD ","? " "*
WORD: /[a-zA-Z$*=_]+/
"""

_expression_parser = Lark(_expression_grammar, start='root')

class _ExpressionReducer(Transformer):
    def flex_seq(self, args):
        (exp,) = args
        return '.*' + '.*'.join(exp.children)
    def sequence(self, args):
        (exp,) = args
        return r'\W*'.join(exp.children)
    def conjunction(self, args):
        (exp,) = args
        return ''.join(['(?=.*{})'.format(term) + '.*' for term in exp.children])
    def disjunction(self, args):
        (exp,) = args
        return '(?:{})'.format('|'.join(['.*' + x for x in exp.children]))
    def negation(self, args):
        exp = args[0]
        return '(?:(?:(?!.*{}.*$).)+)'.format(exp)
    def term(self, args):
        (exp,) = args
        return exp
    def literal(self, args):
        return ' '.join([r'\b{}\b'.format(x.strip()) for x in args]).strip()
    def regex(self, args):
        (exp,) = args
        return exp
    def root(self, args):
        return args[0].children[0]


def init(string):
    tree = _expression_parser.parse(string)
    return _ExpressionReducer().transform(tree)


class Expression:

    def __init__(self, expstring):

        self.re = None
        self._compiled = None

        if expstring[0] not in '-[{<':
            expstring = '({})'.format(expstring)
        tree = _expression_parser.parse(expstring)
        self.re = _ExpressionReducer().transform(tree)

    def match(self, text):
        if self._compiled is None:
            self._compiled = regex.compile(self.re)
        match = self._compiled.match(text + ' ')
        if match is None or match.span()[0] == match.span()[1]:
            return None
        return match

    def express(self, collection):
        collection = list(collection)
        for i, c in enumerate(collection):
            if not isinstance(c, Expression):
                negated = False
                if isinstance(c, list) and c[0] is False:
                    c = c[1:]
                    negated = True
                if isinstance(c, set) and False in c:
                    c.remove(False)
                    negated = True
                if isinstance(c, tuple) and c[0] is False:
                    c = tuple(c[1:])
                    negated = True
                if not negated:
                    collection[i] = str(Expression(c))
                else:
                    collection[i] = str(Expression(False, c))
            else:
                collection[i] = str(c)
        return collection

    def __str__(self):
        return self.re
