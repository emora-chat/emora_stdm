
import regex
from lark import Lark, Transformer, Tree, Visitor

def step(f):
    def compilation_step_function(self, args):
        if self._debugging:
            print(self._current_compilation())
        return f(self, args)
    return compilation_step_function

class Natex:

    def __init__(self, expression):
        self._expression = expression
        self._regex = None
        self._regex_parser = None

    def match(self, natural_language):
        pass

    def compile(self, ngrams: set, macros: dict, debugging=False):
        self._regex = Natex.Compiler(ngrams, macros, debugging).compile(self._expression)

    def regex(self):
        return self._regex

    def __str__(self):
        return 'Natex({})'.format(self._expression)

    def __repr__(self):
        return str(self)

    class Compiler(Visitor):
        grammar = r"""
        start: term
        term: flexible_sequence | rigid_sequence | conjunction | disjunction | negation 
              | regex | assignment | macro | literal
        flexible_sequence: "[" term (","? " "? term)* "]"
        rigid_sequence: "[!" term (","? " "? term)+ "]"
        conjunction: "<" term (","? " "? term)+ ">"
        disjunction: "{" term (","? " "? term)+ "}"
        negation: "-" term
        regex: "/" /[^\/]+/ "/"
        assignment: "$" symbol "=" term
        macro: symbol "(" term (","? " "? term)+ ")" 
        literal: /[a-zA-Z]+( +[a-zA-Z]+)*/
        symbol: /[a-z_A-Z.0-9]+/
        """
        parser = Lark(grammar, propagate_positions=True)

        def __init__(self, ngrams, macros, debugging=False):
            self._tree = None
            self._ngrams = ngrams
            self._macros = macros
            self._assignments = {}
            self._debugging = debugging

        def compile(self, natex):
            self._tree = self.parser.parse(natex)
            self.visit(self._tree)
            return self._tree.compilation

        def to_strings(self, args):
            strings = []
            for arg in args:
                if isinstance(arg, str):
                    strings.append(arg)
                elif isinstance(arg, set):
                    strings.append('|'.join(arg))
            return strings

        def to_sets(self, args):
            sets = []
            for arg in args:
                if isinstance(arg, str):
                    sets.append({arg})
                elif isinstance(arg, set):
                    sets.append(arg)
            return sets

        @step
        def flexible_sequence(self, tree):
            args = tree.children
            tree.compilation =  '.*?' + '.*?'.join(self.to_strings(args)) + '.*'
        @step
        def rigid_sequence(self, tree):
            args = tree.children
            tree.compilation =  r'\W+'.join(self.to_strings(args))
        @step
        def conjunction(self, tree):
            args = tree.children
            tree.compilation =  ''.join(['(?={})'.format(x) for x in self.to_strings(args)])
        @step
        def disjunction(self, tree):
            args = tree.children
            tree.compilation =  '(?:{})'.format('|'.join(self.to_strings(args)))
        @step
        def negation(self, tree):
            args = tree.children
            (arg,) = self.to_strings(args)
            tree.compilation =  '(?:(?:(?!.*{}.*$).)+)'.format(arg)
        @step
        def regex(self, tree):
            args = tree.children
            (arg,) = self.to_strings(args)
            tree.compilation =  arg
        @step
        def assignment(self, tree):
            args = tree.children
            self._assignments[args[0]] = args[1]
            tree.compilation =  args[1]
        @step
        def macro(self, tree):
            args = tree.children
            symbol = args[0]
            macro_args = self.to_sets(args[1:])
            tree.compilation =  self._macros[symbol](self._ngrams, macro_args)

        def literal(self, tree):
            args = tree.children
            (literal,) = args
            tree.compilation = literal

        def symbol(self, tree):
            args = tree.children
            (symbol,) = args
            tree.compilation = symbol

        def term(self, tree):
            args = tree.children
            (term,) = args
            tree.compilation = term

        def start(self, tree):
            args = tree.children
            tree.compilation = args[0]

        def __str__(self):
            return  '<NatexCompiler obj {}>'.format(id(self))

        def _current_compilation(self):
            class Printer(Visitor):
                def get_args(self, args):
                    processed_args = []
                    for arg in args:
                        if hasattr(arg, 'compilation'):
                            processed_args.append(arg.display)
                        else:
                            processed_args
                def flexible_sequence(self, tree):
                    tree.display = '[' + ', '.join([str(arg) for arg in args]) + ']'
                def rigid_sequence(self, tree):
                    tree.display = '[!' + ', '.join([str(arg) for arg in args]) + ']'
                def conjunction(self, tree):
                    tree.display = '<' + ', '.join([str(arg) for arg in args]) + '>'
                def disjunction(self, tree):
                    tree.display = '{' + ', '.join([str(arg) for arg in args]) + '}'
                def negation(self, tree):
                    (arg,) = args
                    tree.display = '-' + str(arg)
                def regex(self, tree):
                    (arg,) = args
                    tree.display = str(arg)
                def assignment(self, tree):
                    tree.display = '${}={}'.format(*args)
                def macro(self, tree):
                    tree.display = args[0] + '(' + ', '.join([str(arg) for arg in args[1:]]) + ')'
                def literal(self, tree):
                    tree.display = str(args[0])
                def symbol(self, tree):
                    tree.display = str(args[0])
                def term(self, tree):
                    tree.display = str(args[0])
                def start(self, tree):
                    tree.display = str(args[0])
            if not isinstance(self._tree, Tree):
                return str(self._tree)
            else:
                return Printer().transform(self._tree)