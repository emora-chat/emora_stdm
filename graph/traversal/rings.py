

class rings:

    def __init__(self, traversal, max_depth=None):
        self.traversal = traversal
        self.depth = -1
        self.max_depth = max_depth
        self.item_buffer, self.depth_buffer = next(self.traversal)
        self.done = traversal.done()

    def get(self):
        if self.item_buffer is not None and self.depth_buffer == self.depth:
            result = self.item_buffer
            try:
                self.item_buffer, self.depth_buffer = next(self.traversal)
            except StopIteration:
                self.item_buffer, self.depth_buffer = None, None
                self.done = True
            return result
        else:
            return None

    def __iter__(self):
        return self

    def __next__(self):
        if self.done:
            raise StopIteration
        self.depth += 1
        return single_ring(self)


class single_ring:

    def __init__(self, ring_traversal):
        self.traversal = ring_traversal

    def __iter__(self):
        return self

    def __next__(self):
        n = self.traversal.get()
        if n is None:
            raise StopIteration
        return n

