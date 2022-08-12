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


def set_system_stack_state(df, transition_options):
    local_sys_trans = lambda df, s: (
      df.has_state(s) and
      list(df.transitions(s, speaker=df.Speaker.SYSTEM))
    )
    error_successor = df.error_successor(df.state())
    error_transition = [error_successor] if error_successor else []
    if transition_options:
        sorted_options = list(zip(*sorted(transition_options, reverse=True)))[2]
        sorted_options = list(list(zip(*sorted_options))[1])
    else:
        sorted_options = []
    for successor_state in sorted_options + error_transition:
        if isinstance(successor_state, tuple) and df.composite_dialogue_flow():
            cdf = df.composite_dialogue_flow()
            component, state = successor_state
            if (
              component in cdf._components
              and local_sys_trans(cdf.component(component), state)
            ):
                df.update_vars(dict(__stack_return = successor_state))
                break
        if local_sys_trans(df, successor_state):
            df.update_vars(dict(__stack_return = successor_state))
            break
    else:
        df.update_vars(dict(__stack_return = None))


def macro_parse_args(args, expected=None):
    if expected is None:
        expected = tuple(range(len(args)))
    kwargs = {}
    for kw, arg in itertools.zip_longest(expected, args, fillvalue=None):
        if '=' in arg:
            kw, arg = arg.split('=')
        kwargs[kw] = arg
    return kwargs


class JMP(Macro):
    def run(self, ngrams, vars, args):
        args = macro_parse_args(args, ('phrase', 'return', 'doom'))
        jump_return = args['return'] or vars.get('__stack_return')
        return_phrase = args.get('return')
        return_phrase = (
          return_phrase if return_phrase is not None else
          vars.get('__stack_phrase', '')
        )
        doom = args.get('doom')
        doom = vars.get('__stack_doom', -1) if doom is None else doom
        if jump_return:
            vars['__stack'].append({
              'phrase': return_phrase,
              'return': jump_return,
              'doom': int(doom)
            })


class RET(Macro):
    def run(self, ngrams, vars, args):
        stack = vars.get('__stack', [])
        if stack:
            return_phrase, return_state, doom = stack.pop().values()
            vars['__target__'] = return_state
            return return_phrase


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

