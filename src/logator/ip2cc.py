#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3

def ip2long(ip):
    """
    Convert a IPv4 address into a 32-bit integer.
    
    @param ip: quad-dotted IPv4 address
    @type ip: str
    @return: network byte order 32-bit integer
    @rtype: int
    """
    ip_array = ip.split('.')
    ip_long = int(ip_array[0]) * 16777216 + int(ip_array[1]) * 65536 + int(ip_array[2]) * 256 + int(ip_array[3])
    return ip_long

def _clean(txt):
	return txt[1:-1]

class IP2CC(object):
	def __init__(self, dbname='ip'):
		self.db = sqlite3.connect("%s.db" % dbname)
		self.cursor = self.db.cursor()
	def feed(self, csv):
		self.cursor.execute('CREATE TABLE ip (start NUMERIC, end NUMERIC, country TEXT)')
		self.cursor.execute('CREATE INDEX idx_start ON ip(start)')
		for line in file(csv, 'r'):
			l = line[:-2].split(',')
			print _clean(l[-1])
			self.cursor.execute("INSERT INTO ip VALUES (?,?, ?)", (long(_clean(l[0])), long(_clean(l[1])), _clean(l[-1]) ))
		self.db.commit()
	def where(self, ip):
		l = ip2long(ip)
		self.cursor.execute("SELECT country FROM ip WHERE start <= ? AND end >= ?", (l,l))
		return self.cursor.fetchone()[0]

import pytc

class IP2CC_tc(object):
	def __init__(self, dbname='ip'):
		self.dbname = "%s.bdb" % dbname
		self.db = pytc.BDB()
		try:
			self.db.open(self.dbname, pytc.BDBOREADER)
		except pytc.Error:
			pass
	def feed(self, csv):
		self.db.open(self.dbname, pytc.BDBOWRITER | pytc.BDBOCREAT)
		for line in file(csv, 'r'):
			l = line[:-2].split(',')
			print _clean(l[-1])
			self.db.putlist(_clean(l[1]), [_clean(l[0]), _clean(l[2]), _clean(l[3]), _clean(l[4])])
		self.db.optimize(2, 4, 19, 4, 5, pytc.BDBTTCBS)
		self.db.close()
		self.db.open(self.dbname, pytc.BDBOREADER)
	def where(self, ip):
		l = ip2long(ip)
		bloc = self.db.range(str(l), True, None, False, 1)[0]
		if bloc == None: return None
		data = self.db.getlist(bloc)
		if str(l) > data[0] : return data[1:]
		return None
	
if __name__ == '__main__':
	import sys
	ip2cc = IP2CC_tc()
	if len(sys.argv) > 1:
		print ip2cc.where(sys.argv[1])
	else:
		ip2cc.feed('ip-to-country.csv')