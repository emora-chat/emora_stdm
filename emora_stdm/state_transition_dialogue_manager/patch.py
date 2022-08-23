"""
Patch notes

* Tracking jump state for stack as the best-next local system state (def set_system_stack_state)
* Added built in #JMP and #RET macros that use the jump state tracking
* loading transitions now includes
    - local_transitions (equivalent of load_transitions)
    - topic_transitions (equivalent of load_global_nlu)
    - global_transitions (equivalent of load_global_nlu but the update rule entries are added to all components)
"""

from emora_stdm.state_transition_dialogue_manager.macro import Macro

import itertools
from copy import deepcopy


def update_var_table(var_table, deepcopied_var_table, debugging=None):
    if debugging:
        print(debugging)
    var_table.clear()
    var_table.update(deepcopied_var_table)
    return var_table


def set_system_stack_state(df, transition_options):
    local_sys_trans = lambda df, s: (
      df.has_state(s) and
      list(df.transitions(s, speaker=df.Speaker.SYSTEM))
    )
    jump_back_point = None
    for source, target, speaker in list(
        df.transitions(df.state(), speaker=df.speaker())
    ):
        if '#RPT' in df.transition_natex(source, target, speaker).expression():
            jump_back_point = {target: df.vars()}
    error_successor = df.error_successor(df.state())
    error_transition = {error_successor: df.vars()} if error_successor else {}
    if transition_options:
        scores, natexes, transitions, varss, four, five = zip(*sorted(
            transition_options, reverse=True, key=lambda x: x[0]
        ))
        sources, targets, speakers = zip(*transitions)
        sorted_options = dict(zip(targets, varss))
        varss = list(varss)
    else:
        sorted_options = {}
        varss = []
    if jump_back_point:
        candidate_returns = jump_back_point
    else:
        candidate_returns = {**sorted_options, **error_transition}
    varss.append(df._vars)
    jump_back_state = None
    for successor_state, var_table in candidate_returns.items():
        if isinstance(successor_state, tuple) and df.composite_dialogue_flow():
            cdf = df.composite_dialogue_flow()
            component, state = successor_state
            if (
              component in cdf._components
              and local_sys_trans(cdf.component(component), state)
            ):
                jump_back_state = successor_state
                break
        if local_sys_trans(df, successor_state):
            if df.namespace() and isinstance(successor_state, str) and ':' not in successor_state:
                successor_state = (df.namespace(), successor_state)
            jump_back_state = successor_state
            break
    if jump_back_state is not None:
        for v in varss:
            v.update(dict(__stack_return = jump_back_state))


def macro_parse_args(args, expected=None):
    if expected is None:
        expected = tuple(range(len(args)))
    kwargs = {}
    for kw, arg in itertools.zip_longest(expected, args, fillvalue=None):
        if isinstance(arg, str) and '=' in arg:
            kw, arg = arg.split('=')
        kwargs[kw] = arg
    return kwargs


class JMP(Macro):

    def __init__(self, df):
        self.df = df

    def run(self, ngrams, vars, args):
        arguments = macro_parse_args(args, ('phrase', 'return', 'doom'))
        def on_transition_fn(vars):
            jump_return = arguments['return'] or vars.get('__stack_return')
            return_phrase = arguments.get('return')
            return_phrase = (
              return_phrase if return_phrase is not None else
              vars.get('__stack_phrase', '')
            )
            doom = arguments.get('doom')
            doom = vars.get('__stack_doom', -1) if doom is None else doom
            if jump_return:
                vars.setdefault('__stack', []).append({
                  'phrase': return_phrase,
                  'return': jump_return,
                  'doom': int(doom)
                })
        vars['__on_transition__'] = on_transition_fn
        return True


class RET(Macro):
    def run(self, ngrams, vars, args):
        stack = vars.get('__stack', [])
        if stack:
            return_phrase, return_state, doom = stack.pop().values()
            vars['__target__'] = return_state
            return return_phrase


class RPT(Macro):
    def run(self, ngrams, vars, args):
        return False


class MANAGE_STACK(Macro):

    def __init__(self, max_stack_len=10):
        self.max_stack_len = max_stack_len

    def run(self, ngrams, vars, args):
        stack = vars.get('__stack', [])
        for entry in list(stack):
            entry['doom'] -= 1
            if entry['doom'] == 0:
                stack.remove(entry)
        if len(stack) > self.max_stack_len:
            items = stack[-self.max_stack_len:]
            stack.clear()
            stack.extend(items)

