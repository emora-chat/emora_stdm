
import regex
from structpy import I
from lark import Lark, Transformer

_expression_grammar = r"""
root: "\n"? expression "\n"?
expression: literal | (term | literal term | (literal ",")+ literal
                    | literal term literal | term literal)+
term: " "* (flex_seq | sequence | conjunction | disjunction | negation | regex | assign) ","? " "* "\n"?
flex_seq: "(" "\n"? expression "\n"? ")" 
sequence: "[" "\n"? expression "\n"? "]"
conjunction: "<" "\n"? expression "\n"? ">"
disjunction: "{" "\n"? expression "\n"? "}"
negation: "-" term | "-" literal
regex: "/" "\n"? REGEX "\n"? "/"
REGEX: /[a-z A-Z0-9\_(+*)\-\\\^?!={}\[\]:;<>#]+/
literal: " "* (WORD " ")* WORD ","? " "*
WORD: /[a-zA-Z0-9$&:#_.]+/
assign: "%" VAR "=" (term | literal)
VAR: /[a-zA-Z0-9_.]+/
"""

_expression_parser = Lark(_expression_grammar, start='root')

class _ExpressionReducer(Transformer):
    def assign(self, args):
        varname = args[0]
        return r'(?P<{}>{})'.format(varname, args[1])
    def flex_seq(self, args):
        (exp,) = args
        return '.*?' + '.*?'.join(exp.children)
    def sequence(self, args):
        (exp,) = args
        return r'\W*'.join(exp.children)
    def conjunction(self, args):
        (exp,) = args
        return ''.join(['(?={})'.format(term) + '.*' for term in exp.children])
    def disjunction(self, args):
        (exp,) = args
        return '(?:{})'.format('|'.join(exp.children))
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


