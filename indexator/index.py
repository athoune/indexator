import collections

"""
[TODO] persistance
[TODO] choix du moteur, gdbm, tokyo cabinet ...
[TODO] création des index
"""
class Index(collections.Mapping):
	_data = {}
	_indexed = None
	def __init__(self, map):
		for a in map:
			self._data[a.lower()] = map[a]
	def __getitem__(self, item):
		return self._data[item.lower()]
	def __len__(self):
		return len(self._data)
	def __iter__(self):
		return self._data.__iter__()

if __name__ == '__main__':
	import unittest
	class IndexTest(unittest.TestCase):
		def setUp(self):
			pass
		def testInit(self):
			m = {'Name' : 'Bob',
			'Sexe' : True,
			'tags' : ['sponge', 'sea'],
			}
			i = Index(m)
			for k in i:
				print k

	unittest.main()