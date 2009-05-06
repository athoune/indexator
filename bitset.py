import marshal
import zlib

class WrongSizeException(Exception):
	pass
# http://code.activestate.com/recipes/576738/
class BitSet:
	_data = 0L
	_size = 0
	def __init__(self, value = None):
		if type(value) == type(1L):
			self._data = value
			try: self._size = math.floor(math.log(self._data, 2)) + 1
			except Exception: self._size = 0
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
		return "<Bitset #%i %s>" % (self._size, str(bin(self._data))[2:])
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
		return self._size
	def __eq__(self, other):
		return self._data == other._data
	def value(self):
		return self._data
	def dump(self, file):
		marshal.dump(self._data, file)

def load(file):
	b = BitSet()
	b.setLong(marshal.load(file))
	return b

if __name__ == '__main__':
	import unittest
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
	unittest.main()