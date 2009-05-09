import marshal
import zlib
import math
import random as _random
import struct

class WrongSizeException(Exception):
	pass
# http://code.activestate.com/recipes/576738/

def empty(size=0):
	"""
	Build an empty BitSet
	"""
	b = BitSet()
	b._data = []
	b._size = size
	return b

def random(n=1):
	"""
	Build a random BitSet
	"""
	_random.seed()
	b = empty()
	b._size = n * b._WORD
	for a in range(n):
		b._data.append(_random.getrandbits(b._WORD))
	return b

class BitSet:
	_data = []
	_size = 0
	_WORD = 128
	_ZSIZE = 1024
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
		b = empty(self._size)
		for i in range(len(self._data)):
			b._data.append(other._data[i] & self._data[i])
		return b
	def __or__(self, other):
		b = empty(self._size)
		for i in range(len(self._data)):
			b._data.append(other._data[i] | self._data[i])
		return b
	def __xor__(self, other):
		b = empty(self._size)
		for i in range(len(self._data)):
			b._data.append(other._data[i] ^ self._data[i])
		return b
	def __neg__(self):
		b = empty(self._size)
		for i in self._data:
			b._data.append(long(2**self._WORD - 1) ^ i)
		return b
	def cardinality(self):
		total = 0
		for i in self._data:
			total += cached_cardinality(i)
		return total
	def dump(self, file):
		file.seek(0)
		file.write(struct.pack('l', self._size))
		d = marshal.dumps(self._data)[1:]
		if self._size > self._ZSIZE:
			file.write('z')
			z = zlib.compress(d)
			file.write(z)
			t = 1.0 * len(z) / len(d)
		else:
			file.write('n')
			file.write(d)
			t = 1
		file.flush()
		return t

def cardinality(i):
	total = 0
	while i > 1:
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
	total = 0
	while i > 255:
		total += _cc[i & 255]
		i = i >> 8
	return total


def load(file):
	file.seek(0)
	b = empty(struct.unpack('l', file.read(4)))
	if 'z' == file.read(1) :
		d = zlib.decompress(file.read())
	else:
		d = file.read()
	b._data = marshal.loads('[' + d)
	return b

if __name__ == '__main__':
	import unittest
	import tempfile
	import StringIO
	class BitSetTest(unittest.TestCase):
		def setUp(self):
			self.b = BitSet([True, True, False])
		def testAppend(self):
			b = BitSet()
			for aa in range(4000):
				for a in range(256):
					b.append(True)
			c = -b
			#print b, c
			#print len(b)
			self.assert_(-c == b)
		def testCardinality(self):
			self.assert_(2, self.b.cardinality())
		def testAnd(self):
			self.assert_(BitSet([True, False, False ]), self.b & BitSet([True,False,True]))
		def testOr(self):
			self.assert_(BitSet([True, True, True]), self.b | BitSet([True,False,True]))
		def testXor(self):
			self.assert_(BitSet([False, True, True]), self.b ^ BitSet([True,False,True]))
		def testDump(self):
			out = StringIO.StringIO()
			self.b.dump(out)
			self.assert_(self.b, load(out))
		def testCompression(self):
			for a in range(8):
				out = StringIO.StringIO()
				b = random(2**a)
				b.dump(out)
				self.assert_(b, load(out))
		def testIter(self):
			b = random(42)
			tas = []
			for a in b:
				tas.append(a)
			self.assert_(b, BitSet(tas))

	unittest.main()