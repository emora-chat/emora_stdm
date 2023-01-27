# import json
import pytest
from emora_stdm.state_transition_dialogue_manager.natex_nlu import NatexNLU
# from emora_stdm.state_transition_dialogue_manager.knowledge_base import KnowledgeBase
# from emora_stdm.state_transition_dialogue_manager.dialogue_flow import DialogueFlow, Speaker
# from emora_stdm.state_transition_dialogue_manager.macros_common import ONTE, ONT_NEG
# from enum import Enum


def test_flexible_sequence_base():
    natex = NatexNLU('[CS, courses, are, fun]')  # need to use everything in order

    assert natex.match('CS courses are fun')
    assert natex.match(' CS courses are fun')  # allows leading spaces
    assert not natex.match('CS courses are fun' + ' ')  # not trailing spaces

    assert not natex.match('are CS courses fun or not')  # order of natex matters
    assert not natex.match('cs 253 is not fun')
    assert not natex.match('CS courses are fun.')  # symbols not allowed

def test_flexible_sequence_edge():
    natex = NatexNLU('[CS, courses, are, fun]')  # need to use everything in order
    assert natex.match('CS.courses.are.fun')  # is this expected? # flag
    assert natex.match('CS.courses are.fun.fun')
    assert not natex.match('CS.courses.are.fun.fun.')
    assert natex.match('The CS courses at emory are not fun' + '  ' + 'but it is essential')
    assert natex.match('CS courses at emory are not fun' + '\t' + 'but it is essential')  # tab matches
    assert not natex.match('CS courses at emory are not fun' + '\n' + 'but it is essential')  # new line does not

# get rid of brackets [ ]
def test_rigid_sequence_base():
    natex = NatexNLU('[!CS, courses, are, hard]')

    assert natex.match('CS courses are hard')
    assert not natex.match('CS courses are hard but fun')
    assert not natex.match('CS courses are not hard')

    assert not natex.match(' ' + 'CS courses are hard')
    assert not natex.match('CS courses are hard' + ' ')
    assert not natex.match('CS courses are hard' + ' ')
    assert not natex.match('!CS course are hard')
    assert not natex.match('CS course are not hard')

def test_rigid_sequence_edge():
    natex = NatexNLU('[!CS, courses, are, hard]')
    assert natex.match('CS!courses!are!hard')  # is this normal?
    assert not natex.match('CS!courses!are!hard!')
    assert natex.match('CS courses' + '  ' + 'are hard')
    assert natex.match('CS courses' + '\t' + 'are hard')
    assert natex.match('CS courses' + '\n' + 'are hard')
    # new line in the middle allowed, but not allowed in flexible sequence


# disjunction is a set {} that matches whether
# the input string is one of the values in the set

def test_disjunction_base():
    natex = NatexNLU('{I enjoy coding, coding, fun, cs}')
    assert natex.match('I enjoy coding')
    assert not natex.match('I enjoy coding' + ' ')

    assert natex.match('coding')
    assert natex.match('fun')
    assert not natex.match('Cs')

def test_disjunction_edge():
    natex = NatexNLU('{I enjoy coding, coding, fun, cs}')
    assert not natex.match('I!enjoy!coding')
    assert not natex.match('I enjoy' + '  ' + 'coding')
    assert not natex.match('I enjoy' + '\t' + 'coding')
    assert not natex.match('I enjoy' + '\n' + 'coding')
    assert not natex.match('\t' + 'cs')
    assert not natex.match('cs' + '\t')


# conjunction is enclosed in <>
def test_conjunction_base():
    natex = NatexNLU('<CS, courses, are, hard>')
    assert natex.match('CS courses are hard')
    assert natex.match('CS courses are hard' + ' ')
    assert natex.match('CS courses are hard' + '.')

    assert natex.match('hard they are, courses of CS')  # order doesn't matter

    assert not natex.match('MATH courses are hard')  # generic fail case

