

class Ngrams(set):

    def __init__(self, text, n=5, raw_text=None):
        set.__init__(self)
        self._raw_text = raw_text or text
        self._text = text
        self._n = []
        self._string = ''
        self.update(text, n)

    def update(self, text, n=5):
        if '_END_' == text[-5:]:
            text = text[:-5]
        self._text = text
        self._string = ''.join([c.lower() for c in text if c.isalpha() or c == ' '])
        tokens = text.split()
        if n is None:
            n = len(tokens)
        self._n = [set() for _ in range(n + 1)]
        all_grams = []
        for gram, l in self._all_n_grams(tokens, n):
            self._n[l].add(gram)
            all_grams.append(gram)
        set.update(self, all_grams)

    def n(self, number_tokens):
        return self._n[number_tokens]

    def text(self):
        return self._text

    def raw_text(self):
        return self._raw_text

    def string(self):
        return self._string

    def _all_n_grams(self, tokens, n):
        for l in range(n, 0, -1):
            for i in range(0, len(tokens) - l + 1):
                gram = ' '.join(tokens[i:i+l])
                yield gram, l

    def __getitem__(self, item):
        return self.n(item)


if __name__ == '__main__':
    text = 'I like to eat sandwiches and drink coffee.'
    ngrams = Ngrams(text, 5)
    for ngram in sorted(ngrams, key=lambda x: len(x.split()), reverse=True):
        print(ngram)