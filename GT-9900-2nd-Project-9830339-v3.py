# I represent a n-vert graph as 2-d matrix
# N=n+1 :
# cell[i,j]=_E_NOT          means v[i] and v[j] are not adjacent
# cell[i,j]=_E_UNC          means v[i] and v[j] are adjacent (no data about color = uncolored)
# cell[i,j]=num in [0,N)    means edge i-j has color num
# max color count is n+1 colors but if I implement the paper correctly it must bound to [Delta,Delta+1]

_E_NOT = None  # not connected edge
_E_UNC = -1  # uncolored
_DEBUG = None


def printGraph(graph, title=None):
	""" Print given graph in a readable form for debug purpose """
	n = len(graph)
	print()
	if title:
		print(title)
	print('', end='\t')
	for colI in range(n):
		print(f'v{colI}', end='\t')
	print()
	for rowI, row in enumerate(graph):
		print(f'v{rowI}', end='\t')
		for cell in row:
			print('-' if cell is _E_NOT else '#' if cell is _E_UNC else f'c{cell}', end='\t')
		print()
	print()


def graphFrom(vertCount, edgeCount, edges):
	""" create instance of problem's graph DS from given edges , edges may include color data """
	graph: list = [[_E_NOT for _ in range(vertCount)] for _ in range(vertCount)]
	for i in range(edgeCount):
		v1, v2, color, *_ = list(edges[i]) + [_E_UNC]
		graph[v1][v2] = graph[v2][v1] = color
	return graph


def constructStandardGraph():
	""" create instance of problem's graph from standard input pattern """
	vertCount, edgeCount, *_ = [int(it) for it in (input().split(' '))]
	edges = [[int(it) for it in (input().split(' '))] for _ in range(edgeCount)]
	return graphFrom(vertCount, edgeCount, edges)


def getGraphDelta(graph):
	""" calculates given graph's Delta (max degree)"""
	D = 0
	for r, _ in enumerate(graph):
		deg = 0
		for c, _ in enumerate(graph):
			if graph[r][c] is not _E_NOT:
				deg += 1
		D = max(D, deg)
	return D


def getGraphEdges(graph):
	""" returns all vertex pair (both dir) for every edge in given graph """
	return [(u, v) for (u, vert) in enumerate(graph) for (v, edge) in enumerate(vert) if edge is not _E_NOT]


def getGraphColors(graph):
	""" returns all distinct colors used for all edges of given graph """
	return set([edge for vert in graph for edge in vert if edge is not _E_NOT])


def printStandardGraph(graph):
	""" outputs standard graph color set """
	vertCount = len(graph)
	# edgeCount = sum([1 for vert in graph for edge in vert if edge is not _E_NOT]) // 2
	# colors = set([edge for vert in graph for edge in vert if edge is not _E_NOT])
	# edgeCount = sum([1 for edge in getGraphEdges(graph)]) // 2
	colorCount = len(getGraphColors(graph))
	delta = getGraphDelta(graph)

	# print(f"{vertCount} {edgeCount} {colorCount}")
	print(f"{delta} {colorCount}")
	for v in range(vertCount):
		for u in range(v + 1, vertCount):
			if graph[v][u] is not _E_NOT:
				print(f"{v} {u} {graph[v][u]+1}")


def clearGraph(graph):
	"""	clear all color settings from graph	"""
	for r, _ in enumerate(graph):
		for c, _ in enumerate(graph):
			if graph[r][c] is not _E_NOT:
				graph[r][c] = _E_UNC


def isGraphValid(graph, noUnColored=True):
	""" check validity of given graph """
	for v, _ in enumerate(graph):
		adjs = adjacentOf(graph, v)
		for x in adjs:
			if noUnColored and graph[v][x] is _E_UNC: return False  # contains uncolored edges
			for y in adjs:
				if x != y and graph[v][x] == graph[v][y]: return False  # same adj-edge color
	return True


def adjacentOf(graph, v):
	""" get children/adjacent/neighbour s of v """
	return [u for u, c in enumerate(graph[v]) if c is not _E_NOT]


def freeColorsOf(graph, v, exclude=None):
	""" returns free colors (no edge with this color on this vert) on given vertex """
	N = len(graph) + 1
	# adjs = list(adjacentOf(graph, v))
	# adjColors = [graph[v][u] for u in adjs if (graph[v][u] is not _E_NOT and graph[v][u] is not _E_UNC)]
	# return [color for color in range(N) if color not in adjColors and (not exclude or color not in exclude)]

	# edges:=graph[v] here is a 1-d array contains:
	#   None as no edge
	#   True as uncolored edge
	#   a number as already edge colored as number
	#   so a free color is which is not in this 1-d edges array
	return [color for color in range(N) if (color not in graph[v]) and ((not exclude) or (color not in exclude))]


def getFirstFromB(graph, X, F):
	""" returns first edge suitable in B set described in article """
	freeColors = freeColorsOf(graph, F[-1])
	for v, c in enumerate(graph[X]):
		if c is _E_NOT: continue  # Xv is not edge
		if c is _E_UNC: continue  # Xv is uncolored
		if v in F: continue  # already exists in F
		if c not in freeColors: continue  # u+ color is not free at u
		return v
	return None


