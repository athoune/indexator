#!/usr/bin/env python
# -*- coding: utf-8 -*-
import collections
import cPickle
import sys
try:
	import pytc
	TC = True
except:
	TC = False

"""
[TODO] choix du moteur, gdbm, tokyo cabinet ...
[TODO] création des index
"""

class Data:
	def __init__(self, file):
		self.data = {}
	def encodeKey(self, key):
		return str(key)
	def encodeValue(self, value):
		return marshal.dumps(value)
	def decodeValue(self, value):
		return marshal.loads(value)
	def __getitem__(self, item):
		return self.decodeValue(self.data[self.encodeKey(item)])
	def __setitem__(self, item, value):
		self.data[self.encodeKey(item)] = self.encodeValue(value)
	def __len__(self):
		return len(self.data)
	def __iter__(self):
		for k,v in self.data:
			yield k, self.decodeValue(v)

if TC:
	class TokyoCabinetData(pytc.HDB):
		def __init__(self, file):
			self.open(file, pytc.HDBOWRITER | pytc.HDBOCREAT)
		def __repr__(self):
			return '<TokyoCabinetData size:%i>' % (len(self))

class Index(collections.Mapping):
	_data = {}
	_indexed = None
	def __init__(self, map):
		for a in map:
			self._data[a.lower()] = map[a]
	def __getitem__(self, item):
		return self._data[item.lower()]
	def __len__(self):
		return len(self._data)
	def __iter__(self):
		return self._data.__iter__()

if __name__ == '__main__':
	if len(sys.argv) > 0:
		try:
			import psyco
			psyco.full()
		except ImportError:
			pass
		from log.apache import Combined
		c = Combined()
		f = file(sys.argv[1], 'r')
		i = 0
		d = TokyoCabinetData('/tmp/apache.htc')
		for line in f:
			i += 1
			d[str(i)] = cPickle.dumps(c.parse(line))
	else:
		import unittest
	
		class DataTest(unittest.TestCase):
			def testGetSet(self):
				if TC:
					d = TokyoCabinetData('/tmp/tc.htc')
					data = [1,2,3,"a"]
					d[42] = data
					self.assert_(data, d[42])
					self.assert_(1, d)
					print d
	
		class IndexTest(unittest.TestCase):
			def setUp(self):
				pass
			def testInit(self):
				m = {'Name' : 'Bob',
				'Sexe' : True,
				'tags' : ['sponge', 'sea'],
				}
				i = Index(m)
				#for k in i:
				#	print k

		unittest.main()
