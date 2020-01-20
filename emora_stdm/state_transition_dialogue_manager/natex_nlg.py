
from lark import Lark, Transformer, Tree, Visitor
from emora_stdm.state_transition_dialogue_manager.stochastic_options import StochasticOptions


class NatexNlg:

    def __init__(self, expression, vars=None, macros=None, ngrams=None):
        self._expression = expression
        self._ngrams = ngrams
        if vars is None:
            self._vars = {}
        else:
            self._vars = vars
        if macros is None:
            self._macros = {}
        else:
            self._macros = macros

    def generate(self, ngrams=None, vars=None, macros=None, debugging=False):
        if vars is not None:
            vars.update(self._vars)
        else:
            vars = self._vars
        if macros is not None:
            macros.update(self._macros)
        else:
            macros = self._macros
        if ngrams is None:
            ngrams = self._ngrams
        macros.update(self._macros)
        if debugging:
            print('NatexNlg generation:')
            if ngrams is not None:
                print('  {:15} {}'.format('Ngrams', ', '.join(ngrams)))
            print('  {:15} {}'.format('Macros', ' '.join(macros.keys())))
            print('  {:15} {}'.format('Steps', '  ' + '-' * 60))
            print('    {:15} {}'.format('Original', self._expression))
        return NatexNlg.Compiler(ngrams, vars, macros, debugging).compile(self._expression)

    def ngrams(self):
        return self._ngrams

    def __str__(self):
        return 'NatexNlg({})'.format(self._expression)

    def __repr__(self):
        return str(self)

    class Compiler(Visitor):
        grammar = r"""
        start: term (","? " "? term)*
        term: rigid_sequence | disjunction | assignment | macro | literal
        rigid_sequence: "[!" term (","? " "? term)+ "]"
        disjunction: "{" term (","? " "? term)+ "}"
        refence: "$" symbol
        assignment: "$" symbol "=" term
        macro: symbol "(" term (","? " "? term)+ ")" 
        literal: /[a-zA-Z]+( +[a-zA-Z]+)*/
        symbol: /[a-z_A-Z.0-9]+/
        """
        parser = Lark(grammar)

        def __init__(self, ngrams, vars, macros, debugging=False):
            self._tree = None
            self._vars = vars
            self._ngrams = ngrams
            self._macros = macros
            self._assignments = {}
            self._debugging = debugging
            self._previous_compile_output = ''

        def compile(self, natex):
            self._tree = self.parser.parse(natex)
            generated = self.visit(self._tree).children[0]
            if self._debugging:
                print('  {:15} {}'.format('Final', generated))
            return generated

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
            tree.children[0] = StochasticOptions(self.to_strings(args)).select()
            if self._debugging: print('    {:15} {}'.format('Disjunction', self._current_compilation(self._tree)))

        def reference(self, tree):
            args = [x.children[0] for x in tree.children]
            tree.data = 'compiled'
            symbol = args[0]
            if symbol in self._assignments:
                value = self._assignments[symbol]
            else:
                value = self._vars[symbol]
            tree.children[0] = value
            if self._debugging: print('    {:15} {}'.format('Var reference', self._current_compilation(self._tree)))

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
            tree.children[0] = StochasticOptions(self._macros[symbol](self._ngrams, self._vars, self._assignments, macro_args)).select()
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
            tree.children[0] = ' '.join(args)

        def _current_compilation(self, tree):
            class DisplayTransformer(Transformer):
                def rigid_sequence(self, args):
                    return '[!' + ', '.join([str(arg) for arg in args]) + ']'
                def disjunction(self, args):
                    return '{' + ', '.join([str(arg) for arg in args]) + '}'
                def reference(self, args):
                    return '$' + args[0]
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
                    return ', '.join(args)
                def compiled(self, args):
                    return str(args[0])
            if not isinstance(tree, Tree):
                return str(tree)
            else:
                return DisplayTransformer().transform(tree)

