#!/usr/bin/env python
# -*- coding: utf-8 -*-
import collections
import cPickle
import sys
import time
import pytc

"""
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

def tokyoCabinetData(file, mode='r'):
	tc = TokyoCabinetData()
	if mode not in ['r', 'w']:
		raise Exception
	file = "%s.htc" % file
	if mode == 'w':
		tc.open(file, pytc.HDBOWRITER | pytc.HDBOCREAT)
	if mode == 'r':
		tc.open(file, pytc.HDBOREADER)
	return tc
class TokyoCabinetData(pytc.HDB):
	def __init__(self):
		self.serializer = cPickle
	def __repr__(self):
		return '<TokyoCabinetData size:%i>' % (len(self))
	def __setitem__(self, item, value):
		self.putasync(str(item), self.serializer.dumps(value))
	def __getitem__(self, item):
		return self.serializer.loads(pytc.HDB.__getitem__(self, str(item)))
	def __contains__(self, key):
		return self.has_key(key)
def tokyoCabinetSortedData(file, mode='r'):
	tc = TokyoCabinetSortedData()
	if mode not in ['r', 'w']:
		raise Exception('only r or w')
	file = "%s.btc" % file
	if mode == 'w':
		tc.open(file, pytc.BDBOWRITER | pytc.BDBOCREAT)
	if mode == 'r':
		tc.open(file, pytc.BDBOREADER)
	return tc
class TokyoCabinetSortedData(pytc.BDB):
	def __init__(self):
		self.serializer = cPickle
	def __repr__(self):
		return '<TokyoCabinetSortedData size:%i>' % (len(self))
	def __setitem__(self, item, value):
		self.put(str(item), self.serializer.dumps(value))
	def __getitem__(self, item):
		return self.serializer.loads(pytc.BDB.__getitem__(self, str(item)))
	def __contains__(self, key):
		return self.has_key(key)

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
	if len(sys.argv) > 1:
		from log.apache import Combined
		c = Combined()
		f = file(sys.argv[1], 'r')
		i = 0
		d = tokyoCabinetData('/tmp/apache')
		chrono = time.time()
		for line in f:
			i += 1
			d[i] = c.parse(line)
			if i % 10 == 0:
				print ".",
			if i % 100 == 0:
				print " ", i, i / (time.time() - chrono), 'line/second'
