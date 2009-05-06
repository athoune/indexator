import marshal
import zlib

class WrongSizeException(Exception):
	pass

class BitSet:
	_data = 0L
	_size = 0
	def __init__(self,array):
		for element in array:
			if element :
				a = 1
			else:
				a = 0
			self._data = (self._data << 1) | a
			self._size += 1
	def __str__(self):
		return "<Bitset #%i %s>" % (self._size, str(bin(self._data))[2:])
	def __and__(self, other):
		if len(other) != len(self):
			raise WrongSizeException
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
	unittest.main()