#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Mathieu Lecarme <mathieu@garambrogne.net>"
__doc__ = """
Simple filter wich can be piped.
"""

import types

class MetaFilter:
	def __init__(self, filter):
		self.filters = [filter]
	def append(self, other):
		self.filters.append(other)
	def __or__(self,other):
		self.append(other)
		return self
	def filter(self, data):
		for filter in self.filters:
			data = filter.filter(data)
		return data

class Filter:
	def __or__(self, other):
		meta = MetaFilter(self)
		meta.append(other)
		return meta

class TextFilter(Filter):
	def filter(self, data):
		if type(data) in [types.StringType, types.UnicodeType]:
			return self.textFilter(data)
		return data
	def textFilter(self, data):
		return data

letters = {
'a':u'àâä',
'e':u'èéêï'
}

accents = {}
for letter, accentz in letters.iteritems():
	for accent in accentz:
		accents[accent] = letter 


class Accent(TextFilter):
	def textFilter(self, data):
		global accents
		tmp = ''
		for letter in data:
			if letter in accents:
				tmp += accents[letter]
			else:
				tmp += letter
		return tmp
	

class Lower(TextFilter):
	"To lower filter"
	def textFilter(self, data):
		return data.lower()

if __name__ == '__main__':
	import unittest
	class FilterTest(unittest.TestCase):
		def testLower(self):
			self.assertEquals('bob', Lower().filter('BoB'))
		def testAccent(self):
			self.assertEquals('pepe', Accent().filter(u'pépé'))
		def testMeta(self):
			filter = Lower() | Accent()
			self.assertEquals('pepe', filter.filter(u'Pépé'))
	unittest.main()
