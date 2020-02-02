
import regex
from lark import Lark, Transformer, Tree, Visitor
from emora_stdm.state_transition_dialogue_manager.stochastic_options import StochasticOptions
from emora_stdm.state_transition_dialogue_manager.natex_nlu import NatexNLU


class NatexNLG:

    def __init__(self, expression, macros=None, ngrams=None):
        self._ngrams = ngrams
        if macros is None:
            self._macros = {}
        else:
            self._macros = macros
        if isinstance(expression, str):
            self._expression = expression
        elif isinstance(expression, list) or isinstance(expression, set):
            item = next(iter(expression))
            if isinstance(item, str):
                self._expression = '{' + ', '.join(expression) + '}'
            elif isinstance(item, NatexNLG):
                raise NotImplementedError()
        elif isinstance(expression, NatexNLG):
            self._expression = expression.expression()
            self._macros = dict(expression.macros())
            self._macros.update(macros)

    def generate(self, ngrams=None, vars=None, macros=None, debugging=False):
        if vars is None:
            vars = {}
        original_vars = vars
        vars = dict(vars)
        if macros is not None:
            for k, v in self._macros.items():
                if k not in macros:
                    macros[k] = v
        else:
            macros = self._macros
        if ngrams is None:
            ngrams = self._ngrams
        if debugging:
            print('NatexNlg generation:')
            if ngrams is not None:
                print('  {:15} {}'.format('Ngrams', ', '.join(ngrams)))
            print('  {:15} {}'.format('Macros', ' '.join(macros.keys())))
            print('  {:15} {}'.format('Vars', ', '.join([k + '=' + str(v) for k, v in vars.items()])))
            print('  {:15} {}'.format('Steps', '  ' + '-' * 60))
            print('    {:15} {}'.format('Original', self._expression))
        compiler = NatexNLG.Compiler(ngrams, vars, macros, debugging)
        generation = compiler.compile(self._expression)
        if self.is_complete(generation):
            original_vars.update(vars)
            return generation
        else:
            return None

    def is_complete(self, string=None):
        if string is None:
            string = self._expression
        if '_' in string:
            return False
        return bool(regex.fullmatch(r'[^$]+', string))

    def ngrams(self):
        return self._ngrams

    def expression(self):
        return self._expression

    def macros(self):
        return self._macros

    def __str__(self):
        return 'NatexNlg({})'.format(self._expression)

    def __repr__(self):
        return str(self)

    class Compiler(Visitor):
        grammar = r"""
        start: term (","? " "? term)*
        term: rigid_sequence | disjunction | assignment | reference | macro | literal
        rigid_sequence: "[!" " "? term (","? " "? term)* "]"
        disjunction: "{" term (","? " "? term)* "}"
        reference: "$" symbol
        assignment: "$" symbol "=" term
        macro: "#" symbol ( "(" term? (","? " "? term)* ")" )? 
        literal: /[a-z_A-Z@.0-9]+( +[a-z_A-Z@.0-9]+)*/ | "\"" /[^\"]+/ "\""
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

        def assignments(self):
            return self._assignments

        def to_strings(self, args):
            strings = []
            for arg in args:
                if isinstance(arg, str):
                    strings.append(arg)
                elif isinstance(arg, set):
                    if arg:
                        strings.append(StochasticOptions(arg).select())
                    else:
                        strings.append('_EMPTY_SET_')
                elif isinstance(arg, bool):
                    if arg:
                        strings.append('')
                    else:
                        strings.append('_FALSE_')
                elif arg is None:
                    strings.append('')
            return strings

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
            elif symbol in self._vars:
                value = self._vars[symbol]
            else:
                value = '_{}_NOT_FOUND_'.format(symbol)
            tree.children[0] = value
            if self._debugging: print('    {:15} {}'.format('Var reference', self._current_compilation(self._tree)))

        def assignment(self, tree):
            args = [x.children[0] for x in tree.children]
            tree.data = 'compiled'
            value = self.to_strings([args[1]])[0]
            self._assignments[args[0]] = value
            self._vars[args[0]] = value
            tree.children[0] = value
            if self._debugging: print('    {:15} {}'.format('Assignment', self._current_compilation(self._tree)))

        def macro(self, tree):
            args = [x.children[0] for x in tree.children]
            tree.data = 'compiled'
            symbol = args[0]
            macro_args = args[1:]
            if symbol in self._macros:
                macro = self._macros[symbol]
                try:
                    tree.children[0] = macro(self._ngrams, self._vars, macro_args)
                except Exception as e:
                    if self._debugging: print('ERROR: Macro {} raised exception {}'.format(symbol, repr(e)))
                    tree.children[0] = '_MACRO_EXCEPTION_'
                if self._debugging: print('    {:15} {}'.format(symbol, self._current_compilation(self._tree)))
            else:
                if self._debugging: print('ERROR: Macro {} not found'.format(symbol))
                tree.children[0] = '_MACRO_NOT_FOUND_'

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
            tree.children[0] = ' '.join(self.to_strings(args))

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
                    return '#' + args[0] + '(' + ', '.join([str(arg) for arg in args[1:]]) + ')'
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

