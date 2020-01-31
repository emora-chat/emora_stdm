from emora_stdm import NatexNLU, ONT, ONT_NEG, KnowledgeBase
import nltk


kb = KnowledgeBase()
kb.load_json_file("opening_database.json")

receive_how_are_you = "{" \
                      "[how are you]," \
                      "[how you doing]," \
                      "[what about you]," \
                      "[whats up with you]," \
                      "[how you are]," \
                      "[how about you]" \
                      "}"

feelings_pos_and_not_received_how_are_you = "{" \
                                            "[!-#ONT_NEG(ont_negation), -%s, [#ONT(ont_feelings_positive)]]," \
                                            "[! -%s, [#ONT(ont_negation)], [#ONT(ont_feelings_negative)]]," \
                                            "#IsPositiveSentiment" \
                                            "}"%(receive_how_are_you,receive_how_are_you)


nlu = NatexNLU(feelings_pos_and_not_received_how_are_you, macros={"ONT": ONT(kb), "ONT_NEG": ONT_NEG(kb)})
print("POS NO HOW ARE YOU")
print()
print("MATCH:")

m = nlu.match("im not too bad", debugging=False)
print()
print(m)
print()

m = nlu.match("great i guess", debugging=False)
print()
print(m)
print()

m = nlu.match("great", debugging=False)
print()
print(m)
print()

m = nlu.match("i seem to be pretty great thanks", debugging=False)
print()
print(m)
print()

m = nlu.match("not bad", debugging=False)
print()
print(m)
print()

m = nlu.match("thanks im not bad dude", debugging=False)
print()
print(m)
print()

print("NO MATCH:")

m = nlu.match("well how are you", debugging=False)
print()
print(m)
print()

m = nlu.match("pretty well how are you", debugging=False)
print()
print(m)
print()

m = nlu.match("not well how are you", debugging=False)
print()
print(m)
print()

m = nlu.match("how are you im not well", debugging=False)
print()
print(m)
print()


m = nlu.match("im bad", debugging=False)
print()
print(m)
print()


m = nlu.match("bad", debugging=False)
print()
print(m)
print()

m = nlu.match("im doing ok", debugging=False)
print()
print(m)
print()

feelings_neg_and_not_received_how_are_you = "{" \
                                            "[!-#ONT_NEG(ont_negation), -%s, [#ONT(ont_feelings_negative)]]," \
                                            "[! -%s, [#ONT(ont_negation)], [{#ONT(ont_feelings_positive),#ONT(ont_feelings_neutral)}]]," \
                                            "#IsNegativeSentiment" \
                                            "}"%(receive_how_are_you,receive_how_are_you)

nlu = NatexNLU(feelings_neg_and_not_received_how_are_you, macros={"ONT": ONT(kb), "ONT_NEG": ONT_NEG(kb)})
print("NEG NO HOW ARE YOU")
print()
print("MATCH:")

m = nlu.match("bad i guess", debugging=False)
print()
print(m)
print()

m = nlu.match("bad", debugging=False)
print()
print(m)
print()

m = nlu.match("i seem to be pretty bad thanks", debugging=False)
print()
print(m)
print()

m = nlu.match("not good", debugging=False)
print()
print(m)
print()

m = nlu.match("thanks im not ok dude", debugging=False)
print()
print(m)
print()

print("NO MATCH:")

m = nlu.match("great i guess", debugging=False)
print()
print(m)
print()

m = nlu.match("great", debugging=False)
print()
print(m)
print()

m = nlu.match("i seem to be pretty great thanks", debugging=False)
print()
print(m)
print()

m = nlu.match("not bad", debugging=False)
print()
print(m)
print()

m = nlu.match("thanks im not bad dude", debugging=False)
print()
print(m)
print()

m = nlu.match("ok how are you", debugging=False)
print()
print(m)
print()

m = nlu.match("pretty well how are you", debugging=False)
print()
print(m)
print()

