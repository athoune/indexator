import unittest
from indexator.document import Document, Library
from indexator.parser import Query, value
from pyparsing import ParseException

class QueryTest(unittest.TestCase):
	def setUp(self):
		self.library = Library('/tmp/parser.test', 'w')
		self.library.append(Document(code="200", plateform="linux", browser="khtml"))
		self.library.append(Document(code="200", plateform="winxp", browser="ie"))
	def testSimple(self):
		query = Query('plateform:winxp')
		self.assertEquals(set([1]), value(query, self.library).results())
	def testNot(self):
		query = Query('not plateform:winxp')
		self.assertEquals(set([0]), value(query, self.library).results())
	def testOr(self):
		query = Query(' plateform:winxp or plateform:linux')
		self.assertEquals(set([0, 1]), value(query, self.library).results())
	def testDummy(self):
		query = Query('not (plateform:winxp)')
		self.assertEquals(set([0]), value(query, self.library).results())
	def testOr(self):
		try:
			query = Query(" or toto:machin")
		except ParseException:
			pass
		query = Query(' plateform:winxp or plateform:linux')
		#print query.asXML()
	def testAll(self):
		q = """
not plateform:winxp
or (
	code:200 
	and  browser:firefox
)"""
		query = Query(q)
		#print query.asXML()
		#print value(query, self.library)
		self.assertEquals(set([0]), value(query, self.library).results())

if __name__ == '__main__':
	unittest.main()
