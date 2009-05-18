__doc__ = """
Stolen from http://code.google.com/p/python-browscap/
and http://browsers.garykeith.com/
"""
__author__ = "Mathieu Lecarme <mathieu@garambrogne.net>"

from ConfigParser import ConfigParser

__all__ = ['UserAgent']

_trad = {
	"unknown": None,
	"false": False,
	"true": True
}

class UserAgent:
	def __init__(self, path='php_browscap.ini'):
		self.config = ConfigParser()
		self.config.readfp(open(path))
		# Remove meta sections
		self.default = self.__parseSection("DefaultProperties")
		self.config.remove_section("DefaultProperties")
		self.config.remove_section("GJK_Browscap_Version")
		self.agents = {}
		for section in self.config.sections():
			self.agents[section] = self.__parseSection(section)
	def __parseSection(self, section):
		global _trad
		dic = {}
		for option in self.config.options(section):
			opt = self.config.get(section, option)
			if _trad.has_key(opt):
				opt = _trad[opt]
			try:
				opt = int(opt)
			except:
				pass
			dic[option] = opt
		return dic

if __name__ == '__main__':
	u = UserAgent()
	print u.default
	print u.agents