import unittest

from indexator.document import Library, Document

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

class LibraryTest(unittest.TestCase):
	def testReadWrite(self):
		library = Library('/tmp/index_rw', 'w')
		self.assertEquals(0, len(library))
		doc = Document(name='Bob', score=42)
		library.append(doc)
		library.warmup()
		library.close()
		libRead = Library('/tmp/index_rw', 'r')
		self.assertEquals(1, len(libRead))
		self.assertEquals('bob', libRead.store[0]['name'])
		self.assertEquals(set([0]), libRead.get('name', 'bob').results())
		#self.assertEquals(0, libRead.oups)
	def _testMulti(self):
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
			pass
			#print document
		self.assertEquals(1, b.cardinality())
		self.assertEquals(set([1]), b.results())
		for doc in self.l.documents(b):
			self.assertEquals('casimir',doc['nom'])

if __name__ == '__main__':
	unittest.main()
