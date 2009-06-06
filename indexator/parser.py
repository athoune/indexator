#!/usr/bin/env python
# -*- coding: utf-8 -*-

__doc__ = """
A boolean language syntax to querying library.
"""
__author__ = "Mathieu Lecarme <mathieu@garambrogne.net>"

from pyparsing import *

__all__ = ['terms', 'Word', 'Operator', 'Bloc', 'Not']

# simple tokens
simple = Word(alphanums)
quoted = dblQuotedString.setParseAction(removeQuotes)
single = simple | quoted
special = Combine(Word(alphas) + ":" + single).setParseAction(lambda t: Word(t[0]))

# boolean operators
operator = (CaselessLiteral("or") | CaselessLiteral("and") | CaselessLiteral("xor")).setParseAction(lambda t: Operator(t[0]))

# recursive parenthetical groups
terms = Forward()
parenthetical = Group(Suppress("(") + Group(terms) + Suppress(")")).setParseAction(lambda t: Bloc(t))

# negative terms
negative = Group(Suppress(CaselessLiteral("not")) + (special | parenthetical)).setParseAction(lambda t: Not(t))

# bring it all together!
term = special | parenthetical | negative 
terms << term + ZeroOrMore(operator + terms)
query = OneOrMore(terms)# + StringEnd()

class Token:
	"Abstract class for representation"
	def __repr__(self):
		return str(self)
class Word(Token):
	def __init__(self, s):
		data = s.split(':')
		self.field = data[0]
		self.data = data[1]
	def value(self, library):
		return library.get(self.field, self.data)
	def __str__(self):
		return '<%s:%s>' % (self.field, self.data)
class Operator(Token):
	def __init__(self, s):
		self.action = s
	def __str__(self):
		return '<%s>' % self.action
class Bloc(Token):
	def __init__(self, values):
		self.values = values
	def __str__(self):
		return '(%s)' % self.values
	def value(self, library):
		value = self.values[0].value(library)
		action = None
		for token in self.values[1:]:
			#print type(token), token
			if action == None:
				action = token.action
			else:
				#print value, action, token
				if action == 'or':
					value = value | token.value(library)
				if action == 'and':
					value = value & token.value(library)
				if action == 'xor':
					value = value ^ token.value(library)
				action == None
		return value
class Not(Bloc):
	def __str__(self):
		return 'not(%s)' % self.values
	def value(self, library):
		return - Bloc.value(library)

if __name__ == '__main__':
	t =  terms.parseString("""not palteform:winxp or (code:200 and not browser:firefox)""")
	print t
	#print t.dump()
	indent = 0
	def eat(t):
		if isinstance(t,ParseResults):
			#print t.getName()
			global indent
			indent += 1
			for a in t:
				eat(a)
			indent -= 1
		else:
			print indent * "\t", t
	eat(t)