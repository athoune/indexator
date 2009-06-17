import unittest

import struct
from indexator.bitset import BitSet, empty, BitsetIterator, fromblob, fromids, random

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
		b = empty(3)
		self.assertEqual(0, b._data[0])
		b[2] = True
		self.assertEqual(4, b._data[0])
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
		z = [False, True, True]
		b = BitSet(z)
		self.assertEqual(2, b.cardinality())
		self.assertEqual(3, len(b))
		cpt = 2
		for a in b:
			#print z[cpt], a
			self.assertEqual(z[cpt], a)
			cpt -= 1
	def testIter(self):
		bit = random(42)
		tas = []
		for bool in bit:
			tas.append(bool)
		tas.reverse()
		self.assertEqual(bit, BitSet(tas))
	def testResults(self):
		self.assertEquals(set([2,1]), self.b.results())

if __name__ == '__main__':
	unittest.main()