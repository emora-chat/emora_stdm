
import regex
from structpy import I
from lark import Lark, Transformer

_expression_grammar = """
root: expression
expression: literal | (term | literal term | (literal ",")+ literal
                    | literal term literal | term literal)+
term: " "* (flex_seq | sequence | conjunction | disjunction | negation | regex | assign) ","? " "*
flex_seq: "(" expression ")" 
sequence: "[" expression "]"
conjunction: "<" expression ">"
disjunction: "{" expression "}"
negation: "-" term | "-" literal
regex: "/" REGEX "/"
REGEX: /[a-z A-Z0-9_(+*)\-\\\^?!={}\[\]:;<>#]+/
literal: " "* (WORD " ")* WORD ","? " "*
WORD: /[a-zA-Z0-9$]+/
assign: "%" VAR "=" (term | literal)
VAR: /[a-zA-Z0-9_]+/
"""

_expression_parser = Lark(_expression_grammar, start='root')

class _ExpressionReducer(Transformer):
    def assign(self, args):
        varname = args[0]
        return r'(?P<{}>{})'.format(varname, args[1])
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


class Expression:

    def __init__(self, expstring):

        self.re = None
        self._compiled = None

        if expstring[0] not in '-[{<':
            expstring = '({})'.format(expstring)
        tree = _expression_parser.parse(expstring)
        self.re = _ExpressionReducer().transform(tree)

    def match(self, text, vars=None):
        expression = self.re
        compilation = self._compiled
        if vars:
            for var, val in vars.items():
                expression.replace('$'+var, val)
            compilation = regex.compile(expression)
        elif compilation is None:
            self._compiled = regex.compile(expression)
            compilation = self._compiled
        match = compilation.match(text + ' ')
        if match is None or match.span()[0] == match.span()[1]:
            return None, {}
        return match, match.groupdict()

    def __str__(self):
        return self.re
