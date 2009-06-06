#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Mathieu Lecarme <mathieu@garambrogne.net>"
__doc__ = """
Simple filter wich can be piped.
"""

import types

__all__ = ['accent', 'lower']

class MetaFilter:
	def __init__(self, filter):
		self.filters = [filter]
	def append(self, other):
		self.filters.append(other)
	def __or__(self,other):
		self.append(other)
		return self
	def __call__(self, data):
		for filter in self.filters:
			data = filter(data)
		return data

class Filter:
	def __or__(self, other):
		meta = MetaFilter(self)
		meta.append(other)
		return meta

class TextFilter(Filter):
	def __call__(self, data):
		if type(data) in [types.StringType, types.UnicodeType]:
			return self.textFilter(data)
		return data
	def textFilter(self, data):
		return data

_letters = {
'a':u'àâä',
'e':u'èéêï',
'i':u'ìïî',
'o':u'òôö',
'u':u'ùûü',
'n':u'ñ'
}

_accents = {}
for letter, accentz in _letters.iteritems():
	for accent in accentz:
		_accents[accent] = letter 


class Accent(TextFilter):
	def textFilter(self, data):
		global _accents
		tmp = ''
		for letter in data:
			if letter in _accents:
				tmp += _accents[letter]
			else:
				tmp += letter
		return tmp

accent = Accent()

class Lower(TextFilter):
	"To lower filter"
	def textFilter(self, data):
		return data.lower()

lower = Lower()

if __name__ == '__main__':
	import unittest
	class FilterTest(unittest.TestCase):
		def testLower(self):
			self.assertEquals('bob', lower('BoB'))
		def testAccent(self):
			self.assertEquals('pepe', accent(u'pépé'))
		def testMeta(self):
			self.assertEquals('pepe', (lower | accent)(u'Pépé'))
	unittest.main()
