
import regex
from structpy import I
from lark import Lark, Transformer

_expression_grammar = """
root: expression
expression: literal | (term | literal term | literal "," literal | literal "," literal "," literal 
                    | literal term literal | term literal)+
term: (flex_seq | sequence | conjunction | disjunction | negation | regex)
flex_seq: "(" expression ")" 
sequence: "[" expression "]"
conjunction: "<" expression ">"
disjunction: "{" expression "}"
negation: "-" term | "-" literal
regex: "/" REGEX "/"
REGEX: /[a-z A-Z0-9_(+*)\-\\\^?!={}\[\]:;<>#]+/
literal: LITERAL
LITERAL: /[a-z A-Z$*=]+/
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
    def term(self, args):
        (exp,) = args
        return exp
    def literal(self, args):
        (exp,) = args
        return exp.strip()
    def regex(self, args):
        (exp,) = args
        return exp
    def root(self, args):
        return self.flex_seq(args)


def init(string):
    tree = _expression_parser.parse(string)
    return _ExpressionReducer().transform(tree)

class Expression:

    def __init__(self, *args):

        self._expression = None
        self._compiled = None

        negated = False
        if args[0] is False:
            args = args[1:]
            negated = True

        # expression literal
        if len(args) == 1 and isinstance(args[0], str):
            literal = args[0]
            formatter = '{}'
            if '*' == literal[0] and '*' == literal[-1]:
                self.re = ' *{} *'.format(formatter.format(literal[1:-1]))
            elif '*' == literal[0]:
                self.re = r' *{}\b'.format(formatter.format(literal[1:]))
            elif '*' == literal[-1]:
                self.re = r' *\b{} *'.format(formatter.format(literal[:-1]))
            else:
                self.re = r' *\b{}\b *'.format(formatter.format(literal))

        # expression conjunction
        elif len(args) == 1 and isinstance(args[0], set):
            self.re = ''
            conjunction = self.express(args[0])
            for term in conjunction:
                self.re += '(?=.*{})'.format(term)
            self.re += '.*'

        # expression disjunction
        elif len(args) > 1:
            disjunction = self.express(args)
            self.re = '(?:{})'.format('|'.join(['.*' + x for x in disjunction]))

        # expression sequence (inflexible)
        elif len(args) == 1 and isinstance(args[0], list):
            seq = self.express(args[0])
            self.re = r'\W*'.join(seq)

        # expression sequence (flexible)
        elif len(args) == 1 and isinstance(args[0], tuple):
            seq = self.express(args[0])
            self.re = '.*' + '.*'.join(seq) + '.*'

        # expression negation
        if negated:
            self.re = '(?:(?:(?!.*{}.*$).)+)'.format(self.re)

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
