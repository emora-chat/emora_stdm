from emora_stdm import NatexNLU, ONTE, ONT_NEG, KnowledgeBase


kb = KnowledgeBase()
kb.load_json_file("opening_database.json")


female_name_nlu = '{' \
                  '[$username=#ONT(ont_female_names)], ' \
                  '[! #ONT_NEG(ont_female_names,ont_male_names), [name, is, $username=alexa]],' \
                  '[! my, name, is, alexa],' \
                  '[! you, {can,may,should}, call, me, alexa]' \
                  '}'

nlu = NatexNLU(female_name_nlu, macros={"ONT": ONTE(kb), "ONT_NEG": ONT_NEG(kb)})

var_dict = {}
assert nlu.match("my name is alexa", vars=var_dict)
assert var_dict["username"] == "alexa"

var_dict = {}
assert nlu.match("my name is sarah", vars=var_dict)
assert var_dict["username"] == "sarah"

var_dict = {}
assert nlu.match("alexa my name is sarah", vars=var_dict)
assert var_dict["username"] == "sarah"

var_dict = {}
assert not nlu.match("alexa stop", vars=var_dict)
assert "username" not in var_dict

var_dict = {}
assert not nlu.match("alexa why are you do dumb at names", vars=var_dict)
assert "username" not in var_dict

var_dict = {}
assert nlu.match("hannah", vars=var_dict)
assert var_dict["username"] == "hannah"

for i in range(100):
    var_dict = {}
    assert nlu.match("alexa hannah", vars=var_dict)
    assert var_dict["username"] == "hannah"






