#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Mathieu Lecarme <mathieu@garambrogne.net>"
__doc__ = """
"""

import os
from multiprocessing import Pool
import struct
import glob

import index
import bitset
import filter as _filter

from parser import terms, Bloc

#[TODO] gerer les listes comme des strings de long long, un add fait un append directement dans TC
#[TODO] gere les index inverses comme des Btrees, pour permettre les > < et [ .. ]. Encodage des clefs, number, date, qui reste triable

class Library:
	def __init__(self, path, mode = 'r'):
		self.dir = path
		if mode not in ['r', 'w', 'a']:
			raise Exception
		if mode == 'a':
			self.mode = 'w'
		else:
			self.mode = mode
		if mode == 'w':
			for tc in glob.glob("%s/index_*.btc" % path):
				os.remove(tc)
			if not os.path.isdir(path):
				os.makedirs(path)
			self.store = index.tokyoCabinetData("%s/store" % path, mode)
			self.store.vanish()
			self.cpt = 0
		else:
			self.store = index.tokyoCabinetData("%s/store" % path, self.mode)
			self.cpt = self.store.rnum() - 1
		self.inverse = {}
	def __len__(self):
		return self.cpt
	def _addInverse(self, key, value, id):
		value = str(value)
		self._index(key).putcat(value, struct.pack('I', id))
	def _index(self, key):
		if not self.inverse.has_key(key):
			self.inverse[key] = index.tokyoCabinetSortedData("%s/inverse_%s" % (self.dir, key), self.mode)
		return self.inverse[key]
	def append(self, document):
		"Add a new document"
		if self.mode == 'r':
			raise Exception
		#if document.id == None:
		document.id = self.cpt
		self.store[document.id] = document
		
		for key, value in document.inverse.iteritems():
			if hasattr(value, '__iter__'):
				for v in value:
					self._addInverse(key, v, document.id)
			else:
				self._addInverse(key, value, document.id)
		self.cpt += 1
		return self.cpt -1
	def get(self, key, value):
		"A simple query for a key=value"
		value = str(value)
		index = self._index(key)
		try:
			b = index.get(value)
			return bitset.fromblob(self.cpt, b)
		except KeyError:
			return bitset.empty(self.cpt)
	def query(self, query):
		return Bloc(terms.parseString(query)).value(self)
	def documents(self, bitset):
		"An iterator wich fetch all document in a bitset"
		for key in bitset.results():
			yield self.store[key]
	def fields(self):
		data = {}
		for key in self.inverse:
			k,v = key.split(':', 1)
			if not data.has_key(k):
				data[k] = []
			data[k].append(v)
		return data

class MultiLibrary:
	_THREAD = 4
	_pool = True
	def __init__(self, libraries):
		self.libraries = libraries
	def query(self, query):
		bloc = Bloc(terms.parseString(query))
		print bloc
		if self._pool:
			m = Pool(processes=self._THREAD).map
		else:
			m = map
		def _map(args):
			ret
			size, data = args
			
			return bloc.value(lib)
		class Iterator:
			def __init__(self, libraries):
				self.libraries = libraries
			def __iter__(self):
				for lib in self.libraries:
					yield lib.freeze()
		tas = m(_map , Iterator(self.libraries))
		return tas

class Document:
	def __init__(self, id = None, **kargs):
		self.id = id
		self.data = {}
		self.inverse = {}
		for key, value in kargs.iteritems():
			self.set(key, value)
	def set(self, key, value, inverse=True, store=True, filter = _filter.lower, lotOfValues=False):
		if filter != None:
			value = filter(value)
		if hasattr(value, '__iter__'):
			for v in value:
				self.set(key, v, inverse, store)
			return
		if store:
			if key in self.data:
				if type(self.data[key]) != 'list':
					self.data[key] = [self.data[key]]
				self.data[key].append(value)
			else:
				self.data[key] = value
		if inverse and value != None:
			if key in self.inverse:
				if type(self.inverse[key]) != 'list':
					self.inverse[key] = [self.inverse[key]]
				self.inverse[key].append(value)
			else:
				self.inverse[key] = value
	def __setitem__(self, key, value):
		self.set(key, value, True, True)
	def __getitem__(self, key):
		return self.data[key]
	def __repr__(self):
		return "<Document #%s %s>" % (self.id, self.data)

if __name__ == '__main__':
	datas = [
		{'nom': 'Bob',
		'score': 2},
		{'nom': 'Casimir',
		'score' : 42,
		'tags' : ['simple', 'monster']},
		{'nom': 'Andre',
		'score': 42}
	]
	import unittest
	import random

	"""
	class LibraryTest(unittest.TestCase):
		def testMulti(self):
			libraries = []
			for a in range(4):
				print a
				library = Library('/tmp/index_%i.test' % a, 'w')
				for b in range(10):
					document = Document(value=b, name=random.choice(('Pim', 'Pam', 'Poum')))
					print '\t',b, document
					library.append(document)
				libraries.append(library)
			multi = MultiLibrary(libraries)
			print multi.query('name:pim')
"""
	class DocumentTest(unittest.TestCase):
		def setUp(self):
			self.l = Library('/tmp/index.test', 'w')
			for data in datas:
				d = Document()
				for k,v in data.iteritems():
					d[k] = v
				self.l.append(d)
		def testKargs(self):
			d = Document(name='Bob', score=42)
			self.assertEquals(42, d['score'])
		def testNot(self):
			b = - self.l.get('score', 42)
			self.assertEquals(set([0]), b.results())
		def testAnd(self):
			b = self.l.get('score', 42) & self.l.get('tags', 'simple')
			for document in self.l.documents(self.l.query("score:42 and tags:simple")):
				print document
			self.assertEquals(1, b.cardinality())
			self.assertEquals(set([1]), b.results())
			for doc in self.l.documents(b):
				self.assertEquals('casimir',doc['nom'])
	unittest.main()
