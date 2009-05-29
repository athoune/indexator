#!/usr/bin/env python
# -*- coding: utf-8 -*-

__doc__ = """
A bitset is an array of boolean wich implements all boolean algebra operations.

A bitset can be stored and retrieved, compressed or not.
"""
__author__ = "Mathieu Lecarme <mathieu@garambrogne.net>"

import marshal
import math
import random as _random
import struct
from multiprocessing import Pool
try:
	from index_pb2 import Index
	PROTOBUF = True
except ImportError:
	PROTOBUF = False

from compressor import compressors

__all__ = ['empty', 'Bitset', 'Serializator']

class Serializator:
	"Simple serialization"
	def __init__(self, file):
		self.file = file
		self.compressor = 'z'

	def _dump(self, bitset):
		return struct.pack('l', bitset._size) + marshal.dumps(bitset._data)[1:]

	def dump(self, bitset):
		self.file.seek(0)
		buff = self._dump(bitset)
		if bitset._size > bitset._ZSIZE:
			self.file.write(self.compressor)
			z = compressors[self.compressor].compress(buff)
			t = 1.0 * len(z) / len(buff)
			self.file.write(z)
		else:
			self.file.write('n')
			self.file.write(buff)
			t = 1.0
		self.file.flush()
		return t

	def _load(self, buff):
		b = empty(struct.unpack('l', buff[:4])[0])
		b._data = marshal.loads('[' + buff[4:])
		return b
	def load(self):
		self.file.seek(0)
		compress = compressors[self.file.read(1)]
		buff = compress.decompress(self.file.read())
		return self._load(buff)

if PROTOBUF:
	__all__.append('ProtoBufSerializator')
	class ProtoBufSerializator(Serializator):
		"Google's protobuf serialization"
		def _dump(self, bitset):
			index = Index()
			index.size = bitset._size
			for d in bitset._data:
				bloc = index.blocs.add()
				bloc.data = d
			return index.SerializeToString()
		def _load(self, buff):
			index = Index()
			index.ParseFromString(buff)
			b = empty(index.size)
			b._data = []
			for bloc in index.blocs:
				b._data.append(bloc.data)
			return b

class WrongSizeException(Exception):
	pass
# http://code.activestate.com/recipes/576738/

def empty(size=0):
	"""Build an empty BitSet
	[TODO] building large bitset without filling it one bit at time
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
	_ZSIZE = 1024
	_THREAD = 4
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
		return self._data == other._data
	def __and__(self, other):
		return self.map(other, _and)
	def __or__(self, other):
		return self.map(other, _or)
	def __xor__(self, other):
		return self.map(other, _xor)
	def __neg__(self):
		return self.map(None, _neg)
	def cardinality(self):
		total = 0
		for i in self._data:
			total += cached_cardinality(i)
		return total
	def map(self, other, method):
		p = Pool(processes=self._THREAD)
		b = empty(self._size)
		b._data = p.map(method, BitsetIterator(self, other))
		return b

from functools import wraps
def mapDecorator(func):
	@wraps(f)
	def wrapper(*args, **kwds):
		p = Pool(processes=4)
		b = empty(self._size)
		b._data = p.map(f, BitsetIterator(self, other))
		return b
	return wrapper

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
	import StringIO
	class BitSetTest(unittest.TestCase):
		def setUp(self):
			self.b = BitSet([True, True, False])
		def testIterator(self):
			i = BitsetIterator(random(42))
			for a in i:
				pass
				#print a
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
		def testCardinality(self):
			self.assertEqual(2, self.b.cardinality())
		def testAnd(self):
			self.assertEqual(BitSet([True, False, False ]), self.b & BitSet([True,False,True]))
		def testOr(self):
			self.assertEqual(BitSet([True, True, True]), self.b | BitSet([True,False,True]))
		def testXor(self):
			self.assertEqual(BitSet([False, True, True]), self.b ^ BitSet([True,False,True]))
		def testDump(self):
			serialz = [Serializator]
			if PROTOBUF:
				serialz.append(ProtoBufSerializator)
			for s in serialz:
				out = StringIO.StringIO()
				serial = s(out)
				serial.dump(self.b)
				self.assertEqual(self.b, serial.load())
		def testCompression(self):
			for c in compressors.keys():
				for a in range(8):
					out = StringIO.StringIO()
					serial = Serializator(out)
					b = random(2**a)
					b.compressor = c
					serial.dump(b)
					self.assertEqual(b, serial.load())
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
	unittest.main()