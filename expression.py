
import regex
from structpy import I


class Expression:
    """
    1. disjunction of expressions
    2. negation of disjunction of expressions

    Expressions:
        - string literal
        - ontology class
        - expression sequence
        - conjunction of expressions
        - disjunction of expressions
        - negation of disjunction of expressions
    """

    def __init__(self, *args, name=None):

        self._compiled = None

        negated = False
        if args[0] is False:
            args = args[1:]
            negated = True

        # expression literal
        if len(args) == 1 and isinstance(args[0], str):
            literal = args[0]
            if name is not None:
                formatter = '(?P<{}>{{}})'.format(name)
            else:
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
            if name is not None:
                for term in conjunction[:-1]:
                    self.re += '(?=.*{})'.format(term)
                self.re += '(?=(?P<{}>.*{}))'.format(name, conjunction[-1])
            else:
                for term in conjunction:
                    self.re += '(?=.*{})'.format(term)
            self.re += '.*'

        # expression disjunction
        elif len(args) > 1:
            disjunction = self.express(args)
            if name is not None:
                self.re = '(?:{})'.format('|'.join(['.*' + r'(?P<{}>{})'.format(name, x)
                                    for x in disjunction]))
            else:
                self.re = '(?:{})'.format('|'.join(['.*' + x for x in disjunction]))

        # expression sequence (inflexible)
        elif len(args) == 1 and isinstance(args[0], list):
            seq = self.express(args[0])
            if name is not None:
                self.re = r'(?P<{}>{})'.format(name, r'\W*'.join(seq))
            else:
                self.re = r'\W*'.join(seq)

        # expression sequence (flexible)
        elif len(args) == 1 and isinstance(args[0], tuple):
            seq = self.express(args[0])
            if name is not None:
                self.re = r'.*(?P<{}>{}).*'.format(name, '.*'.join(seq))
            else:
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
