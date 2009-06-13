#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Mathieu Lecarme <mathieu@garambrogne.net>"

import struct
from cStringIO import StringIO

from compressor import compressors
import bitset

__all__ = ['Serializator']
	
class Serializator:
	"Simple serialization"
	def __init__(self, out, compressor = 'n', thresold=1024):
		self.file = out
		self.compressor = compressor
		self.thresold = thresold
	def dump(self, bitset):
		f = self.file
		f.seek(0)
		buff = dump(bitset)
		if self.compressor != 'n' and len(bitset) > self.thresold:
			f.write(self.compressor)
			z = compressors[self.compressor].compress(buff)
			t = 1.0 * len(z) / len(buff)
			f.write(z)
		else:
			f.write('n')
			f.write(buff)
			t = 1.0
		f.flush()
		return t
	def load(self):
		f = self.file
		f.seek(0)
		buff = compressors[f.read(1)].decompress(f.read())
		return load(buff)

def dump(bitset):
	"serialize a bitset"
	buffer = StringIO()
	buffer.write(struct.pack('Q', bitset._size))
	for a in bitset._data:
		buffer.write(struct.pack('Q', a))
	buffer.seek(0)
	return buffer.read()
def load(buff):
	"make a bitset from a bitflow"
	b = bitset.empty()
	buffer = StringIO(buff)
	b._size = struct.unpack('Q', buffer.read(8))[0]
	b._data = []
	while True:
		bloc = buffer.read(8)
		if bloc == "": break
		b._data.append(long(struct.unpack('Q', bloc)[0]))
	return b

if __name__ == '__main__':
	import unittest
	from bitset import BitSet, empty, random

	class SerializatorTest(unittest.TestCase):
		def setUp(self):
			self.b = random(2048 / 64)
		def testDump(self):
			serialz = [Serializator]
			for serializator in serialz:
				out = StringIO()
				serial = serializator(out)
				serial.compressor = 'n'
				self.assertEquals(8+2048/8,len(dump(self.b)))
				serial.dump(self.b)
				self.assertEqual(self.b, serial.load())
		def testCompression(self):
			for compress in compressors.keys():
				for a in range(8):
					out = StringIO()
					serial = Serializator(out)
					b = random(2**a)
					b.compressor = compress
					serial.dump(b)
					#print a, 2**a, compress
					self.assertEqual(b, serial.load())
	unittest.main()
