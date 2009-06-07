#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Mathieu Lecarme <mathieu@garambrogne.net>"
__doc__ = """
"""

import struct
import datetime

import document
import filter as _filter


class Type(object):
	def pack(self, data):
		return struct.pack(self.fmt, data)
	def unpack(self, data):
		return struct.unpack(self.fmt, data)[0]

class String(Type):
	def pack(self, data):
		return data
	def unpack(self, data):
		return data

class Integer(Type):
	fmt = "Q"
class Float(Type):
	fmt = "d"
class Boolean(Type):
	fmt = '?'
"""
class DateTime(Type):
	fmt = 'L'
	def pack(self, data):
		return struct.pack(self.fmt, data.localtime)
	def unpack(self, data):
		return datetime.fromtimestamp(struct.unpack(self.fmt, data)[0])
"""

class Field(object):
	def __init__(self, type, inverse=True, store=True, filter = _filter.lower, lotOfValues = False):
		self.type = type
		self.inverse = inverse
		self.store = store
		self.filter = filter
		self.lotOfValues = lotOfValues
	def __repr__(self):
		return "<Field: %s>" % self.type.__name__

class MetaBase(type):
	def __init__(self, classname='Base', bases=(object,), dico= {}):
		#print "dict avant", dico
		self._definitions = {}
		for key, value in dico.iteritems():
			#print "key", key, isinstance(value, Field)
			if key[0] == '_':
				continue
			if isinstance(value, Field):
				self._definitions[key] = value
		#print "dict apres", dico
		return type.__init__(self, classname, (object, MetaBase, ), dico)

Base = MetaBase('Base', (object,), {})

if __name__ == '__main__':
	import unittest
	class Data(Base):
		name = Field(String)
		score = Field(Integer)
		tags = Field(String)
		def __init__(self, name, score, tags= None):
			self.name = name
			self.score = score
			self.tags = tags
	d = Data("Robert", 42)
	print d.name, d._definitions, d.__dict__
	d.test = Field(String)
	class ORMTypeTest(unittest.TestCase):
		def testInteger(self):
			integer = Integer()
			self.assertEquals(42, integer.unpack(integer.pack(42)))
		def testFloat(self):
			float = Float()
			self.assertEquals(42.2, float.unpack(float.pack(42.2)))
		def testBoolean(self):
			boolean = Boolean()
			self.assert_(boolean.unpack(boolean.pack(True)))
		'''
		def testDateTime(self):
			today = datetime.datetime.now()
			date = DateTime()
			self.assertEquals(today, date.unpack(date.pack(today)))
		'''
	unittest.main()