from random import random
import numpy

# Edge types
RELATED_SOMEHOW = 0
LATENT_CERTAIN  = 1
REVERSE_MAYBE   = 2
REVERSE_CERTAIN = 3
FORWARD_MAYBE   = 4
FORWARD_CERTAIN = 5

UNDIRECTED = 0
REVERSE = 1
FORWARD = 2

UNCERTAIN = 0
CERTAIN = 1

attributes = {
	FORWARD_CERTAIN: '[dir=forward][label="*"]',
	FORWARD_MAYBE:   '[dir=forward]',
	LATENT_CERTAIN:  '[dir=both]',
	RELATED_SOMEHOW: '[dir=none]',
	REVERSE_MAYBE:   '[dir=back]',
	REVERSE_CERTAIN: '[dir=back][label="*"]'
}

class Edge:
	def __init__(self, src, dest, edgeType):
		self._src = src
		self._dest = dest
		self._type = edgeType
		src._addEdge(self)
		dest._addEdge(self)

	def mayStartWith(self, node):
		return (node is self._src) if self.isForward() else (node is self._dest) if self.isReverse() else (node is self._src or node is self._dest)

	def mayEndWith(self, node):
		return (node is self._dest) if self.isForward() else (node is self._src) if self.isReverse() else (node is self._src or node is self._dest)

	def otherEnd(self, known):
		if known is self._src:
			return self._dest
		assert(known is self._dest)
		return self._src

	def isForward(self):
		return (self._type // 2) == FORWARD

	def isReverse(self):
		return (self._type // 2) == REVERSE

	def isCertain(self):
		return (self._type % 2) == CERTAIN

	def getDOTString(self):
		return '    N%d -> N%d %s\n' % (self._src.getIndex(), self._dest.getIndex(), attributes[self._type])


class DirectedNode:
	def __init__(self, idx, name):
		self._edges = []
		self._name = name
		self._idx = idx

	def _addEdge(self, edge):
		self._edges.append(edge)

	def getName(self):
		return self._name

	def getIndex(self):
		return self._idx

	def genSetup(self):
		self._condSize = tuple(2 for edge in self._edges if edge.mayEndWith(self))
		self._condProbs = numpy.random.random_sample(self._condSize)

	def generate(self, values):
		index = tuple(values[edge.otherEnd(self).getIndex()] for edge in self._edges if edge.mayEndWith(self))
		return 1 if random() < self._condProbs[index] else 0


def makeDo(probMap):
	def do(idx, node, values):
		if idx in probMap:
			return int(random() < probMap[idx])
		return node.generate(values)
	return do


class Graph:
	def __init__(self, nodes=None, edges=None):
		if nodes is None:
			nodes = []
		if edges is None:
			edges = []
		self._nodes = nodes
		self._edges = edges

	def getNodes(self):
		return self._nodes

	def getEdges(self):
		return self._edges

	def generateDataPoint(self, do=None):
		# assumes DAG node list is sorted in ascending order!!!
		if do is None:
			do = lambda idx, node, values: node.generate(values)
		values = []
		for idx, node in enumerate(self._nodes):
			values.append(do(idx, node, values))
		return numpy.array(values)

	def generateDataPoints(self, number, do=None):
		return numpy.array(list(self.generateDataPoint(do) for _ in xrange(number)))

	def writeDOT(self, filename):
		dot = open(filename, 'w')
		dot.write('digraph {\n')
		for node in self._nodes:
			dot.write('    N%d [label="%s"]\n' % (node.getIndex(), node.getName()))

		for edge in self._edges:
				dot.write(edge.getDOTString())

		dot.write('}\n')
		dot.close()

def generateDAG(numNodes, edgeProbability, generateName):
	nodes = [DirectedNode(n, generateName()) for n in xrange(numNodes)]
	edges = []
	for i in xrange(numNodes-1):
		for j in xrange(i+1, numNodes):
			if (random() < edgeProbability):
				edges.append(Edge(nodes[i], nodes[j], FORWARD_CERTAIN))

	for node in nodes:
		node.genSetup()

	return Graph(nodes, edges)

