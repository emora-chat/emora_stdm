
# Ontology

Using an ontology is an efficient way to distinguish different types of entities mentioned 
in a dialogue. This can save a lot of effort for systems with handcrafted interactions or logic.

Here is an example of an ontology, specified in json:
```
{
  "ontology": {
    "animal": ["mammal", "fish", "bird", "reptile", "amphibian"],
    "mammal": ["dog", "ape", "rat"],
    "reptile": ["snake", "lizard"],
    "amphibian": ["frog"],
    "dog": ["german shepard", "poodle"]
  },

  "expressions": {
    "dog": ["canine", "puppy"]
  }
}
```

There are two top-level entries in the root dictionary of this json object. 
`"ontology"` defines a dictionary that describes a directed acyclic graph (DAG) of the
ontology structure. 
Each entry in this dictionary takes the form `"type": ["subtype_1", "subtype_2", "..."]`,
where each value list element is a subtype of the node specified by the key.

The second top-level entry, `"expressions"`, is a table of alternative surface expressions
for each ontology node defined in `"ontology"`. 
In the above example, terms "canine" and "puppy" are two alternative linguistic expressions
that match the "dog" node.
By default, each node entry in "ontology" (whether specified as a key or in the value list)
will automatically be matched by it's own name, _unless the name contains an underscore_.

Here is a toy example of the above ontology being used in practice:

```python
df = DialogueFlow('start')
df.knowledge_base().load_json_file('ontology_example.json')
df.load_transitions({
    'state': 'start',

    '`What is your favorite animal?`': {

        '[#ONT(mammal)]': {

            '`I think mammals are cool too!`': 'start'
        },

        '[#ONT(reptile)]': {

            '`Reptiles are cool.`': 'start'
        },

        '[$animal=#ONT(animal)]': {
            'score': 0.5,

            '`I like` $animal `too.`': 'start'
        },

        'error': {

            '`I\'ve never heard of that animal.`': 'start'
        }
    }
})

df.run()
```

The above system can produce the following conversation:

```
S: What is your favorite animal?
U: The lizard.
S: Reptiles are cool. What is your favorite animal?
U: I like dogs.
S: I think mammals are cool too! What is your favorite animal?
U: Puppies are my favorite.
S: I think mammals are cool too! What is your favorite animal?
U: Birds.
S: I like birds too. What is your favorite animal?
```

Notice that the ontology macro will automatically run a lemmatizer to match input,
meaning that different forms of a word such as plurals or verb tenses will still
match the root form of their corresponding ontology entries. 