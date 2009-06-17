#!/usr/bin/env python
# -*- coding: utf-8 -*-

__doc__ = """
A boolean language syntax to querying library.
"""
__author__ = "Mathieu Lecarme <mathieu@garambrogne.net>"

from pyparsing import *

__all__ = ['Query', 'value']

def defaultParser():
	# simple tokens
	simple = Word(alphanums)
	quoted = dblQuotedString.setParseAction(removeQuotes)
	single = (simple | quoted).setResultsName('value')
	word = Group(Word(alphas).setResultsName('field') + Suppress(":") + single).setResultsName('word')

	expression = Forward()
	unit = Forward()

	# Parentheses can enclose (group) any expression
	parenthetical = Group((Suppress("(") + expression + Suppress(")"))).setResultsName('group')

	operatorAnd = Group(Suppress(CaselessLiteral("and")) + expression).setResultsName('and')
	operatorOr = Group(Suppress(CaselessLiteral("or")) + expression).setResultsName('or')
	operatorXor = Group(Suppress(CaselessLiteral("xor")) + expression).setResultsName('xor')

	operator = ( operatorAnd | operatorOr | operatorXor )

	operatorNot = Group(Suppress(CaselessLiteral("not")) + unit ).setResultsName('not')

	unit << (word | parenthetical | operatorNot)

	expression << (unit  + ZeroOrMore(operator))
	#query = OneOrMore(terms)# + StringEnd()
	return Group(expression).setResultsName("query") + StringEnd()

_defaultParser = defaultParser()
def Query(query):
	global _defaultParser
	return _defaultParser.parseString(query)[0]

def value(nodes, library):
	#print 'name', nodes.getName()
	if nodes.getName() in ['query','group']:
		_value = value(nodes[0], library)
		for node in nodes[1:]:
			#print '\t', node.getName(), node[0].getName()
			if node.getName() == 'or':
				_value |= value(node[0], library)
			if node.getName() == 'and':
				_value &= value(node[0], library)
			if node.getName() == 'xor':
				_value ^= value(node[0], library)
		return _value
	if 'word' == nodes.getName():
		return library.get(nodes.field, nodes.value)
	if 'not' == nodes.getName():
		return - value(nodes[0], library)