def test_conjunction_edge():
    natex = NatexNLU('<CS, courses, are, hard>')
    assert natex.match('CS courses !are hard')
    assert natex.match('!CS,courses,are,hard.123')
    assert not natex.match('!CS,courses,are,hard123')

    assert natex.match('"CS"courses"are"hard"')
    assert natex.match('"CS"" ""courses"" ""are"" ""hard"')

    assert natex.match('CS courses' + '  ' + 'are hard')
    assert natex.match('CS courses' + '\t' + 'are hard')
    assert not natex.match('CS courses' + '\n' + 'are hard')  # new line doesn't


def test_optional_base():
    natex1 = NatexNLU('[!CS, is, not?, fun]')
    assert natex1.match('CS is fun')
    assert natex1.match('CS is not fun')
    assert not natex1.match('CS is fun fun')  # doesn't work when its repeated
    assert not natex1.match('CS is not fun' + ' ')

    natex2 = NatexNLU('[!CS, is, not? fun]')
    assert not natex2.match('CS is')
    assert natex2.match('CS is fun')
    assert not natex2.match('CS is very fun')

    assert natex2.match('CS is not fun')
    assert not natex2.match('CS is fun fun')  # doesn't work when its repeated

def test_optional_edge(): # optional take out
    natex1 = NatexNLU('[!CS, is, not?, fun]')
    assert natex1.match('CS is' + '  ' + 'fun')
    assert natex1.match('CS is' + '\t' + 'fun')
    assert natex1.match('CS is' + '\n' + 'fun')  # works here

    natex2 = NatexNLU('[!CS, is, not? fun]')
    assert natex2.match('CS is' + '  ' + 'fun')
    assert natex2.match('CS is' + '\t' + 'fun')
    assert natex2.match('CS is' + '\n' + 'fun')  # works here

def test_kleene_star_base(): # kleene star out
    natex = NatexNLU('[!CS, is, really*, fun]')
    assert natex.match('CS is really fun')
    assert natex.match('CS is fun')
    assert not natex.match('CS is not fun')

    assert natex.match('CS is really really really fun')
    assert not natex.match('CS is reallyreallyreally fun')

    assert not natex.match('CS is really really really fun' + ' ')

    assert not natex.match('CS is really ' + 'very' + ' really fun')
    assert not natex.match('CS is really really not fun')

def test_kleene_star_edge():
    natex = NatexNLU('[!CS, is, really*, fun]')
    assert natex.match('CS.is.really.really.really.fun')  # symbols issue(?) continues
    assert not natex.match('CS.is.really.really.really.fun.')

    assert natex.match('CS is really' + '  ' + 'really' + '  ' + 'really fun')
    assert natex.match('CS is really' + '\t' + 'really' + '\t' + 'really fun')
    assert natex.match('CS is really' + '\n' + 'really' + '\n' + 'really fun')
    assert natex.match('CS is really' + '.' + 'really' + '.' + 'really fun')

    assert natex.match('CS is really ' + '!! ' + 'really ' + '!! ' + 'really fun')
# remove kleene plus
def test_kleene_plus_base():  # same results as kleene_star
    natex = NatexNLU('[!CS, is, really+, fun]')
    assert natex.match('CS is really fun')
    assert not natex.match('CS is fun')
    assert not natex.match('CS is not fun')
    assert not natex.match('CS is not really fun')
    assert natex.match('CS is really really really fun')
    assert not natex.match('CS is reallyreallyreally fun')
    assert not natex.match('CS is really really really fun' + ' ')
    assert not natex.match('CS is really ' + 'very' + ' really fun')
    assert not natex.match('CS is really really not fun')

def test_kleene_plus_edge():  # same results as kleene_star
    natex = NatexNLU('[!CS, is, really+, fun]')
    assert natex.match('CS.is.really.really.really.fun')
    assert not natex.match('CS.is.really.really.really.fun.')
    assert natex.match('CS is really' + '  ' + 'really' + '  ' + 'really fun')
    assert natex.match('CS is really' + '\t' + 'really' + '\t' + 'really fun')
    assert natex.match('CS is really' + '\n' + 'really' + '\n' + 'really fun')
    assert natex.match('CS is really' + '.' + 'really' + '.' + 'really fun')
    assert natex.match('CS is really ' + '!! ' + 'really ' + '!! ' + 'really fun')


