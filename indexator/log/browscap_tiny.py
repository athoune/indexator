__doc__ = """
Stolen from http://code.google.com/p/python-browscap/
and http://browsers.garykeith.com/
"""
__author__ = "Mathieu Lecarme <mathieu@garambrogne.net>"

import codecs

__all__ = ['UserAgent']

_trad = {
	"unknown": None,
	"false": False,
	"true": True
}

class UserAgent:
	def __init__(self, path='php_browscap.ini'):
		global _trad
		#self.config = ConfigParser()
		#self.config.readfp(open(path))
		# Remove meta sections
		self.default = {}
		#self.default = self.__parseSection("DefaultProperties")
		#self.config.remove_section("DefaultProperties")
		#self.config.remove_section("GJK_Browscap_Version")
		self.agents = {}
		bof = ['GJK_Browscap_Version', '*']
		#for section in self.config.sections():
		#	self.agents[section] = self.__parseSection(section)
		f = codecs.open(path, encoding='latin1')
		section = None
		for l in f:
			line = l.strip()
			if line == '' or line[0] == ';' : continue
			if line[0] == '[':
				section = line[1:-1]
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

if __name__ == '__main__':
	u = UserAgent()
	print u.default
	print u.agents