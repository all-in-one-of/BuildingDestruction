# ==================================================
# primGroups(prim):
#   Returns the groups a primitive is in...
# ==================================================


def primGroups(prim):
	groups = []
	geo = prim.geometry()
	for gr in geo.primGroups():
		if gr.contains(prim):
			groups.append(gr.name())
	return groups

def samePrimGroups(primA, primB):
	grA = primGroups(primA)
	grB = primGroups(primB)
	grA.sort()
	grB.sort()
	return grA == grB