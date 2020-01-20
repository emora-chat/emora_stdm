
import regex


class Interpretation:

    def __init__(self, dialogue_flow, natex_string):
        self._dialogue_flow = dialogue_flow
        self._variable_assignments = self._parse_variable_assignments(natex_string)
        self._variable_references = self._parse_variable_references(natex_string) - self._variable_assignments
        self._variable_local_references = self._variable_assignments & self._variable_references
        self._knowledge_queries = self._parse_knowledge_queries(natex_string)

    def evaluate_user_transition(self, utterance):
        phrases = self._all_ngrams(utterance, 10)
        for ref in self._variable_references:
            pass
        for o in self._ontology_queries:
            results = self._dialogue_flow.knowledge_base().subtypes(o, filter=phrases)
        for var, query in self._knowledge_queries.items():
            results = self._dialogue_flow.knowledge_base().query(query, filter=phrases)

    def _parse_variable_references(self, natex_string):
        return {x for x in regex.findall(r'\$[a-zA-Z0-9_.]+', natex_string)}

    def _parse_variable_assignments(self, natex_string):
        return {'$'+x[1:] for x in regex.findall(r'\%[a-zA-Z0-9_.]+', natex_string)}

    def _parse_knowledge_queries(self, natex_string):
        queries = {}
        n = 0
        for x in regex.findall(r'#[^#]*#', natex_string):
            queries['$_KB_'+str(n)] = x[1:-1]
            n += 1
        return queries