
from lark import Lark, Transformer, Tree, Visitor
from emora_stdm.state_transition_dialogue_manager.stochastic_options import StochasticOptions


class NatexGenerator:

    def __init__(self, expression, lexicon=None):
        self._expression = expression
        self._lexicon = lexicon

    def generate(self, lexicon=None):
        pass

    def __str__(self):
        return 'NatexGenerator({})'.format(self._expression)

    def __repr__(self):
        return str(self)

    class Compiler(Visitor):
        grammar = r"""
        start: term
        term: flexible_sequence | rigid_sequence | conjunction | disjunction | negation 
              | regex | assignment | macro | literal
        rigid_sequence: "[!" term (","? " "? term)+ "]"
        disjunction: "{" term (","? " "? term)+ "}"
        assignment: "$" symbol "=" term
        macro: symbol "(" term (","? " "? term)+ ")" 
        literal: /[a-zA-Z]+( +[a-zA-Z]+)*/
        symbol: /[a-z_A-Z.0-9]+/
        """
        parser = Lark(grammar)

        def __init__(self, ngrams, macros, debugging=False):
            self._tree = None
            self._ngrams = ngrams
            self._macros = macros
            self._assignments = {}
            self._debugging = debugging
            self._previous_compile_output = ''

        def compile(self, natex):
            self._tree = self.parser.parse(natex)
            return self.visit(self._tree).children[0]

        def to_strings(self, args):
            strings = []
            for arg in args:
                if isinstance(arg, str):
                    strings.append(arg)
                elif isinstance(arg, set):
                    strings.append('(?:' + '|'.join(arg) + ')')
            return strings

        def to_sets(self, args):
            sets = []
            for arg in args:
                if isinstance(arg, str):
                    sets.append({arg})
                elif isinstance(arg, set):
                    sets.append(arg)
            return sets

        def rigid_sequence(self, tree):
            args = [x.children[0] for x in tree.children]
            tree.data = 'compiled'
            tree.children[0] = ' '.join(self.to_strings(args))
            if self._debugging: print('    {:15} {}'.format('Rigid sequence', self._current_compilation(self._tree)))

        def disjunction(self, tree):
            args = [x.children[0] for x in tree.children]
            tree.data = 'compiled'
            tree.children[0] = '(?:{})'.format('|'.join(self.to_strings(args)))
            if self._debugging: print('    {:15} {}'.format('Disjunction', self._current_compilation(self._tree)))

        def assignment(self, tree):
            args = [x.children[0] for x in tree.children]
            tree.data = 'compiled'
            self._assignments[args[0]] = args[1]
            value = self.to_strings([args[1]])[0]
            tree.children[0] = value
            if self._debugging: print('    {:15} {}'.format('Assignment', self._current_compilation(self._tree)))

        def macro(self, tree):
            args = [x.children[0] for x in tree.children]
            tree.data = 'compiled'
            symbol = args[0]
            macro_args = self.to_sets(args[1:])
            tree.children[0] = StochasticOptions(self._macros[symbol](self._ngrams, macro_args)).select()
            if self._debugging: print('    {:15} {}'.format(symbol, self._current_compilation(self._tree)))

        def literal(self, tree):
            args = tree.children
            tree.data = 'compiled'
            (literal,) = args
            tree.children[0] = literal

        def symbol(self, tree):
            args = tree.children
            tree.data = 'compiled'
            (symbol,) = args
            tree.children[0] = symbol

        def term(self, tree):
            args = [x.children[0] for x in tree.children]
            tree.data = 'compiled'
            (term,) = args
            tree.children[0] = term

        def start(self, tree):
            args = [x.children[0] for x in tree.children]
            tree.data = 'compiled'
            tree.children[0] = args[0]

        def __str__(self):
            return '<NatexCompiler obj {}>'.format(id(self))

        def _current_compilation(self, tree):
            class DisplayTransformer(Transformer):
                def flexible_sequence(self, args):
                    return '[' + ', '.join([str(arg) for arg in args]) + ']'

                def rigid_sequence(self, args):
                    return '[!' + ', '.join([str(arg) for arg in args]) + ']'

                def conjunction(self, args):
                    return '<' + ', '.join([str(arg) for arg in args]) + '>'

                def disjunction(self, args):
                    return '{' + ', '.join([str(arg) for arg in args]) + '}'

                def negation(self, args):
                    (arg,) = args
                    return '-' + str(arg)

                def regex(self, args):
                    (arg,) = args
                    return str(arg)

                def assignment(self, args):
                    return '${}={}'.format(*args)

                def macro(self, args):
                    return args[0] + '(' + ', '.join([str(arg) for arg in args[1:]]) + ')'

                def literal(self, args):
                    return str(args[0])

                def symbol(self, args):
                    return str(args[0])

                def term(self, args):
                    return str(args[0])

                def start(self, args):
                    return str(args[0])

                def compiled(self, args):
                    return str(args[0])

            if not isinstance(tree, Tree):
                return str(tree)
            else:
                return DisplayTransformer().transform(tree)

