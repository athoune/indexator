__doc__ = """
"""
__author__ = "Mathieu Lecarme <mathieu@garambrogne.net>"

import marshal
import zlib
import bz2
import math
import random as _random
import struct
try:
	from index_pb2 import Index
	PROTOBUF = True
except:
	PROTOBUF = False
try:
	import lzo
	LZO = True
except:
	LZO = False
try:
	import pylzma
	LZMA = True
except:
	LZMA = False

__all__ = ['empty', 'Bitset', 'Serializator']

compressors = {}

class NullCompressor:
	def compress(self, data):
		return data
	def decompress(self, data):
		return data

compressors['n'] = NullCompressor()
compressors['z'] = zlib
compressors['b'] = bz2
if LZO:
	compressors['o'] = lzo
if LZMA:
	compressors['m'] = pylzma

class Serializator:
	"Classical Python implementation"
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
		"Google's protobuf implementation"
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
	"""
	Build an empty BitSet
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
	_WORD = 64
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
		b._data = []
		for i in self._data:
			b._data.append(long(2**self._WORD - 1) ^ i)
		return b
	def cardinality(self):
		total = 0
		for i in self._data:
			total += cached_cardinality(i)
		return total

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

if __name__ == '__main__':
	import unittest
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
			serialz = [Serializator]
			if PROTOBUF:
				serialz.append(ProtoBufSerializator)
			for s in serialz:
				out = StringIO.StringIO()
				serial = s(out)
				serial.dump(self.b)
				self.assert_(self.b, serial.load())
		def testCompression(self):
			for c in compressors.keys():
				for a in range(8):
					out = StringIO.StringIO()
					serial = Serializator(out)
					b = random(2**a)
					b.compressor = c
					serial.dump(b)
					self.assert_(b, serial.load())
		def testIter(self):
			b = random(42)
			tas = []
			for a in b:
				tas.append(a)
			self.assert_(b, BitSet(tas))
		def testEmpty(self):
			b = empty(42)
			self.assert_(42 * '0', str(b))

	unittest.main()