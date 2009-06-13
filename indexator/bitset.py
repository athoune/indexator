#!/usr/bin/env python
# -*- coding: utf-8 -*-

__doc__ = """
A bitset is an array of boolean wich implements all boolean algebra operations.

A bitset can be stored and retrieved, compressed or not.
"""
__author__ = "Mathieu Lecarme <mathieu@garambrogne.net>"

import random as _random
import time
from multiprocessing import Pool
from cStringIO import StringIO
import struct

__all__ = ['empty', 'Bitset', 'random', 'fromids', 'fromblob']


class WrongSizeException(Exception):
	pass
# http://code.activestate.com/recipes/576738/

def empty(size=0):
	"""Build an empty BitSet
	"""
	b = BitSet()
	b._data = []
	b._size = size
	n = size // b._WORD
	if size % b._WORD > 0 : n += 1
	for a in range(n):
		b._data.append(0)
	return b

def random(n=1):
	"Build a random BitSet"
	_random.seed()
	b = empty()
	b._size = n * b._WORD
	for a in range(n):
		b._data.append(_random.getrandbits(b._WORD))
	return b

def fromids(size, ids):
	b = empty(size)
	for id in ids:
		b[id] = True
	return b

def fromblob(size, blob):
	b = empty(size)
	buffer = StringIO(blob)
	while True:
		bloc = buffer.read(4)
		if bloc == "": break
		b[struct.unpack('I', bloc)[0]] = True
	return b

def _and(args):
	me, other, size = args
	return me & other

def _neg(args):
	me, other, size = args
	return long(2**size -1) ^ me

def _or(args):
	me, other, size = args
	return me | other
	
def _xor(args):
	me, other, size = args
	return me ^ other
	

