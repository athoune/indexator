__doc__ = """
Stolen from http://code.google.com/p/python-browscap/
and http://browsers.garykeith.com/
"""
__author__ = "Mathieu Lecarme <mathieu@garambrogne.net>"

import codecs
import fnmatch
import time
import os.path

__all__ = ['UserAgent']

_trad = {
	"unknown": None,
	"false": False,
	"true": True
}

class UserAgent:
	def __init__(self, path=os.path.dirname(__file__) + '/php_browscap.ini'):
		chrono = time.time()
		global _trad
		self.default = {}
		self.agents = {}
		self.sections = []
		bof = ['GJK_Browscap_Version']
		f = codecs.open(path, encoding='latin1')
		section = None
		for l in f:
			line = l.strip()
			if line == '' or line[0] == ';' : continue
			if line[0] == '[':
				section = line[1:-1]
				self.sections.append(section)
				continue
			if section in bof: continue
			poz = line.find('=')
			if poz == -1: continue #weird
			key = line[:poz]
			value = line[poz+1:]
			if _trad.has_key(value):
				value = _trad[value]
			else:
				try:
					value = int(value)
				except:
					pass
			if section == 'DefaultProperties':
				self.default[key] = value
			else:
				if not self.agents.has_key(section):
					self.agents[section] = {}
				self.agents[section][key] = value
				if key == 'Parent' and self.agents.has_key(value):
					for (k,v) in self.agents[value].iteritems():
						if not self.agents[section].has_key(k):
							self.agents[section][k] = v
		self.chrono = time.time() - chrono
	def match(self, agent):
		for section in self.sections:
			if fnmatch.fnmatch(agent, section):
				return self.agents[section]
		return None

if __name__ == '__main__':
	u = UserAgent()
	print u.chrono
	#print u.default
	#print u.agents
	#print u.sections
	agents = [
		'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
		'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)',
		'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; .NET CLR 1.1.4322)',
		'Mozilla/5.0 (compatible; Yoono; http://www.yoono.com/)',
		'Mozilla/5.0 (compatible; Yahoo! Slurp; http://help.yahoo.com/help/us/ysearch/slurp)',
		'Mozilla/5.0 (X11; U; Linux i686; fr; rv:1.8.1) Gecko/20061010 Firefox/2.0'
	]
	for agent in agents:
		print u.match(agent)
	