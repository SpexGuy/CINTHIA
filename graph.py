from random import random

class DirectedNode:
	def __init__(self, idx, name):
		self._parents = []
		self._children = []
		self._name = name
		self._idx = idx

	def addParent(self, node):
		self._parents.append(node)

	def addChild(self, node):
		self._children.append(node)

	def linkChild(self, node):
		self.addChild(node)
		node.addParent(self)

	def getChildren(self):
		return self._children

	def getName(self):
		return self._name

	def getIndex(self):
		return self._idx

class Graph:
	def __init__(self, nodes=None):
		if (nodes is None):
			nodes = []
		self._nodes = nodes

	def getNodes(self):
		return self._nodes

	def writeDOT(self, filename):
		dot = open(filename, 'w')
		dot.write('digraph {\n')
		for node in self._nodes:
			dot.write('    N%d [label="%s"]\n' % (node.getIndex(), node.getName()))

		for node in self._nodes:
			for child in node.getChildren():
				dot.write('    N%d -> N%d\n' % (node.getIndex(), child.getIndex()))

		dot.write('}\n')
		dot.close()

def generateDAG(numNodes, edgeProbability, generateName):
	nodes = [DirectedNode(n, generateName()) for n in xrange(numNodes)]
	for i in xrange(numNodes-1):
		for j in xrange(i+1, numNodes):
			if (random() < edgeProbability):
				nodes[i].linkChild(nodes[j])
	return Graph(nodes)

