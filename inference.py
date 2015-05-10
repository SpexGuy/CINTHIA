import numpy
import graph
from randomnames import RandomNames
from itertools import combinations
from itertools import product
from itertools import chain
from collections import Counter
from math import log

# Higher margin => more edges
INDEPENDENT_MARGIN = 0.01

nameGen = RandomNames()

truth = graph.generateDAG(10, 0.3, nameGen.getRandomName)
#truth = graph.Graph([graph.DirectedNode(n, nameGen.getRandomName()) for n in xrange(5)])
#truth.addEdge(0,1)
#truth.addEdge(0,2)
#truth.addEdge(1,3)
#truth.addEdge(2,3)
#truth.addEdge(3,4)
#truth.makeGenerative()
truth.writeDOT('truth.dot')

model = truth.copyNodes()

def ICStar(model, truth):
	print 'Generating data...'
	controlData = truth.generateDataPoints(100000)
	controlTable = numpy.ones(tuple(2 for _ in xrange(len(model.getNodes()))), numpy.int32)
	counts = Counter(tuple(x) for x in controlData)
	for key in counts:
		controlTable[key] += counts[key]
	#print controlTable
	print 'Done!'

	separators = {}
	for (a, b) in combinations(xrange(len(model.getNodes())), 2):
		separator = findSeparatingSet(controlTable, a, b)
		if separator is None:
			model.addEdge(a, b, graph.RELATED_SOMEHOW)
		else:
			separators[(a,b)] = separator

	model.writeDOT('model1.dot')
	
	nodeNeighbors = model.findNonadjacentNeighbors()
	for (nodes, neighbor) in nodeNeighbors:
		if nodes in separators:
			if neighbor in separators[nodes]:
				print "Trig! %s" % (str((nodes, neighbor)),)
				model.getEdge(nodes[0], neighbor).forwardFrom(nodes[0], graph.UNCERTAIN)
				model.getEdge(nodes[1], neighbor).forwardFrom(nodes[1], graph.UNCERTAIN)

	model.writeDOT('model2.dot')
	
	changed = True
	while changed:
		while changed:
			changed = False
			for (nodes, neighbor) in nodeNeighbors:
				edge0 = model.getEdge(nodes[0], neighbor)
				edge1 = model.getEdge(nodes[1], neighbor)
				if not edge0.isUndirected() and edge0.getEnd().getIndex() == neighbor and edge1.getType() == graph.RELATED_SOMEHOW:
					edge1.forwardFrom(neighbor, graph.CERTAIN)
					changed = True
				elif not edge1.isUndirected() and edge1.getEnd().getIndex() == neighbor and edge0.getType() == graph.RELATED_SOMEHOW:
					edge0.forwardFrom(neighbor, graph.CERTAIN)
					changed = True

		#TODO: rule 2

	model.writeDOT('model3.dot')

def findSeparatingSet(data, a, b):
	print "Investigating (%d, %d) " % (a, b)
	for conds in powerset(filter(lambda x: x != a and x != b, xrange(len(model.getNodes())))):
		if independent(data, a, b, conds):
			return conds
	print "    DEPENDENT!"
	return None

def powerset(iterable):
    "powerset([1,2,3]) --> (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(1, len(s)+1))

LN_2 = log(2)
def log2(x):
	return log(x)/LN_2

def gSquared(data, varA, varB, conditions):
	# G = 2 * N * H(a | s) + H(b | s) - H(a,b | s)
	indexes = sorted((varA, varB) + conditions)
	indexA = indexes.index(varA)
	indexB = indexes.index(varB)
	sumAxes = [x for x in xrange(len(data.shape)) if not x in indexes]
	#print "    Testing %d and %d given %s, omit %s" % (varA, varB, str(conditions), str(sumAxes))
	# sum from right to left to avoid moving index problems
	absData = data
	for axis in reversed(sumAxes):
		absData = numpy.sum(absData, axis)
	asData = numpy.sum(absData, indexB)
	bsData = numpy.sum(absData, indexA)
	sData = numpy.sum(asData, indexA)
	count = numpy.sum(sData)
#	print absData
#	print asData
#	print bsData
#	print sData
	h_a_N = 0
	h_b_N = 0
	h_ab_N = 0
	for values in product([0,1], repeat=len(indexes)):
		sCount = sData[values[:indexA]+values[indexA+1:indexB]+values[indexB+1:]]
		asCount = asData[values[:indexB]+values[indexB+1:]]
		bsCount = bsData[values[:indexA]+values[indexA+1:]]
		absCount = absData[values]
#		print sCount
#		print asCount
#		print bsCount
#		print absCount
		if asCount > 0:
			h_a_N += float(asCount)/count * log2(float(sCount)/asCount)
		if bsCount > 0:
			h_b_N += float(bsCount)/count * log2(float(sCount)/bsCount)
		if absCount > 0:
			h_ab_N += float(absCount)/count * log2(float(sCount)/absCount)

	return 2 * (h_a_N + h_b_N - h_ab_N)
		

def independent(data, varA, varB, conditions):
	# P(varA and varB | conditions) == P(varA | conditions)P(varB | conditions)
	# TODO: this is really inefficient, and the reason the program is slow
	gsq = gSquared(data, varA, varB, conditions)
	#print "Gsq(%d %d | %s) = %f" % (varA, varB, str(conditions), gsq)
	if abs(gsq) < 2.8:
		print "    INDEPENDENT! %s (%f)" % (conditions, gsq)
		return True
	return False

ICStar(model, truth)
