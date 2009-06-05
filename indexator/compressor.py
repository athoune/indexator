#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Mathieu Lecarme <mathieu@garambrogne.net>"
__doc__ = """
An abstraction for differents compressions with a single letter signature.
"""

__all__ = ['compressors']

import zlib
import bz2
try:
	import lzo
	LZO = True
except ImportError:
	LZO = False
try:
	import pylzma
	LZMA = True
except ImportError:
	LZMA = False

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

if __name__ == '__main__':
	import unittest
	class CompressTest(unittest.TestCase):
		def testCompression(self):
			for compress in compressors.values():
				test = "Il fait beau et chaud"
				self.assertEquals(test, compress.decompress(compress.compress(test)))
	unittest.main()