m = nlu.match("not well how are you", debugging=False)
print()
print(m)
print()

m = nlu.match("how are you im not well", debugging=False)
print()
print(m)
print()

feelings_neutral_and_not_received_how_are_you = "[!-#ONT_NEG(ont_negation), -%s, [#ONT(ont_feelings_neutral)]]"%(receive_how_are_you)
nlu = NatexNLU(feelings_neutral_and_not_received_how_are_you, macros={"ONT": ONT(kb), "ONT_NEG": ONT_NEG(kb)})
print("NEUTRAL NO HOW ARE YOU")
print()

print("MATCH:")

m = nlu.match("ok i guess", debugging=False)
print()
print(m)
print()

m = nlu.match("ok", debugging=False)
print()
print(m)
print()

m = nlu.match("i seem to be ok thanks", debugging=False)
print()
print(m)
print()

print("NO MATCH:")

m = nlu.match("great i guess", debugging=False)
print()
print(m)
print()

m = nlu.match("great", debugging=False)
print()
print(m)
print()

m = nlu.match("i seem to be pretty great thanks", debugging=False)
print()
print(m)
print()

m = nlu.match("not bad", debugging=False)
print()
print(m)
print()

m = nlu.match("thanks im not bad dude", debugging=False)
print()
print(m)
print()

m = nlu.match("ok how are you", debugging=False)
print()
print(m)
print()

m = nlu.match("pretty well how are you", debugging=False)
print()
print(m)
print()

m = nlu.match("not well how are you", debugging=False)
print()
print(m)
print()

m = nlu.match("how are you im not well", debugging=False)
print()
print(m)
print()

m = nlu.match("bad i guess", debugging=False)
print()
print(m)
print()

m = nlu.match("bad", debugging=False)
print()
print(m)
print()

m = nlu.match("i seem to be pretty bad thanks", debugging=False)
print()
print(m)
print()

m = nlu.match("not good", debugging=False)
print()
print(m)
print()

m = nlu.match("thanks im not ok dude", debugging=False)
print()
print(m)
print()

feelings_pos_and_received_how_are_you = "{" \
                                        "[!-#ONT_NEG(ont_negation), [#ONT(ont_feelings_positive)], [%s]]," \
                                        "[#ONT(ont_negation), #ONT(ont_feelings_negative), %s]," \
                                        "<#IsPositiveSentiment, %s>" \
                                        "}"%(receive_how_are_you,receive_how_are_you,receive_how_are_you)

nlu = NatexNLU(feelings_pos_and_received_how_are_you, macros={"ONT": ONT(kb), "ONT_NEG": ONT_NEG(kb)})
print("POS HOW ARE YOU")
print()

print("MATCH:")

m = nlu.match("pretty well how are you", debugging=False)
print()
print(m)
print()

m = nlu.match("great how are you", debugging=False)
print()
print(m)
print()

m = nlu.match("not too bad how are you", debugging=False)
print()
print(m)
print()

m = nlu.match("not bad how are you", debugging=False)
print()
print(m)
print()

print("NO MATCH:")

m = nlu.match("ok i guess", debugging=False)
print()
print(m)
print()

m = nlu.match("ok", debugging=False)
print()
print(m)
print()

m = nlu.match("i seem to be ok thanks", debugging=False)
print()
print(m)
print()

m = nlu.match("great i guess", debugging=False)
print()
print(m)
print()

m = nlu.match("great", debugging=False)
print()
print(m)
print()

m = nlu.match("i seem to be pretty great thanks", debugging=False)
print()
print(m)
print()

m = nlu.match("not bad", debugging=False)
print()
print(m)
print()

m = nlu.match("thanks im not bad dude", debugging=False)
print()
print(m)
print()

m = nlu.match("ok how are you", debugging=False)
print()
print(m)
print()

m = nlu.match("not well how are you", debugging=False)
print()
print(m)
print()

