import marshal
import zlib
import math
import random as _random
import struct

class WrongSizeException(Exception):
	pass
# http://code.activestate.com/recipes/576738/

def empty(size=0):
	b = MBitSet()
	b._data = []
	b._size = size
	return b

def random(n=1):
	_random.seed()
	b = empty()
	b._size = n * b._WORD
	for a in range(n):
		b._data.append(_random.getrandbits(b._WORD))
	return b

class MBitSet:
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
		r = "<MbitSet #%i " % self._size
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
	def __getitem__(self, s):
		start, stop, step = s.indices(len(self))
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
		b = MBitSet()
		b._size = self._size
		b._data = []
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

class BitSet:
	_data = 0L
	_size = 0
	_minsize = 1024
	def __init__(self, value = None, size= 0):
		if type(value) == type(1):
			value = long(value)
		if type(value) == type(1L):
			self._data = value
			try:
				self._size = size or math.floor(math.log(self._data, 2)) + 1
			except Exception as e:
				self._size = 0
			return
		if value != None:
			for element in value:
				self.append(element)
	def append(self, elem):
		if elem :
			a = 1
		else:
			a = 0
		self._data = (self._data << 1) | a
		self._size += 1
	def pop(self):
		ret = self._data & 1
		self._data << 1
		self._size -= 1
		return ret
	def __str__(self):
		b = str(bin(self._data))[2:]
		b = '0' * int(self._size - len(b)) + b
		return "<Bitset #%i %s>" % (self._size, b)
	def _testSize(self,other):
		if len(other) != len(self):
			raise WrongSizeException
	def __and__(self, other):
		self._testSize(other)
		b = BitSet()
		b._size = self._size
		b._data = self._data & other._data
		return b
	def __or__(self, other):
		self._testSize(other)
		b = BitSet()
		b._size = self._size
		b._data = self._data | other._data
		return b
	def __len__(self):
		return int(self._size)
	def __eq__(self, other):
		return self._data == other._data
	def value(self):
		return self._data
	def __neg__(self):
		return BitSet(long(2L**self._size - 1) ^ self._data, len(self) )
	def dump(self, file):
		file.seek(0)
		file.write(marshal.dumps(int(self._size))[1:])
		if self._size > self._minsize:
			file.write('z')
			file.write(zlib.compress(marshal.dumps(self._data)[1:]))
		else:
			file.write('n')
			file.write(marshal.dumps(self._data)[1:])
		file.flush()

def load(file):
	file.seek(0)
	size =  marshal.loads('i' + file.read(4))
	if 'z' == file.read(1) :
		value = marshal.loads('l' + zlib.decompress(file.read()))
	else:
		value = marshal.loads('l' + file.read())
	return BitSet(value, size)
def mload(file):
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
	class SimpleTest(unittest.TestCase):
		def setUp(self):
			self.b = BitSet([True, True, False])
		def testInit(self):
			self.assert_(3, len(self.b))
			self.assert_(6L, self.b.value())
		def testSizeError(self):
			try:
				self.b & BitSet([True])
				self.assert_(False)
			except WrongSizeException:
				self.assert_(True)
		def testDump(self):
			self.assert_("<Bitset #3 110>" == str(self.b))
		def testPop(self):
			self.assert_(False == self.b.pop())
			self.assert_(2, len(self.b))
			self.assert_(BitSet([True,True]), self.b)
		def testAnd(self):
			self.assert_(BitSet([True, False, False ]), self.b & BitSet([True,False,True]))
		def testOr(self):
			self.assert_(BitSet([True, True, True]), self.b | BitSet([True,False,True]))
		def testLong(self):
			self.assert_(BitSet([True, True, False]) == BitSet(6L))
		def testNeg(self):
			self.assert_((-self.b) == BitSet(1L))
		def testDump(self):
			with tempfile.TemporaryFile() as f:
				self.b.dump(f)
				self.assert_(self.b, load(f))
		def testSize(self):
			b = BitSet(6L)
			self.assert_(3, len(b))
			b = BitSet(2**4096)
			self.assert_(4096, len(b))
		def testComress(self):
			b = BitSet(2**8 +1)
			out = StringIO.StringIO()
			b.dump(out)
			self.assert_(b, load(out))
		def testNeg(self):
			b = BitSet(9L)
			n = -b
			self.assert_(-n == b)
		def testLarge(self):
			for a in range(6):
				b = BitSet(2**(2**a) + 3)
				#print a, 2**a, len(b)
				n = -b
				#print n, b
				self.assert_(-n == b)
	class MTest(unittest.TestCase):
		def setUp(self):
			self.b = MBitSet([True, True, False])
		def testAppend(self):
			b = MBitSet()
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
			self.assert_(MBitSet([True, False, False ]), self.b & MBitSet([True,False,True]))
		def testOr(self):
			self.assert_(MBitSet([True, True, True]), self.b | MBitSet([True,False,True]))
		def testXor(self):
			self.assert_(MBitSet([False, True, True]), self.b ^ MBitSet([True,False,True]))
		def testDump(self):
			out = StringIO.StringIO()
			self.b.dump(out)
			self.assert_(self.b, mload(out))
		def testCompression(self):
			for a in range(8):
				out = StringIO.StringIO()
				b = random(2**a)
				b.dump(out)
				self.assert_(b, mload(out))
		def testIter(self):
			b = random(42)
			tas = []
			for a in b:
				tas.append(a)
			self.assert_(b, MBitSet(tas))

	unittest.main()