#!/usr/bin/env python
# -*- coding: utf-8 -*-

__doc__ = """
Stolen from http://code.google.com/p/python-browscap/
and http://browsers.garykeith.com/
"""
__author__ = "Mathieu Lecarme <mathieu@garambrogne.net>"

import codecs
import fnmatch
import time
import os.path
import re

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
		self.treeSections = {}
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
			if value[0] == '"': value = value[1:]
			if value[-1] == '"': value = value[:-1]
			value = value.strip()
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
		#This trick eats some results, but, it's 50% faster
		magic = re.compile('[?*]')
		for section in self.sections:
			key = self._firstWord(magic.split(section)[0])
			if not self.treeSections.has_key(key):
				self.treeSections[key] = []
			self.treeSections[key].append(section)
		#print self.treeSections.keys()
		self.chrono = time.time() - chrono
	def _firstWord(self, txt):
		space = txt.find(' ')
		slash = txt.find('/')
		if space == -1 and slash == -1:
			return txt
		if space == -1:
			return txt[:slash]
		if slash == -1:
			return txt[:space]
		return txt[min(space, slash)]
	def match(self, agent):
		sections = self.treeSections.get(self._firstWord(agent), self.treeSections[''])
		for section in sections:
			if fnmatch.fnmatch(agent, section):
				return self.agents[section]
		return self.default

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
	