m = nlu.match("how are you im not well", debugging=False)
print()
print(m)
print()

m = nlu.match("bad i guess", debugging=False)
print()
print(m)
print()

m = nlu.match("bad", debugging=False)
print()
print(m)
print()

m = nlu.match("i seem to be pretty bad thanks", debugging=False)
print()
print(m)
print()

m = nlu.match("not good", debugging=False)
print()
print(m)
print()

m = nlu.match("thanks im not ok dude", debugging=False)
print()
print(m)
print()

feelings_neg_and_received_how_are_you = "{" \
                                        "[!-#ONT_NEG(ont_negation), [#ONT(ont_feelings_negative)], [%s]]," \
                                        "[#ONT(ont_negation), {#ONT(ont_feelings_positive),#ONT(ont_feelings_neutral)}, %s]," \
                                        "<#IsNegativeSentiment, %s>" \
                                        "}"%(receive_how_are_you,receive_how_are_you,receive_how_are_you)

nlu = NatexNLU(feelings_neg_and_received_how_are_you, macros={"ONT": ONT(kb), "ONT_NEG": ONT_NEG(kb)})
print("NEG HOW ARE YOU")
print()

print("MATCH:")


m = nlu.match("not well how are you", debugging=False)
print()
print(m)
print()

m = nlu.match("bad how are you", debugging=False)
print()
print(m)
print()

m = nlu.match("im bad how are you", debugging=False)
print()
print(m)
print()

print("NO MATCH:")

m = nlu.match("ok i guess", debugging=False)
print()
print(m)
print()

m = nlu.match("ok", debugging=False)
print()
print(m)
print()

m = nlu.match("i seem to be ok thanks", debugging=False)
print()
print(m)
print()

m = nlu.match("great i guess", debugging=False)
print()
print(m)
print()

m = nlu.match("great", debugging=False)
print()
print(m)
print()

m = nlu.match("i seem to be pretty great thanks", debugging=False)
print()
print(m)
print()

m = nlu.match("not bad", debugging=False)
print()
print(m)
print()

m = nlu.match("thanks im not bad dude", debugging=False)
print()
print(m)
print()

m = nlu.match("ok how are you", debugging=False)
print()
print(m)
print()

m = nlu.match("bad i guess", debugging=False)
print()
print(m)
print()

m = nlu.match("bad", debugging=False)
print()
print(m)
print()

m = nlu.match("i seem to be pretty bad thanks", debugging=False)
print()
print(m)
print()

m = nlu.match("not good", debugging=False)
print()
print(m)
print()

m = nlu.match("thanks im not ok dude", debugging=False)
print()
print(m)
print()

m = nlu.match("pretty well how are you", debugging=False)
print()
print(m)
print()

m = nlu.match("great how are you", debugging=False)
print()
print(m)
print()

feelings_neutral_and_received_how_are_you = "[!-#ONT_NEG(ont_negation), [#ONT(ont_feelings_neutral)], [%s]]"%(receive_how_are_you)
nlu = NatexNLU(feelings_neutral_and_received_how_are_you, macros={"ONT": ONT(kb), "ONT_NEG": ONT_NEG(kb)})
print("NEUTRAL HOW ARE YOU")
print()

print("MATCH:")


m = nlu.match("ok but how are you", debugging=False)
print()
print(m)
print()

print("NO MATCH:")

m = nlu.match("not ok how are you", debugging=False)
print()
print(m)
print()

m = nlu.match("im not ok how are you", debugging=False)
print()
print(m)
print()

m = nlu.match("not well how are you", debugging=False)
print()
print(m)
print()

m = nlu.match("bad how are you", debugging=False)
print()
print(m)
print()

m = nlu.match("im bad how are you", debugging=False)
print()
print(m)
print()

m = nlu.match("ok i guess", debugging=False)
print()
print(m)
print()

