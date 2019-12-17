
from structpy.graph.traversal.traversal import Traversal
from structpy.graph.traversal.frontier import Queue, Stack
from structpy.graph.traversal.rings import rings
from structpy.language.simple import each

def BreadthFirst(graph, start):
    return Traversal(graph, Queue()).memoried().start(start)

def BreadthFirstArcs(graph, start):
    return Traversal(graph, Queue()).arcs().memoried().start(start)

def BreadthFirstLabeledArcs(graph, start):
    return Traversal(graph, Queue()).labeled_arcs().memoried().start(start)

def BreadthFirstBounded(graph, start, depth):
    return Traversal(graph, Queue()).memoried().to_depth(depth).start(start)

def BreadthFirstBoundedArcs(graph, start, depth):
    return Traversal(graph, Queue()).arcs().memoried().to_depth(depth).start(start)

def BreadthFirstReverse(graph, start):
    return Traversal(graph, Queue()).memoried().with_sfn(lambda g, n: g.sources(n)).start(start)

def BreadthFirstOnArcs(graph, start, *arc_labels):
    def successors(g, n):
        return set(each(*[g.targets(n, l) for l in arc_labels if g.has_arc_label(n, l)]))
    return Traversal(graph, Queue()).memoried().with_sfn(successors).start(start)

def BreadthFirstOnArcsReverse(graph, start, *arc_labels):
    def successors(g, n):
        return set(each(*[g.sources(n, l) for l in arc_labels if g.has_in_arc_label(n, l)]))
    return Traversal(graph, Queue()).memoried().with_sfn(successors).start(start)

def Ring(graph, start, depth=None):
    if depth is None:
        return rings(Traversal(graph, Queue()).memoried().with_depth().start(start))
    else:
        return rings(Traversal(graph, Queue()).memoried().with_depth(depth).start(start))

def RingArcs(graph, start, depth=None):
    if depth is None:
        return rings(Traversal(graph, Queue()).arcs().memoried().with_depth().start(start))
    else:
        return rings(Traversal(graph, Queue()).arcs().memoried().with_depth(depth).start(start))

def RingLabeledArcs(graph, start, depth=None):
    if depth is None:
        return rings(Traversal(graph, Queue()).labeled_arcs().memoried().with_depth().start(start))
    else:
        return rings(Traversal(graph, Queue()).labeled_arcs().memoried().with_depth(depth).start(start))

def RingWander(graph, start, depth=None):
    if depth is None:
        return rings(Traversal(graph, Queue()).with_depth().start(start))
    else:
        return rings(Traversal(graph, Queue()).with_depth(depth).start(start))

def RingArcsWander(graph, start, depth=None):
    if depth is None:
        return rings(Traversal(graph, Queue()).arcs().with_depth().start(start))
    else:
        return rings(Traversal(graph, Queue()).arcs().with_depth(depth).start(start))

def RingLabeledArcsWander(graph, start, depth=None):
    if depth is None:
        return rings(Traversal(graph, Queue()).labeled_arcs().with_depth().start(start))
    else:
        return rings(Traversal(graph, Queue()).labeled_arcs().with_depth(depth).start(start))


