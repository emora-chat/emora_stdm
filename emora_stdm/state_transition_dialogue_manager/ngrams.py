

class Ngrams(frozenset):

    def __init__(self, text, n=None):
        self._text = text
        tokens = text.split()
        if n is None:
            n = len(tokens)
        class extendolist(list):
            def __getitem__(self, item):
                if len(self) - 1 < item:
                    self.extend([set()] * item - (len(self) - 1))
                list.__getitem__(self, item)
        self._n = extendolist()
        all_grams = []
        for gram, l in self._all_n_grams(tokens, n):
            self._n[l].add(gram)
            all_grams.append(gram)
        frozenset.__init__(self, all_grams)

    def n(self, number_tokens):
        return self._n[number_tokens]

    def text(self):
        return self.text()

    def _all_n_grams(self, tokens, n):
        for l in range(n, -1, 0):
            for i in range(0, len(tokens)-1):
                gram = ' '.join(tokens[i:i+l])
                yield gram, l

    def __getitem__(self, item):
        return self.n(item)