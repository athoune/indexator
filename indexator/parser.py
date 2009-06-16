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

if __name__ == '__main__':
	import unittest
	from document import Document, Library

	class QueryTest(unittest.TestCase):
		def setUp(self):
			self.library = Library('/tmp/parser.test', 'w')
			self.library.append(Document(code="200", plateform="linux", browser="khtml"))
			self.library.append(Document(code="200", plateform="winxp", browser="ie"))
		def testSimple(self):
			query = Query('plateform:winxp')
			self.assertEquals(set([1]), value(query, self.library).results())
		def testNot(self):
			query = Query('not plateform:winxp')
			self.assertEquals(set([0]), value(query, self.library).results())
		def testOr(self):
			query = Query(' plateform:winxp or plateform:linux')
			self.assertEquals(set([0, 1]), value(query, self.library).results())
		def testDummy(self):
			query = Query('not (plateform:winxp)')
			self.assertEquals(set([0]), value(query, self.library).results())
		def testOr(self):
			try:
				query = Query(" or toto:machin")
			except ParseException:
				pass
			query = Query(' plateform:winxp or plateform:linux')
			#print query.asXML()
		def testAll(self):
			q = """
not plateform:winxp
or (
	code:200 
	and  browser:firefox
)"""
			query = Query(q)
			#print query.asXML()
			#print value(query, self.library)
			self.assertEquals(set([0]), value(query, self.library).results())
	
	unittest.main()
