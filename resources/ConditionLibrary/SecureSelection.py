# -*- coding: utf-8 -*-
import hou
#primGroup contains a list of primitives, it is NOT a object group of houdini
def condition(primGroup, primReference, geo, grow):
    #Base case false
    if grow==0 or (primReference.number() in [primIter.number() for primIter in primGroup]):
        return False
    #Firts check if the primitive satisfy the condition
    primInGroup=False
    for vertex in primReference.vertices():
        for prim in primGroup:
            for vertice in prim.vertices():
                if vertex.point().position()==vertice.point().position():
                    primInGroup=True                
    #Base case true            
    if primInGroup:
        return True
    grow=grow-1
    if grow==0: return False
    #Next level of grow, we have to construct the new group of grow
    tempGroup=primGroup[:]
    for primGeo in geo.prims():
        if condition(primGroup, primGeo, geo, 1):
            tempGroup.append(primGeo)
            
    #Check if the primitive is in this level of grow, recursive call
    if condition(tempGroup, primReference, geo, grow):
        return True                            
    return False