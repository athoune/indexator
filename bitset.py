import marshal
import zlib
import math

class WrongSizeException(Exception):
	pass
# http://code.activestate.com/recipes/576738/

class MBitSet:
	_data = []
	_size = 0
	_word = 128
	def __init__(self, data = []):
		for a in data:
			self.append(a)
	def append(self, bool):
		if bool: a = 1
		else:    a = 0
		self._size += 1
		if self._data == []:
			self._data = [a]
			return
		last = self._data[-1]
		if (self._size -1) % self._word == 0:
			self._data.append(0)
			last = a
		else :
			last = (last << 1) | a
		self._data[-1] = last
	def __repr__(self):
		r = "<MbitSet #%i " % self._size
		for i in self._data:
			n = bin(i)[2:]
			r += "\n" + (self._word - len(n)) * "0" + n
		return  r + ">"
	def __len__(self):
		return int(self._size)
	def __eq__(self, other):
		return self._data == other._data
	def __neg__(self):
		b = MBitSet()
		b._size = self._size
		b._data = []
		for i in self._data:
			b._data.append(long(2**self._word - 1) ^ i)
		return b

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
			for aa in range(40000):
				for a in range(256):
					b.append(True)
			c = -b
			#print b, c
			print len(b)
			self.assert_(-c == b)

	unittest.main()