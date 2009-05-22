class Library:
	def __init__(self):
		self.cpt = 0
		self.store = {}
	def newDocument(self):
		self.cpt += 1
		return Document(self, self.cpt)

class Document:
	def __init__(self, library, id):
		self.library = library
		self.id = id
		self.keys = {}
	def __setitem__(self, key, value):
		if '__iter__' in dir(value):
			for v in value:
				self[key] = v
			return
		if key not in self.keys:
			self.keys[key] = set()
		self.keys[key].add(value)
		kk = "%s:%s" % (key, value)
		if kk not in self.library.store:
			self.library.store[kk] = set()
		self.library.store[kk].add(self.id)

if __name__ == '__main__':
	l = Library()
	datas = [
		{'nom': 'Bob',
		'score': 2},
		{'nom': 'Casimir',
		'score' : 42,
		'tags' : ['simple', 'monster']},
		{'nom': 'Andre',
		'score': 42}
	]
	for data in datas:
		d = l.newDocument()
		for k,v in data.iteritems():
			d[k] = v
	print l.store
