

from structpy.graph.traversal.traversal_step import Step
from structpy.language import Mechanic, WrapperFunction


class Traversal:

    def __init__(self, graph, frontier):
        self.graph = graph
        self.frontier = frontier
        self.transforms = []
        self.successors = lambda g, node: g.targets(node)
        self.output = lambda step: step.node
        self._start = None

    def start(self, *initials):
        self._start = set(initials)
        initials = [Step(x) for x in initials]
        for transform in self.transforms:
            old_initials = set(initials)
            initials = set()
            for step in old_initials:
                for t_step in transform(self.graph, step):
                    initials.add(t_step)
        for initial in initials:
            self.frontier.add(initial)
        return self

    def expand(self, step):
        successors = {Step(x) for x in self.successors(self.graph, step.node)}
        for transform in self.transforms:
            old_successors = set(successors)
            successors = set()
            for successor in old_successors:
                for t_step in transform(self.graph, successor, step):
                    successors.add(t_step)
        for successor in successors:
            yield successor

    def done(self):
        return len(self.frontier) <= 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.done():
            raise StopIteration
        step = self.frontier.get()
        for next_step in self.expand(step):
            self.frontier.add(next_step)
        return self.output(step)

    #############################################################

    def arcs(self):
        def arcify(graph, step, prev=None):
            if prev is None:
                for target in self.successors(graph, step.node):
                    next_step = Step(target)
                    next_step.source = step.node
                    yield next_step
            else:
                step.source = prev.node
                yield step
        self.transforms.append(arcify)
        self.output = lambda step: (step.source, step.node)
        return self

    def labeled_arcs(self):
        def larcify(graph, step, prev=None):
            if prev is None:
                for target in self.successors(graph, step.node):
                    next_step = Step(target)
                    next_step.source = step.node
                    next_step.label = graph.label(next_step.source, next_step.node)
                    yield next_step
            else:
                step.source = prev.node
                step.label = graph.label(step.source, step.node)
                yield step
        self.transforms.append(larcify)
        self.output = lambda step: (step.source, step.node, step.label)
        return self

    def memoried(self):
        @Mechanic(visited=set())
        def remember(this, graph, step, prev=None):
            if prev is None:
                this.visited.update(self._start)
                this.visited.add(step.node)
                yield step
            elif step.node not in this.visited:
                this.visited.add(step.node)
                yield step
        self.transforms.append(remember)
        return self

    def with_sfn(self, successor_function):
        self.successors = successor_function
        return self

    def to_depth(self, max_depth):
        def add_depth(graph, step, prev=None):
            if prev is None:
                step.depth = 0
            else:
                step.depth = prev.depth + 1
            if step.depth <= max_depth:
                yield step
        self.transforms.append(add_depth)
        return self

    def with_depth(self, max_depth=None):
        def add_depth(graph, step, prev=None):
            if prev is None:
                step.depth = 0
            else:
                step.depth = prev.depth + 1
            if max_depth is None or step.depth <= max_depth:
                yield step
        self.transforms.append(add_depth)
        @WrapperFunction(self.output)
        def output(result, step):
            return result, step.depth
        self.output = output
        return self

