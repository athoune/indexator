#!/usr/bin/env python
# -*- coding: utf-8 -*-

__doc__ = """
"""
__author__ = "Mathieu Lecarme <mathieu@garambrogne.net>"

from indexator.log.apache import Combined
from indexator.document import Library, Document
import indexator.graph as graph
import sys
import time
import cProfile
import pstats

from optparse import OptionParser

def parse(log, size):
	c = Combined()
	f = file(log, 'r')
	cpt = 0
	chrono = time.time()
	scores = []
	for line in f:
		cpt += 1
		log = c.parse(line)
		d = Document()
		d['code'] = log['code']
		d['command'] = log['command']
		d['crawler'] = log['user-agent'].get('Crawler', False)
		if not d['crawler']:
			d['plateform'] = log['user-agent'].get('Platform', 'unknown')
			d['browser'] = log['user-agent']['Browser']
			d['version'] = log['user-agent'].get('MajorVer', 0)
		library.append(d)
		if cpt % 100 == 0:
			print cpt, cpt / (time.time() - chrono)
			scores.append([cpt, cpt / (time.time() - chrono)])
		if cpt == size:
			break
	d = graph.Document("Parsing")
	g = graph.Graph("speed/size")
	g.plot(scores)
	d.add(g)
	d.save("bench-parsing.html")

def showall(size):
	chrono = time.time()
	cpt = 0
	for field in library.fields():
		print field
		for plateform in library.fields()[field]:
			score = None
			for a in range(1000):
				score = library.query(field, plateform).cardinality()
				cpt += 1
			print "\t", plateform,  score/ (size / 100.0)
	print cpt / (time.time() - chrono), 'query/s'

def query(size):
	chrono = time.time()
	cpt = 0
	for a in range(1000):
		bit = library.query('plateform', 'winxp') & library.query('code', '200') & library.query('browser', 'firefox')
		cpt += 1
	print bit.cardinality()
	print cpt / (time.time() - chrono), 'query/s'

parser = OptionParser()
parser.add_option("-l", "--log", dest="log", help="apache combined log file")
parser.add_option("-n", "--size", dest="size", help="number of parsed lines", type="int", default=10000)
parser.add_option("-S", "--stat", dest="stat", help="number of parsed lines")
actions = ['showall', 'query']
parser.add_option("-a", "--action", dest="action", help="actions : " + str(actions))


(options, args) = parser.parse_args()

if options.log != None:
	library = Library('/tmp/apache.test', True)
	cProfile.run('parse(options.log, options.size)', 'parse.prof')
if options.action != None:
	if options.action in actions:
		library = Library('/tmp/apache.test', False)
		cProfile.run(options.action + '(options.size)', options.action + '.prof')
	else:
		print "action must be choose in " + str(actions)

if options.stat != None:
	p = pstats.Stats(options.stat)
	p.sort_stats('cumulative').print_stats(50)