def test_negation_base():
    natex1 = NatexNLU('[!-{math, econ}, like, cs]')
    assert natex1.match('I like cs')
    assert natex1.match('I like cs')
    assert not natex1.match('  ' + 'I like cs')
    assert natex1.match('I like' + ' ' + 'cs')

    natex2 = NatexNLU('[!I like, {cs, -math, -econ}]')  # negation needs to be first
    assert natex2.match('I like cs')
    assert natex2.match('I like math')  # this could match

    natex3 = NatexNLU('[!I like, <-math, -econ, cs>]')  # negation needs to be first
    assert not natex3.match('I like math')
    assert not natex3.match('I like econ')
    assert natex3.match('I like cs')

def test_negation_edge():
    natex1 = NatexNLU('[!-{math, econ}, like, cs]')
    assert not natex1.match('.' + 'I like cs')
    assert not natex1.match('I like cs' + ' ')
    assert not natex1.match('I like cs' + '.')
    assert natex1.match('I like' + '  ' + 'cs')
    assert natex1.match('I like' + '\t' + 'cs')
    assert natex1.match('I like' + '\n' + 'cs')

def test_regex_base():
    natex = NatexNLU('[!/[a-zA-Z]+/, like, cs, /[0-9]+/]')
    assert natex.match('I like cs 253')
    assert not natex.match('I like ! cs 171')  # should this work?!

    assert not natex.match('I like cs171')
    assert not natex.match('I like cs' + ' ')
    assert not natex.match('I like cs' + '.')
    assert not natex.match('I like cs 171!')

def test_regex_edge():
    natex = NatexNLU('[!/[a-zA-Z]+/, like, cs, /[0-9]+/]')
    assert natex.match('I like' + '\t' + 'cs 253')
    assert natex.match('I like' + '\n' + 'cs 370')
    assert natex.match('I like' + '  ' + 'cs 170')

def test_reference_base():
    v1 = {'A': 'cs', 'B': 'nlp', 'C': 'math'}
    natex1 = NatexNLU('[!my favorite subject is, {$A, $B, $C}]')

    assert natex1.match('my favorite subject is cs', vars=v1)
    assert natex1.match('my favorite'+' '+'subject is cs', vars=v1)

    assert natex1.match('my favorite subject is nlp', vars=v1)
    assert not natex1.match('my favorite subject is econ', vars=v1)

    natex2 = NatexNLU('[!{$A, $B, $C} is my favorite subject]')
    assert natex2.match('cs is my favorite subject', vars=v1)


def test_reference_edge():
    v1 = {'A': 'cs', 'B': 'nlp', 'C': 'math'}
    natex1 = NatexNLU('[!my favorite subject is, {$A, $B, $C}]')
    assert natex1.match('my favorite subject is'+'\t'+'cs', vars=v1)  # check flag
    assert natex1.match('my favorite subject is'+'\n'+'cs', vars=v1)  # check flag
    assert not natex1.match('my favorite subject is cs.', vars=v1)

    natex2 = NatexNLU('[!{$A, $B, $C} is my favorite subject]')
    assert natex2.match('cs'+'\t'+'is my favorite subject', vars=v1) # check flag
    assert natex2.match('cs'+'\n'+'is my favorite subject', vars=v1) # check flag

def test_assignment():
    v = {'A': 'cs'}
    natex = NatexNLU('[!i took, {a, an}, $A={econ, math} class today]')
    assert not natex.match('i took a cs class today', vars=v)
    assert natex.match('i took an econ class today', vars=v)
    assert v['A'] == 'econ'
    assert natex.match('i took a math class today', vars=v)
    assert v['A'] == 'math'

# fix
# commas
# build test cases for these
# and  raise compiler error for specific cases
# works
# -{x, y} standard way
# {-x, -y} not x or not y so weird
# -<x,y>
# <-x,-y>
# -[x,y]
# [-x, -y] compiler error when negation is directly inside flexible sequence
# -x works
# [x] -y negation has to be the first

# regex
def test_integration_flexible_negation_base():
    # pre appends .* (eats up everything) then checking negation (doesn't work)
    natex = NatexNLU('-cs, [is, very, fun]') # '-cs [is, very, fun]' is the CORRECT SYNTAX # pytest raises
    assert natex.match('math is very fun')
    assert natex.match('math is' + ' ' + 'very fun')
    assert natex.match(' ' + 'math is very fun')  # should work
    assert not natex.match('cs is very fun')
    # we want to have a compiler error specifically, when negation is used inside the sequence

