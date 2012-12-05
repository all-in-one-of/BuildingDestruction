# ==================================================
# Primitive Tree manipulation routines
# ==================================================

import sEp
import houPrimGroups
import bE_general

def userDefinedPrimGroups(prim):
	groups = houPrimGroups.primGroups(prim)
	userGroups = []
	for gr in groups:
		if "__" not in gr:
			userGroups.append(gr)
	return userGroups

def primGroupsIncludedIn(primA, primB):
	grA = houPrimGroups.primGroups(primA)
	grB = houPrimGroups.primGroups(primB)
	for gr in grA:
		if gr not in grB:
			return False
	return True

def isAncestor(parent, candidateChild):
	return primGroupsIncludedIn(parent, candidateChild)

def isParent(parent, candidateChild):
	if isAncestor(parent, candidateChild):
		#We know the groups in node are a subset of the ones in candidateChild...
		grParent = userDefinedPrimGroups(parent)
		grCandidateChild = userDefinedPrimGroups(candidateChild)
		#they'll parent and child if the child has the same 
		#number of USER-DEFINED labels of its parent, or just one more...
		#(the case of SAME labels happens when the user did nod add a product label
		#at the current node...)
		return len(grCandidateChild) <= len(grParent)+1
	return False

def startingPrims(node):
	return node.geometry().prims()

def parentNode(prim):
	myGeo = prim.geometry()
	myNode = myGeo.sopNode()
	return myNode

def childPrims(prim):
	children = []
	myNode = parentNode(prim)
	downstreamNodes = myNode.outputs()
	for n in downstreamNodes:
		if not bE_general.is_Insert_node(n):
			for child in n.geometry().prims():
				if isParent(prim, child):
					#print "isParent",prim, child
					children.append(child)
				#else:
				#	print "is NOT Parent",prim, child
	return children

def childInserts(prim):
	childrenInserts = []
	myGeo = prim.geometry()
	myNode = myGeo.sopNode()
	downstreamNodes = myNode.outputs()
	for n in downstreamNodes:
		if bE_general.is_Insert_node(n):
			groups = houPrimGroups.primGroups(prim)
			filters = bE_general.filters(n)
			for f in filters:
				if f in groups:
					childrenInserts.append(n)
	return childrenInserts

def parentPrim(prim):
	myGeo = prim.geometry()
	myNode = myGeo.sopNode()
	upstreamNodes = myNode.inputs()
	#print "parentPrim: upstreamNodes", upstreamNodes
	for n in upstreamNodes:
		if n:
			for p in n.geometry().prims():
				if isParent(p, prim):
					#we need to verify if isParent, even if we're checking only the upstream nodes...
					#  The reason is that "non-canonical" implementations might directly 
					#connect to nodes just to have some primitives processed while the rest
					#make a "detour" through other nodes before getting to the same node...
					#  if we use isAncestor, the library will be confused and give "false"
					#parenthood relations.
					return p
	return None	

def firstChild(prim):
	parent = parentPrim(prim)
	children = childPrims(parent)
	if len(children) > 0:
		return children[0]
	else:
		return None

def lastChild(prim):
	parent = parentPrim(prim)
	children = childPrims(parent)
	if len(children) == 0:
		return None
	else:
		return children[len(children)-1]

def nextSibling(prim):
	print "================="
	parent = parentPrim(prim)
	print "productTree.nextSibling - prim:", prim, "parent:", parent,
	children = childPrims(parent)
	print "children", children,
	pos = children.index(prim)
	print "pos", pos
	print "================="
	if len(children) > pos + 1:
		#print len(children), ">=", pos, "(", pos+1, ")"
		return children[pos + 1]
	else:
		return None
	
def previousSibling(prim):
	parent = parentPrim(prim)
	children = childPrims(parent)
	pos = children.index(prim)	
	if pos - 1 >= 0:
		return children[pos - 1]
	else:
		return None
	
# ////////////////////////////////////////////
# This function traverses the Product tree of an element and operates on the tree.  
# This function called recursively until the Product tree is fully traversed.
# 
# Parameters:
# - currentElement is the element that we want to operate on
# - depth is the depth of the current element 
#   (it should be 1 for the initial element)
# //////////////////////////////////////////
def traverseProductTree(currentElement, depth, op, insOp):
	if (currentElement):
		# Traverse the tree
		# Formatting code (indent the tree so it looks nice on the screen)
		op(currentElement, depth)
		children = childPrims(currentElement)
		#print depth*"  "+"traversing:", currentElement, children
		for currentElementChild in children:
			# Recursively traverse the tree structure of the child node
			traverseProductTree(currentElementChild, depth+1, op, insOp);
		childIns = childInserts(currentElement)
		for ins in childIns:
			insOp(currentElement, ins, depth)

# ////////////////////////////////////////////
# A few test functions: 
#           print the tree
# ////////////////////////////////////////////
def printOp(prim, depth):
	print depth * "  ", "("+str(depth)+")",prim
	pass

def printInsertOp(prim, node, depth):
	print (depth+1) * "  ", "****", node, " <-", prim
	pass

def printTree(rootNode, tagName = None):
	starting = startingPrims(rootNode)
	for pr in starting:
		groups = houPrimGroups.primGroups(pr)
		if not tagName or tagName in groups:
			print
			print "*********************************************"
			print "processing:", pr
			traverseProductTree(pr, 1, printOp, printInsertOp)

# ////////////////////////////////////////////
# A few test functions: 
#           print the terminal inserts
# ////////////////////////////////////////////
def nullOp(prim, depth):
	pass

def printTerminalInserts(rootNode, tagName = None):
	starting = startingPrims(rootNode)
	for pr in starting:
		print
		print "*********************************************"
		groups = houPrimGroups.primGroups(pr)
		if not tagName or tagName in groups:
			print "processing:", pr
			traverseProductTree(pr, 1, nullOp, printInsertOp)

if __name__ == '__main__':
	print "productTree library"	

# eof