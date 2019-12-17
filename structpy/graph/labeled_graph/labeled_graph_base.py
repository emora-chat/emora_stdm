import json
from structpy.graph.element import Node, Arc


class LabeledGraphBase:

    def node(self, node_value):
        """

        """
        return Node(self, node_value)

    def arc(self, source, target, label=None):
        """

        """
        return Arc(self, source, target, label)


    def _serialize(self, node_transform_function=None, label_transform_function=None, indent=0):
        arcs = []
        for s, t, l in self.arcs():
            if node_transform_function is not None:
                s = node_transform_function(s)
                t = node_transform_function(t)
            if label_transform_function is not None:
                l = label_transform_function(l)
            if hasattr(s, 'serialize'):
                s = s.serialize()
            if hasattr(t, 'serialize'):
                t = t.serialize()
            if hasattr(l, 'serialize'):
                l = l.serialize()
            arcs.append((s, t, l))
        return json.dumps(arcs, indent=indent)

    def serialize(self, node_transform_function=None, label_transform_function=None):
        """

        """
        return self._serialize(node_transform_function, label_transform_function)


    def display(self, node_transform_function=None, label_transform_function=None):
        """

        """
        return self._serialize(node_transform_function, label_transform_function, indent=4)

    def deserialize(self, json_string, node_transform_function=None, label_transform_function=None):
        """

        """
        arcs = json.loads(json_string)
        if node_transform_function or label_transform_function:
            for i in range(len(arcs)):
                s, t, l = arcs[i]
                if node_transform_function is not None:
                    s = node_transform_function(s)
                    t = node_transform_function(t)
                if label_transform_function is not None:
                    l = label_transform_function(l)
                arcs[i] = (s, t, l)
        for arc in arcs:
            self.add(*arc)