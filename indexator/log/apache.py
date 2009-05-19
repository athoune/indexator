__doc__ = """
"""
__author__ = "Mathieu Lecarme <mathieu@garambrogne.net>"

import re
from datetime import datetime
from browscap_tiny import UserAgent

RE_COMMON = re.compile('(.*?) - (.*?) \[(.*?) [+-]\d{4}\] "(.*?) (.*?) (.*?)" (\d{3}) (\d+)', re.U)
RE_COMBINED = re.compile('(.*?) - (.*?) \[(.*?) [+-]\d{4}\] "(.*?) (.*?) (.*?)" (\d{3}) (\d+) "(.*?)" "(.*?)"', re.U)
userAgent = UserAgent()

class Common:
	def parse(self, line):
		m = RE_COMMON.match(line)
		dico = {
		'ip':     m.group(1),
		'user':   m.group(2),
		'date':   datetime.strptime(m.group(3), '%d/%b/%Y:%H:%M:%S'),
		'command':m.group(4),
		'url':    m.group(5),
		'http':   m.group(6),
		'code':   int(m.group(7)),
		'size':   int(m.group(8))
		}
		return dico

class Combined:
	def parse(self, line):
		m = RE_COMBINED.match(line)
		dico = {
		'ip':     m.group(1),
		'user':   m.group(2),
		'date':   datetime.strptime(m.group(3), '%d/%b/%Y:%H:%M:%S'),
		'command':m.group(4),
		'url':    m.group(5),
		'http':   m.group(6),
		'code':   int(m.group(7)),
		'size':   int(m.group(8)),
		'referer':m.group(9),
		'user-agent':userAgent.match(m.group(10))
		}
		return dico

if __name__ == '__main__':
	import sys
	if len(sys.argv) > 1:
		c = Combined()
		f = file(sys.argv[1], 'w')
		for line in f:
			print c.parse(l)
	import unittest
	class ApacheTest(unittest.TestCase):
		def testCommon(self):
			log = '127.0.0.1 - frank [10/Oct/2000:13:55:36 -0700] "GET /apache_pb.gif HTTP/1.0" 200 2326'
			common = Common()
			print common.parse(log)
		def testCombined(self):
			log = '127.0.0.1 - frank [10/Oct/2000:13:55:36 -0700] "GET /apache_pb.gif HTTP/1.0" 200 2326 "http://www.example.com/start.html" "Mozilla/4.08 [en] (Win98; I ;Nav)"'
			common = Combined()
			print common.parse(log)
			
	unittest.main()