m = nlu.match("ok", debugging=False)
print()
print(m)
print()

m = nlu.match("i seem to be ok thanks", debugging=False)
print()
print(m)
print()

m = nlu.match("great i guess", debugging=False)
print()
print(m)
print()

m = nlu.match("great", debugging=False)
print()
print(m)
print()

m = nlu.match("i seem to be pretty great thanks", debugging=False)
print()
print(m)
print()

m = nlu.match("not bad", debugging=False)
print()
print(m)
print()

m = nlu.match("thanks im not bad dude", debugging=False)
print()
print(m)
print()

m = nlu.match("bad i guess", debugging=False)
print()
print(m)
print()

m = nlu.match("bad", debugging=False)
print()
print(m)
print()

m = nlu.match("i seem to be pretty bad thanks", debugging=False)
print()
print(m)
print()

m = nlu.match("not good", debugging=False)
print()
print(m)
print()

m = nlu.match("thanks im not ok dude", debugging=False)
print()
print(m)
print()

m = nlu.match("pretty well how are you", debugging=False)
print()
print(m)
print()

m = nlu.match("great how are you", debugging=False)
print()
print(m)
print()


decline_share = "{"\
                "[#ONT(ont_negation), {talk, talking, discuss, discussing, share, sharing, tell, telling, say, saying}],"\
                "[#ONT(ont_fillers), #ONT(ont_negative)],"\
                "[#ONT(ont_negative)]"\
                "<{dont,do not}, know>,"\
                "<not, sure>"\
                "}"

nlu = NatexNLU(decline_share, macros={"ONT": ONT(kb), "ONT_NEG": ONT_NEG(kb)})
print("DECLINE SHARE")
print()

print("MATCH:")

m = nlu.match("i dont know", debugging=False)
print()
print(m)
print()

m = nlu.match("im not sure", debugging=False)
print()
print(m)
print()

m = nlu.match("i dont want to tell you", debugging=False)
print()
print(m)
print()

m = nlu.match("no", debugging=False)
print()
print(m)
print()

m = nlu.match("i dont want to talk about it", debugging=False)
print()
print(m)
print()


print("NO MATCH:")

m = nlu.match("ok but how are you", debugging=False)
print()
print(m)
print()

m = nlu.match("not ok how are you", debugging=False)
print()
print(m)
print()

m = nlu.match("im not ok how are you", debugging=False)
print()
print(m)
print()

m = nlu.match("not well how are you", debugging=False)
print()
print(m)
print()

m = nlu.match("bad how are you", debugging=False)
print()
print(m)
print()

m = nlu.match("im bad how are you", debugging=False)
print()
print(m)
print()

m = nlu.match("ok i guess", debugging=False)
print()
print(m)
print()

m = nlu.match("ok", debugging=False)
print()
print(m)
print()

m = nlu.match("i seem to be ok thanks", debugging=False)
print()
print(m)
print()

m = nlu.match("great i guess", debugging=False)
print()
print(m)
print()

m = nlu.match("great", debugging=False)
print()
print(m)
print()

m = nlu.match("i seem to be pretty great thanks", debugging=False)
print()
print(m)
print()

m = nlu.match("not bad", debugging=False)
print()
print(m)
print()

m = nlu.match("thanks im not bad dude", debugging=False)
print()
print(m)
print()

m = nlu.match("bad i guess", debugging=False)
print()
print(m)
print()

m = nlu.match("bad", debugging=False)
print()
print(m)
print()

m = nlu.match("i seem to be pretty bad thanks", debugging=False)
print()
print(m)
print()

m = nlu.match("not good", debugging=False)
print()
print(m)
print()

m = nlu.match("thanks im not ok dude", debugging=False)
print()
print(m)
print()

m = nlu.match("pretty well how are you", debugging=False)
print()
print(m)
print()

m = nlu.match("great how are you", debugging=False)
print()
print(m)
print()