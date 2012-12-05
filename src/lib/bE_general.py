# -*- coding: utf-8 -*-

# ==================================================================
# ==================================================================
#   buildingEngine utitlity functions
# ==================================================================
# ==================================================================

buildingEngineNames = ["Comp", "CompSelector", "Subdiv", "Repeat", "Insert", "Extrude", "CreateBase", "Roof", "Trans","Exception"]
buildingEngineInsertNames = ["Insert","InsertTex"]

# ==================================================================
#   is_bE_node utitlity function to check whether node is bE or not
# ==================================================================
def is_bE_node(node):
	if node:
		return (node.type().name() in buildingEngineNames)
	else:
		return False

# ==================================================================
#   is_Insert_node utitlity function to check whether node is bE or not
# ==================================================================
def is_Insert_node(node):
	if node:
		return (node.type().name() in buildingEngineInsertNames)
	else:
		return False

# ==================================================================
#   utitlity functions to manipulate/check bE node products
# ==================================================================
def numProds(node):
	counter = 1
	if node.type().name() == 'Comp':
		counter = node.parm('components').eval()
	elif node.type().name() == 'Subdiv':
		counter = node.parm('Divisions').eval()
	elif node.type().name() == 'Filter' or node.type().name() == 'Exception' or node.type().name() == 'CompSelector':
		counter = 2
	return counter

def products(node):
	prods = []
	if is_bE_node(node):
		counter = numProds(node)
		for s in range(counter):
			nProd = node.parm('product'+str(s)).evalAsString()
			prods.append(nProd)
	return prods

def isEffectivelyUsedProduct(container, node, prod):
	import houIterators
	if is_bE_node(node):
		it = houIterators.depthFirstSearchIterator(houIterators.descendingConnexion(), container, [node], preorder = True)
		for depth, i in it.navigate():
			if is_bE_node(i):
				fils = filters(i)
				if prod in fils:
					return True
	return False

def effectivelyUsedProducts(container, node):
	finalProducts = []
	if is_bE_node(node):
		allProducts = products(node)
		for prod in allProducts:
			if isEffectivelyUsedProduct(container, node, prod):
				finalProducts.append(prod)
		print "Effectively used products for", node, "=", finalProducts, "(From ", allProducts, ")"
	return finalProducts

# ==================================================================
#   utitlity functions to manipulate/check bE node filters
# ==================================================================
def numFilters(node):
	value = 0
	if is_bE_node(node):
		value = len(node.parm('filter').evalAsString().split(' '))
	return value

def filters(node):
	value = []
	if is_bE_node(node):
		value = node.parm('filter').evalAsString().split(' ')
	while '' in value:
		#if someone left blank spaces, we need to remove them!
		value.remove('')
	return value

def isEffectiveFilter(container, node, filter):
	import houIterators
	if is_bE_node(node):
		it = houIterators.depthFirstSearchIterator(houIterators.ascendingConnexion(), container, [node], preorder = True)
		for depth, i in it.navigate():
			if is_bE_node(i):
				if filter.startswith(i.name()+'__'):
					return True
				else:
					prods = products(i)
					#print "navigating", i, ": ", prods, " - ", filter
					if filter in prods:
						return True
	return False

def effectiveFilters(container, node):
	finalFilters = []
	if is_bE_node(node):
		allFilters = filters(node)
		for f in allFilters:
			if isEffectiveFilter(container, node, f):
				finalFilters.append(f)
		#print "Effective filters for", node, "=", finalFilters, "(From ", allFilters, ")"
	return finalFilters
