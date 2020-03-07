
from emora_stdm.state_transition_dialogue_manager.update_rule import UpdateRule
from collections import defaultdict


class UpdateRules:

    def __init__(self, vars=None, macros=None):
        if vars is None:
            vars = {}
        if macros is None:
            macros = {}
        self.vars = vars
        self.rules = []
        self.untapped = []
        self.macros = macros

    def set_vars(self, vars):
        self.vars = vars
        for rule in self.rules:
            rule.set_vars(vars)

    def add(self, precondition, postcondition=''):
        self.rules.append(UpdateRule(precondition, postcondition, vars=self.vars, macros=self.macros))

    def update(self, user_input, debugging=False):
        self.rules = sorted(self.rules, key=lambda x: x.precondition_score, reverse=True)
        self.untapped = self.rules
        response = None
        converged = False
        while not converged:
            converged, response = self.update_step(user_input, debugging=debugging)
        return response

    def update_step(self, user_input, debugging=False):
        for i, rule in enumerate(self.untapped):
            try:
                satisfaction = rule.satisfied(user_input, debugging=debugging)
            except RuntimeError as e:
                print('Failed information state update condition check:')
                print('  ', rule)
                print(e)
                del self.untapped[i]
                return False, None
            if satisfaction:
                generation = None
                if debugging:
                    print('Rule triggered: ', rule.precondition, '==>', rule.postcondition)
                if rule.postcondition is not None:
                    try:
                        gen = rule.apply(debugging=debugging)
                    except RuntimeError as e:
                        print('Failed information state update application')
                        print('  ', rule)
                        print(e)
                        del self.untapped[i]
                        return False, None
                    if rule.postcondition_score is not None:
                        generation = (gen, rule.postcondition_score)
                        del self.untapped[i]
                        return True, generation
                del self.untapped[i]
                return False, generation
        return True, None