def each(*generators, key=None):
    if key is None:
        for generator in generators:
            for item in generator:
                yield item
    else:
        for generator in generators:
            for item in key(generator):
                yield item

def rfind(indexable, item):
    """
    Iterates through the collection in reverse order and returns the index of
    an item
    """
    length = len(indexable)
    for i in range(length - 1, -1, -1):
        if indexable[i] == item:
            return i
    return - 1

def empty_generator():
        return
        yield

def both(generator_one, generator_two):
    yield from generator_one
    yield from generator_two

def element_at(iterable, index):
    i = 0
    for e in iterable:
        if i == index:
            return e
        i += 1

def every_pair(iterable):
    ls = list(iterable)
    for i in range(len(ls) - 1):
        for j in range(i + 1, len(ls)):
            yield ls[i], ls[j]


def single(iterable_with_single_item):
    (item,) = iterable_with_single_item
    return item