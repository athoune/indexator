import marshal
import zlib

class WrongSizeException(Exception):
	pass

class BitSet:
	_data = 0L
	_size = 0
	def __init__(self,array):
		if array != None:
			for element in array:
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
		b = BitSet(None)
		b._size = self._size
		b._data = self._data & other._data
		return b
	def __or__(self, other):
			self._testSize(other)
			b = BitSet(None)
			b._size = self._size
			b._data = self._data | other._data
			return b
	def __len__(self):
		return self._size
	def value(self):
		return self._data

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
	unittest.main()