class BitSet:
	"""
A bitset is an array of boolean wich implements all boolean algebra operations.
	"""
	_data = []
	_size = 0
	_WORD = 64
	_THREAD = 2
	_pool = False
	def __init__(self, data = []):
		for a in data:
			self.append(a)
	def append(self, bool):
		a = int(bool)
		self._size += 1
		if self._data == []:
			self._data = [a]
			return
		last = self._data[-1]
		if (self._size -1) % self._WORD == 0:
			self._data.append(0)
			last = a
		else :
			last = (last << 1) | a
		self._data[-1] = last
	def __repr__(self):
		r = "<BitSet #%i " % self._size
		for i in self._data:
			n = bin(i)[2:]
			r += "\n" + (self._WORD - len(n)) * "0" + n
		return  r + ">"
	def __str__(self):
		r = ''
		for i in self._data:
			n = bin(i)[2:]
			r += (self._WORD - len(n)) * "0" + n
		return r
	#def __getitem__(self, s):
	#	start, stop, step = s.indices(len(self))
	def __iter__(self):
		for a in range(len(self)):
			w = self._data[a // self._WORD]
			aa = (len(self) - a -1) % self._WORD
			yield bool(w  & (1 << aa))
	def __len__(self):
		return int(self._size)
	def __eq__(self, other):
		#print self._data, other._data
		return self._data == other._data
	def __and__(self, other):
		return self._map(other, _and)
	def __or__(self, other):
		return self._map(other, _or)
	def __xor__(self, other):
		return self._map(other, _xor)
	def __neg__(self):
		return self._map(None, _neg)
	def __setitem__(self, key, value):
		if key > self._size:
			raise KeyError
		nbloc = key // self._WORD
		n = key % self._WORD
		if value:
			self._data[nbloc] |= (1 << n)
		else:
			self._data[nbloc] &= ~(1 << n)
	def __getitem__(self, key):
		if key > self._size:
			raise KeyError
		return  self._data[key // self._WORD] & (1 << (key % self._WORD))
	def cardinality(self):
		total = 0
		for i in self._data:
			total += cached_cardinality(i)
		return total
	def _map(self, other, method):
		b = empty(self._size)
		if self._pool:
			m = Pool(processes=self._THREAD).map
		else:
			m = map
		b._data = m(method, BitsetIterator(self, other))
		return b
	def results(self):
		results = set()
		cpt = 0
		for value in self:
			if value : results.add(cpt)
			cpt +=1
		return results

class BitsetIterator:
	def __init__(self, one, other = None):
		self.one = one
		self.other = other
	def __iter__(self):
		size = len(self.one._data)
		for a in range(len(self.one._data)):
			if a+1 < size:
				s = self.one._WORD
			else:
				s = self.one._size - a * self.one._WORD
			if self.other != None:
				o = self.other._data[a]
			else:
				o = None
			yield self.one._data[a], o, s

def cardinality(i):
	total = 0
	while i >= 1:
		if i & 1 == 1 : total += 1
		i = i >> 1
	return total

_cc = None
def cached_cardinality(i):
	global _cc
	if _cc == None:
		_cc = {}
		for a in range(256):
			_cc[a] = cardinality(a)
	total = _cc[i & 255]
	while i > 255:
		total += _cc[i & 255]
		i = i >> 8
	return total

if __name__ == '__main__':
	import unittest
	class BitSetTest(unittest.TestCase):
		def setUp(self):
			self.b = BitSet([True, True, False])
		def testPickle(self):
			import cPickle
			self.assertEquals(self.b, cPickle.loads(cPickle.dumps(self.b)))
		def testFromids(self):
			self.assertEquals(self.b, fromids(3, [2,1]))
		def testFromBlob(self):
			tmp = struct.pack('I', 2) + struct.pack('I', 1)
			self.assertEquals(self.b, fromblob(3, tmp))
		def testIterator(self):
			i = BitsetIterator(random(42))
			for a in i:
				pass
				#print a
		def testGet(self):
			#for a in range(len(self.b)):
			#	print a, self.b[a]
			#print self.b._data[0]
			self.assert_(not self.b[0])
			self.assert_(self.b[1])
			self.assert_(self.b[2])
		def testSet(self):
			b = BitSet([True, True, False])
			try:
				b[42] = True
				self.fail()
			except KeyError:
				pass
				
			b[1] = True
			self.assertEqual(BitSet([True, True, False]), b)
			b = BitSet([True, False, False])
			b[1] = True
			self.assertEqual(BitSet([True, True, False]), b)
			b[0] = False
			self.assertEqual(BitSet([True, True, False]), b)
			b[0] = True
			self.assertEqual(BitSet([True, True, True]), b)
			b[2] = False
			self.assertEqual(BitSet([False, True, True]), b)
		def testNot(self):
			self.assertEqual(BitSet([False, False, True]), - self.b)
		def testAppend(self):
			b = BitSet()
			for aa in range(4000):
				for a in range(256):
					b.append(True)
			c = -b
			#print b, c
			#print len(b)
			self.assertEqual(-c, b)
		def _testThread(self):
			for a in range(16):
				b = random(1492)
				b._THREAD = a
				bb = random(1492)
				chrono = time.time()
				for aa in range(500):
					b ^ bb
				print a, time.time() - chrono
		def testCardinality(self):
			self.assertEqual(2, self.b.cardinality())
		def testAnd(self):
			self.assertEqual(BitSet([True, False, False ]), self.b & BitSet([True,False,True]))
		def testOr(self):
			self.assertEqual(BitSet([True, True, True]), self.b | BitSet([True,False,True]))
		def testXor(self):
			self.assertEqual(BitSet([False, True, True]), self.b ^ BitSet([True,False,True]))
		def testSimpleIter(self):
			z = [False, True, False]
			b = BitSet(z)
			self.assertEqual(1, b.cardinality())
			self.assertEqual(3, len(b))
			cpt = 0
			for a in b:
				#print z[cpt], a
				self.assertEqual(z[cpt], a)
				cpt += 1
		def testIter(self):
			b = random(42)
			tas = []
			for a in b:
				tas.append(a)
			self.assertEqual(b, BitSet(tas))
		def testResults(self):
			self.assertEquals(set([0,1]), self.b.results())
	unittest.main()