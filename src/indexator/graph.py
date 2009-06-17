#!/usr/bin/env python
# -*- coding: utf-8 -*-

__doc__ = """
HTML and Javascript graph simple abstraction
"""

class Document:
	"An HTML page"
	def __init__(self, title = 'Graph'):
		self.title = title
		self.graph = []
	def add(self, graph):
		self.graph.append(graph)
	def __str__(self):
		header = '''
		<html>
		<head>
		<title>{title}</title>
		<script type="text/javascript" 
		        src="http://www.google.com/jsapi"></script>
		<script type="text/javascript">
		  google.load("jquery", "1.3");
		</script>
		<script language="javascript" type="text/javascript" src="http://people.iola.dk/olau/flot/jquery.flot.js"></script>
		<body>
		<h1>{title}</h1>
		'''.format(title=self.title)
		footer = '''
		</body>
		</html>
		'''
		buffer = header
		for g in self.graph:
			buffer += str(g)
		return buffer + footer
	def save(self, name):
		f = open(name, 'w')
		f.write(str(self))
		f.close()
cpt = 0

class Graph:
	"A graph"
	def __init__(self, title= "A cute graph", width=600, height=300):
		global cpt
		cpt+=1
		self.id = cpt
		self.buffer = """
		<h2>{title}</h2>
		<div id="plot-{id}" style="width:600px;height:300px"></div>
		""".format(id=self.id, title = title)
		self.datas = []
	def plot(self, data):
		self.datas.append(data)
	def __str__(self):
		self.buffer += """
		<script>
		{data}
		$.plot($('#plot-{id}'), 
		datas
		);
		</script>
		""".format(id= self.id, data= self.values())
		return self.buffer
	def values(self, var= 'datas'):
		buffer = ""
		cpt = 0;
		for data in self.datas:
			buffer = "d{n} = [".format(n=cpt)
			for point in data:
				buffer += str(point) + ", "
			buffer += "];\n"
			cpt += 1
		buffer += "var {var} = [".format(var = var)
		for a in range(cpt):
			buffer += "d{a}, ".format(a=a)
		buffer += "];"
		return buffer

if __name__ == '__main__':
	g = Graph()
	g.plot({1:2, 2:3})
	d = Document(title="Beuha")
	d.add(g)
	d.save('/tmp/test.html')