def maximalFanOf(graph, X, f=None):
	"""	calculate Maximal Fan of X based on given algorithm, X-f edge must be uncolored	"""
	# find f if not provided
	if f is None:
		for v, c in enumerate(graph[X]):
			if c is _E_UNC:  # edge exists but not colored
				f = v
				break

	# cannot construct fan , no uncolored X-f edge exists
	if f is None:
		return None

	F = [f]
	while (v := getFirstFromB(graph, X, F)) is not None:  # until v is not exists in B
		F.append(v)  # F <- F cat v
	return F


def getCDPathOf(graph, X, c, d):
	"""
	graph colors are valid so adjs of any u only have c or d or none
	no two adjs can use same color
	X is free on c so we search for d and swap each step
	X is an endpoint of cd-path of X so we start at X and finish on last c|d edge
	"""

	path = []
	nextV = X  # start node

	while (cur := nextV) is not None:
		path.append(cur)
		nextV = None
		for v in adjacentOf(graph, cur):
			if graph[cur][v] == d:
				nextV = v
				break
		d, c = c, d

	return path


def invertCDPathOf(graph, X, c, d):
	""" invert c<=>d colors in cd-path """
	path = getCDPathOf(graph, X, c, d)
	if _DEBUG: print(f"cd-path of {X=}: {c=} {d=} {path=}")
	for i in range(1, len(path)):
		u, v = path[i - 1], path[i]
		if graph[u][v] == c:
			graph[u][v] = graph[v][u] = d
		else:
			graph[u][v] = graph[v][u] = c


def rotateFan(graph, X, F):
	""" shift colors from X to l to make color at l free to use at X """
	colors = [graph[X][v] for v in F]
	colors.append(colors.pop(0))  # left shift colors
	# colors.insert(0, colors.pop())  # right shift colors # * NOT CORRECT *
	for i, v in enumerate(F):
		graph[X][v] = graph[v][X] = colors[i]


def colorGraph(graph):
	""" generates valid N-edge-color for given graph which N=n+1 colors from [0:N) """
	n = len(graph)
	N = n + 1

	# first clear all colors
	clearGraph(graph)

	if _DEBUG: print()
	for X, _ in enumerate(graph):
		if _DEBUG: print()
		changed = True
		while changed:  # max loop count is num of adjs
			changed = False
			if _DEBUG: printGraph(graph, f"on {X=}")

			F = maximalFanOf(graph, X)  # F=<f,l>
			if _DEBUG: print(f"Fan on {X=}: ", F)

			if not F:
				continue

			f = F[0]
			l = F[-1]
			l_freeColors = freeColorsOf(graph, l)  # I pick l first from smallest color, because it may add new color to graph
			d = l_freeColors[0]  # or random, if I choose new colors, graph may contains more than D+1 colors
			X_freeColors = freeColorsOf(graph, X, [d])  # except color d already picked , it has grantee that X has free color
			c = X_freeColors[0]  # or random , again smaller colors (which may already picked up) to prevent new colors
			if _DEBUG: print(f"on {X=}: {f=} {l=} {c=} {d=}")

			invertCDPathOf(graph, X, c, d)
			changed = True  # on every change I declare it to prevent later code edits lost their path
			if _DEBUG: printGraph(graph, f"inverted cd-path {X=}")

			# find first w
			wPos, w = None, None
			for vPos, v in enumerate(F):
				if d in freeColorsOf(graph, v):
					wPos, w = vPos, v
					break
			if w is None:
				# impossible to reach here
				continue

			# subFan= <f,l> ^ <f,w> = <f,w>
			subFan = F[:wPos + 1]
			if _DEBUG: print(f"on {X=}: {w=} subFan=", subFan)

			rotateFan(graph, X, subFan)
			graph[X][w] = graph[w][X] = d
			changed = True

	return graph


if __name__ == '__main__':
	# # Kn graph
	# n = 10
	# G = [[_E_UNC if u != v else _E_NOT for u in range(n)] for v in range(n)]

	# G = [  # Fig-6.1
	# 	[_E_NOT, _E_UNC, _E_UNC, _E_UNC, _E_NOT],
	# 	[_E_UNC, _E_NOT, _E_UNC, _E_NOT, _E_UNC],
	# 	[_E_UNC, _E_UNC, _E_NOT, _E_UNC, _E_NOT],
	# 	[_E_UNC, _E_NOT, _E_UNC, _E_NOT, _E_UNC],
	# 	[_E_NOT, _E_UNC, _E_NOT, _E_UNC, _E_NOT],
	# ]

	# # Fig-6.5
	# G = graphFrom(9, 10, [(0, 4), (0, 6), (0, 7), (1, 5), (1, 7), (2, 5), (2, 6), (2, 7), (3, 7), (3, 8)])

	# # a complete bipartite graph
	# G = graphFrom(6, 9, [(0, 1), (0, 3), (0, 5), (1, 2), (1, 4), (2, 3), (2, 5), (3, 4), (4, 5)])

	# # Project Example graph
	# G = graphFrom(5, 7, [(0, 1), (0, 3), (1, 2), (1, 4), (2, 3), (2, 4), (3, 4)])

	# # create graph from input
	G = constructStandardGraph()

	# printGraph(G)
	colorGraph(G)
	# printGraph(G)
	# print("isValid: ", isGraphValid(G))
	printStandardGraph(G)
