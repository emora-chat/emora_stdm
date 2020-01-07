
import random

def random_choice(choices):
    transitions = list(choices.keys())
    total = sum(choices.values())
    thresholds = []
    curr = 0
    for t in transitions:
        prob = choices[t] / total
        curr += prob
        thresholds.append(curr)
    r = random.uniform(0, 1.0)
    for i, threshold in enumerate(thresholds):
        if r < threshold:
            return transitions[i]
    return transitions[-1]