def test_integration_flexible_negation_edge():
    natex = NatexNLU('-cs, [is, very, fun]')
    assert natex.match('math is' + '\n' + 'very fun')  # flag
    assert natex.match('math is' + '  ' + 'very fun')
    assert natex.match('math is' + '\t' + 'very fun')
    assert natex.match('math is' + '!' + 'very fun')  # should work
    assert not natex.match('math is very fun' + ' ')
    assert not natex.match('math is very fun' + '.')

# what this should be doing:
# ending with "fun" and "boring" should only match and everything else should fail.
def test_integration_rigid_sequence_negation_base():
    natex1 = NatexNLU('-cs, [!is, very, {fun, boring}]')
    assert natex1.match('math is very fun')
    assert natex1.match('math is very boring')
    assert not natex1.match('math is very exciting')
    assert natex1.match('math is'+' '+'very fun')

    natex2 = NatexNLU('[!-cs, -is, very, {fun, boring}]')
    assert natex2.match('courses are very fun')
    assert not natex2.match('math is very fun')  # matches is
    # may have to fix how negation is handled in rigid sequence,
    # by re-writing the natex string inside the compiler.

def test_integration_rigid_sequence_negation_edge():
    natex1 = NatexNLU('-cs, [!is, very, {fun, boring}]')
    assert natex1.match('math is'+'  '+'very boring')
    assert natex1.match('math is'+'\t'+'very fun')
    assert not natex1.match('math is'+'\n'+'very fun')  # new line flag
    assert not natex1.match('econ!is!very!fun')  # this works

    natex2 = NatexNLU('[!-cs, -is, very, {fun, boring}]')
    assert natex2.match('courses!are!very!fun')  # this works
    assert not natex2.match('math.is.very.fun')  # matches is
    assert not natex2.match('math ? very fun') # symbol is not being handled
    assert natex2.match('cs is very fun')  # does not match cs

# negation fix needed
# negation is eating up everything
def test_integration_disjunction_negation_base():
    natex1 = NatexNLU('{-cs, -nlp, fun}') # not cs and not nlp, and/or fun
    assert not natex1.match('cs')
    assert natex1.match('nothing')
    assert not natex1.match('nothing cs')
    assert natex1.match('nothing nlp')
    assert not natex1.match('c.cs')

    natex2 = NatexNLU('{-cs}')
    assert not natex2.match('cs'+'\t')
    assert not natex2.match('cs'+' ')
    assert not natex2.match('cs'+'  ')
    assert not natex2.match('c.cs')
    assert not natex2.match('math.')  # symbols still same result

    natex3 = NatexNLU('-{cs, nlp, econ}')
    assert not natex3.match('cs')
    assert not natex3.match('cs'+' ')
    assert not natex3.match('cs'+'  ')

    assert not natex3.match('nlp')
    assert not natex3.match('econ')
    assert natex3.match('good')
    assert natex3.match('good'+' ')
    assert natex3.match(' '+'good')
    assert not natex3.match('econ.nlp.cs')
    assert not natex3.match('how is cs?')
    assert not natex3.match('how fun is nlp?')
    assert natex3.match('how interesting is economics?')
    assert natex3.match('is math fun?')

def test_integration_conjunction_negation():
    natex1 = NatexNLU('<-math, food>')
    assert natex1.match('hello food')
    assert natex1.match(' food 123 ')
    assert natex1.match('cs food ')
    assert not natex1.match('food math')  # check whether math food works
    assert not natex1.match('math food')
    assert natex1.match('food')

    natex2 = NatexNLU('-<math, food>')  # NOT (both math AND food)
    assert natex2.match('hello')
    assert not natex2.match('food')
    assert not natex2.match('math')
    assert not natex2.match('math food')
    assert natex2.match('math drink')
    assert natex2.match('science drink')
    assert natex2.match('science food')
    assert natex2.match('science drink')
    assert natex2.match('science'+' '+'drink')
    assert natex2.match('science'+'\t'+'drink')
    assert not natex2.match('science'+'\n'+'drink')
