
import random

def random_choice(choices):
    if len(choices) > 0:
        transitions = list(choices.keys())
        total = sum(choices.values())
        if total > 0:
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
        else:
            return None
    else:
        raise Exception("No valid system transition is found.")

def all_grams(s):
    tokens = [token for token in s.split() if token != ""]
    all_grams = set()
    for n in range(len(tokens)+1):
        ngrams = zip(*[tokens[i:] for i in range(n)])
        all_grams.update(set([" ".join(ngram) for ngram in ngrams]))
    return all_grams