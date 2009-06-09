#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Mathieu Lecarme <mathieu@garambrogne.net>"
__doc__ = """
"""

import os

import index
import bitset
import filter as _filter

from parser import terms, Bloc

#[TODO] gerer les listes comme des strings de long long, un add fait un append directement dans TC
#[TODO] gere les index inverses comme des Btrees, pour permettre les > < et [ .. ]. Encodage des clefs, number, date, qui reste triable

class Library:
	def __init__(self, path, raz = False):
		try:
			os.makedirs(path)
		except OSError:
			pass
		self.dir = path
		self.cpt = 0
		if raz:
			for f in ['store', 'inverse']:
				try:
					os.remove("%s/%s.htc" % (path, f))
				except OSError:
					pass
					#print 'oups', "%s/%s.htc" % (path, f)
		self.store = index.TokyoCabinetData("%s/store.htc" % path)
		self.inverse = index.TokyoCabinetData("%s/inverse.htc" % path)
	def append(self, document):
		"Add a new document"
		if document.id == None:
			document.id = self.cpt
		self.store[document.id] = document
		keys = self.inverse.keys()
		for i in document.inverse:
			if i not in keys: keys.append(i)
		#print keys
		for key in keys:
			if self.inverse.has_key(key):
				new = self.inverse[key]
			else:
				new = bitset.empty(self.cpt)
			new.append(key in document.inverse)
			self.inverse[key] = new
		self.cpt += 1
		return self.cpt -1
	def get(self, key, value):
		"A simple query for a key=value"
		return self.inverse["%s:%s" % (key, value)]
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

class Document:
	def __init__(self, id = None):
		self.id = id
		self.data = {}
		self.inverse = []
	def set(self, key, value, inverse=True, store=True, filter = _filter.lower, lotOfValues=False):
		if filter != None:
			value = filter(value)
		if '__iter__' in dir(value):
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
			self.inverse.append("%s:%s" % (key, value))
	def __setitem__(self, key, value):
		self.set(key, value, True, True)
	def __getitem__(self, key):
		return self.data[key]
	def __repr__(self):
		return "<Document #%s %s %s>" % (self.id, self.data, self.inverse)

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
	class DocumentTest(unittest.TestCase):
		def setUp(self):
			self.l = Library('/tmp/index.test', True)
			for data in datas:
				d = Document()
				for k,v in data.iteritems():
					d[k] = v
				#print d
				self.l.append(d)
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
