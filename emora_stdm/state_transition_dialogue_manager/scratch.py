from emora_stdm import Macro


class MyMacro(Macro):

    # optionally, define constructor if macro needs access to additional data
    def __init__(self, x):
        self.x = x

    # define method to run when macro is evaluated in Natex
    def run(self, ngrams, vars, args):
        """
        :param ngrams: an Ngrams object defining the set of all ngrams in the
                       input utterance (for NLU) or vocabulary (for NLG). Treat
                        like a set for all ngrams, or get a specific ngram set
                        using ngrams[n]. Get original string using .text()
        :param vars: a reference to the dictionary of variables
        :param args: a list of arguments passed to the macro from the Natex
        :returns: string, set, boolean, or arbitrary object
                  returning a string will replace the macro call with that string
                  in the natex
                  returning a set of strings replaces macro with a disjunction
                  returning a boolean will replace the macro with wildcards (True)
                  or an unmatchable character sequence (False)
                  returning an arbitrary object is only used to pass data to other macros
        """
        return ' '.join(['hello ' + args[0]] * self.x)


from emora_stdm import NatexNLU

if __name__ == '__main__':
    natex = NatexNLU('[!oh #MyMacro(there) how are you]', macros={'MyMacro': MyMacro(2)})
    assert natex.match('oh hello there hello there how are you')