#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Mathieu Lecarme <mathieu@garambrogne.net>"
__doc__ = """
"""

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
