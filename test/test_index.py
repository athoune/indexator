import unittest

from indexator.index import tokyoCabinetData, tokyoCabinetSortedData, Index

class DataTest(unittest.TestCase):
	def testGetSet(self):
		for cabinet in [tokyoCabinetData, tokyoCabinetSortedData]:
			d = cabinet('/tmp/tc', 'w')
			data = [1,2,3,"a"]
			d[42] = data
			d.close()
			d = cabinet('/tmp/tc', 'r')
			self.assert_(data, d[42])
			self.assert_(1, d)
			#print d

class IndexTest(unittest.TestCase):
	def testInit(self):
		m = {'Name' : 'Bob',
		'Sexe' : True,
		'tags' : ['sponge', 'sea'],
		}
		i = Index(m)
		#for k in i:
		#	print k
	def testRange(self):
		d = tokyoCabinetSortedData('/tmp/span', 'w')
		cpt = 0
		for fruit in ['carotte', 'pomme', 'banane', 'coing']:
			d[fruit] = cpt
			cpt += 1
		self.assertEquals(['coing'], d.rangefwm('co', 50))
		self.assertEquals([], d.rangefwm('a', 50))
		self.assertEquals(['banane'], d.range('a', True, None, True, 1))
		self.assertEquals(['banane', 'carotte'], d.range('a', True, 'coing', False, 50))

if __name__ == '__main__':
	unittest.main()
