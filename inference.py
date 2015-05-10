import numpy
import graph
from randomnames import RandomNames
from itertools import combinations
from itertools import product
from itertools import chain
from collections import Counter

# Higher margin => more edges
INDEPENDENT_MARGIN = 0.01

nameGen = RandomNames()

truth = graph.generateDAG(15, 0.3, nameGen.getRandomName)
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
	controlData = truth.generateDataPoints(100000)
	controlTable = numpy.ones(tuple(2 for _ in xrange(len(model.getNodes()))), numpy.int32)
	counts = Counter(tuple(x) for x in controlData)
	for key in counts:
		controlTable[key] += counts[key]
	print controlTable
	separators = {}
	for (a, b) in combinations(xrange(len(model.getNodes())), 2):
		separator = findSeparatingSet(controlData, a, b)
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

def independent(data, varA, varB, conditions):
	# P(varA and varB | conditions) == P(varA | conditions)P(varB | conditions)
	# TODO: this is really inefficient, and the reason the program is slow
	conditions = list(conditions)
	maxDifference = 0
	for aVal in [0,1]:
		for bVal in [0,1]:
			for condVals in product([0,1], repeat=len(conditions)):
				matchCount = 2
				aCount = 1
				bCount = 1
				bothCount = 1
				for datum in data:
					if tuple(datum[conditions]) == condVals:
						matchCount += 1
						if datum[varA] == aVal:
							aCount += 1
						if datum[varB] == bVal:
							bCount += 1
						if datum[varA] == aVal and datum[varB] == bVal:
							bothCount += 1
				aProb = float(aCount) / matchCount
				bProb = float(bCount) / matchCount
				bothProb = float(bothCount) / matchCount
				abProb = aProb * bProb
				difference = abs(bothProb - abProb)
				maxDifference = max(maxDifference, difference)
				if difference > INDEPENDENT_MARGIN:
					return False
	print "    INDEPENDENT! %s (%f)" % (conditions, maxDifference)
	return True

ICStar(model, truth)
