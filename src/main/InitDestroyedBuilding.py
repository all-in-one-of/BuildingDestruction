# -*- coding: utf-8 -*-
# HOU dependant

from lib import LoD
import hou  # @UnresolvedImport
import logging
import math
import re


# PRECONDITIONS: Not modified building, not with condition nodes before, etc.(for LoD function cause!)
# Program possible issues:
# -need to be linux, for the slash in some parameters?¿?¿?¿?¿?¿?. It will be fixed shortly
# -be careful with the products and filters and the function hou.parm.expression(). Take it into account.

# Houdini names(not all yet)
nameParmObjPath = 'objpath'
nameParmGroups = 'group'
nameParmEnable = 'enable'
offsetCondNodeGroupsParm = 6

###############################################################################################

class InitDestroyedBuilding:

    def __init__(self):
        self.__listPartsInserts__ = []
        self.__listPartsGeneric__ = []
        self.__conditionNodeInserts__ = None
        self.__conditionNodeGeneric__ = None
        self.__finalBuilding__ = None
        self.__inserts__ = []
        self.__base_node__ = None
        # Program names
        self.__listNamesInserts__ = ['insertsTotallyDestroyed', 'insertsPartiallyDestroyed', 'insertsNotDestroyed']
        self.__listNamesGeneric__ = ['genericDestroyed']
        self.__nameOfInsertGroups__ = ['insertTotDestroyed', 'insertPartDestroy', 'insertNotDestroy']
        self.__nameOfGenericGroups__ = ['genericTotDestroy', 'genericPartDestroy', 'genericNotDestroy']
        self.__conditionGroupsParm__ = ['totdes', 'partides', 'notdes']

        self.__rayIntersectSomePointPath__ = '$HIP/conditonallib/RayIntersectSomePoint.py'
        self.__rayIntersectAllPointsPath__ = '$HIP/conditionallib/RayIntersectAllPoints.py'
        self.__rayIntersectCenterPath__ = '$HIP/conditionallib/RayIntersectCenter.py'
        self.__secureSelectionPath__ = '$HIP/conditionallib/SecureSelection.py'
        self.__geo__ = None

###############################################################################################
###############################################################################################

    def twoSpeheresDestruction(self, geo):
        self.__geo__ = geo
        self.__selectionMetode__ = "twoSpeheresDestruction"
        # Creating building nodes
        print "#Creating building nodes"
        self.__createBuildingNodes__()
        # Creating 2 spheres for the destruction
        print "#Creating 2 spheres for the destruction"
        self.inside = self.__geo__.createNode('sphere')
        self.outside = self.__geo__.createNode('sphere')
        # Setting up the condition node with the 2 created spheres
        print "#Setting up the condition node with the 2 created spheres"
        self.__iniCondiNode__(self.__conditionNodeInserts__, self.inside, self.outside, 0, 0)
        self.__iniCondiNode__(self.__conditionNodeGeneric__, self.inside, self.outside, 1, 0)
        # Setting values to spheres based on geometry previous condition node
        print "#Setting values to spheres based on geometry previous condition node"
        self.__iniSpheres__(self.inside, self.outside, self.__conditionNodeInserts__)
        # Setting up building nodes, IMPORTANT: need to all nodes(condition node and spheres) inicialized
        print "#Setting up building nodes"
        self.__iniBuildingNodes__()
        # Deleting building parts totally destroyed
        print "#Deleting building parts totally destroyed"
        self.__iniDeleteGeo__()
        self.__finalBuilding__.setDisplayFlag(True)
        self.__finalBuilding__.setRenderFlag(True)

    ###############################################################################################

    def secureSelectionDestruction(self, geo):
        self.__geo__ = geo
        self.__selectionMetode__ = "secureSelectionDestruction"
        # Creating building nodes
        print "#Creating building nodes"
        self.__createBuildingNodes__()
        # Creating 2 spheres for the destruction
        print "#Creating 2 spheres for the destruction"
        self.inside = self.__geo__.createNode('sphere')
        # Setting up the condition node with the 2 created spheres
        print "#Setting up the condition node with the 1 created spheres"
        self.__iniCondiNode__(self.__conditionNodeInserts__, self.inside, None, 0, 1)
        self.__iniCondiNode__(self.__conditionNodeGeneric__, self.inside, None, 1, 1)
        # Setting values to spheres based on geometry previous condition node
        print "#Setting values to spheres based on geometry previous condition node"
        self.__iniSpheres__(self.inside, None, self.__conditionNodeInserts__)
        # Setting up building nodes, IMPORTANT: need to all nodes(condition node and spheres) inicialized
        print "#Setting up building nodes"
        self.__iniBuildingNodes__()
        # Deleting building parts totally destroyed
        print "#Deleting building parts totally destroyed"
        self.__iniDeleteGeo__()
        self.__finalBuilding__.setDisplayFlag(True)
        self.__finalBuilding__.setRenderFlag(True)

    ###############################################################################################
    ###############################################################################################
    ###############################################################################################
    ###############################################################################################

    # #Global variables used: nameParmObjPath
    def __createBuildingNodes__(self):
        # Inicialize for LoD function
        firstNode = self.__geo__.children()[0]
        firstNode.setSelected(True)
        LoD.LoD_max().recorrer(LoD.connexioDescendent(), LoD.obtenirNodesArrels().obtenir())
        # Last added node(node from LoD import function) which contains the original building
        originalBuilding = self.__geo__.children()[len(self.__geo__.children()) - 1]
        originalBuilding.moveToGoodPosition()
        # We create the condition node and connect it with the nodes
        # which input nodes were connected
        conditionNodeInserts = self.__geo__.createNode('destructionConditional')
        conditionNodeInserts.setName('conditionNodeInserts', True)
        conditionNodeGeneric = self.__geo__.createNode('destructionConditional')
        conditionNodeGeneric.setName('conditionNodeGeneric', True)
        mergeToInserts = self.__geo__.createNode('merge')
        mergeToInserts.setName('mergeToInserts', True)
        mergeFromGeneric = self.__geo__.createNode('merge')
        mergeFromGeneric.setName('mergeFromGeneric', True)
        fuseToInserts = self.__geo__.createNode('fuse')
        fuseToInserts.setName('fuseToInserts', True)
        fuseToInserts.parm('dist').set(0.01)
        fuseFromGeneric = self.__geo__.createNode('fuse')
        fuseFromGeneric.setName('fuseFromGeneric', True)
        fuseFromGeneric.parm('dist').set(0.01)
        conditionNodeInserts.moveToGoodPosition()
        conditionNodeGeneric.moveToGoodPosition()
        # pattern to find the correct parm in the "object_merge" node
        # wich is the original building
        pattern = nameParmObjPath + '[0-9]*'
        patternCompiled = re.compile(pattern)

        '''
        Added and modified 19/05/2011
        '''
        geo = self.__geo__
        listOfParmsGroup = self.__conditionGroupsParm__
        # Create merge node
        mergeNode = geo.createNode('merge')
        mergeNode.setNextInput(conditionNodeInserts)
        mergeNode.setNextInput(conditionNodeGeneric)
        # Connect groupNode partDes shop to condition nodes
        combineGroupPartDes = geo.createNode('group')
        combineGroupPartDes.setNextInput(mergeNode)
        # rename node
        combineGroupPartDes.setName('combinedGroupPartDes', True)
        # Connect groupNode totDes shop to groupPartDes node
        combineGroupTotDes = geo.createNode('group')
        combineGroupTotDes.setNextInput(combineGroupPartDes)
        # rename node
        combineGroupTotDes.setName('combinedGroupTotDes', True)

        combineGroupNotDes = geo.createNode('group')
        combineGroupNotDes.setNextInput(combineGroupTotDes)
        # rename node
        combineGroupNotDes.setName('combinedGroupNotDes', True)

        totDesInsertName = conditionNodeInserts.evalParm(listOfParmsGroup[0])
        partiDesInsertName = conditionNodeInserts.evalParm(listOfParmsGroup[1])
        notDesInsertName = conditionNodeInserts.evalParm(listOfParmsGroup[2])

        totDesGenericName = conditionNodeGeneric.evalParm(listOfParmsGroup[0])
        partiDesGenericName = conditionNodeGeneric.evalParm(listOfParmsGroup[1])
        notDesGenericName = conditionNodeGeneric.evalParm(listOfParmsGroup[2])

        # Inicialize combined groups
        combineGroupPartDes.parm('crname').set('combinedPartDes')
        combineGroupPartDes.parm('grpequal').set('combinedPartDes')
        combineGroupPartDes.parm('grp1').set(partiDesInsertName)
        combineGroupPartDes.parm('grp2').set(partiDesGenericName)
        combineGroupPartDes.parm('op1').set('or')

        combineGroupTotDes.parm('crname').set('combinedTotDes')
        combineGroupTotDes.parm('grpequal').set('combinedTotDes')
        combineGroupTotDes.parm('grp1').set(totDesInsertName)
        combineGroupTotDes.parm('grp2').set(totDesGenericName)
        combineGroupTotDes.parm('op1').set('or')

        combineGroupNotDes.parm('crname').set('combinedNotDes')
        combineGroupNotDes.parm('grpequal').set('combinedNotDes')
        combineGroupNotDes.parm('grp1').set(notDesInsertName)
        combineGroupNotDes.parm('grp2').set(notDesGenericName)
        combineGroupNotDes.parm('op1').set('or')

        labeler = self.__geo__.createNode('Labeler')
        labeler.setNextInput(combineGroupNotDes)
        '''
        End modification 19/05/2011
        '''
        for parm in originalBuilding.parms():
            if patternCompiled.match(parm.name()):
                posibleNode = hou.node(parm.eval())
                if posibleNode.type().name() == 'Insert':
                    logging.debug('INSERTS:' + str(posibleNode))
                    self.__inserts__.append(posibleNode)
                    tempInputs = posibleNode.inputs()
                    # we delete the connections from input nodes to not duplicated geometry
                    '''
                    Added and modified 12/05/2011, Labeler
                    '''
                    posibleNode.setInput(0, labeler, 0)
                    '''
                    End modification 12/05/2011, Labeler
                    '''

                    for i in range(len(tempInputs) - 1):
                        posibleNode.setInput(i + 1, None, 0)
                    for input in tempInputs:
                        # We have to ensure that "input" is not None(in houdini it's allowed None inputs) and not repeat
                        if input != None and input not in mergeToInserts.inputs():
                            mergeToInserts.setNextInput(input, 0)

        fuseToInserts.setNextInput(mergeToInserts, 0)
        conditionNodeInserts.setNextInput(fuseToInserts, 0)
        mergeToInserts.moveToGoodPosition()
        fuseToInserts.moveToGoodPosition()
        conditionNodeInserts.moveToGoodPosition()
        for output in conditionNodeInserts.outputs():
            output.moveToGoodPosition()
        # we create the nodes which will contain the destroyed building. They will be a copy
        # of the original building, and later we will change some parameters to convert it to
        # a destroyed building

        # "group" of nodes to copy. We need only the original building, but, for houdini software reasons
        # it must be a group.
        tempGroup = [originalBuilding]
        listPartsInserts = []
        listPartsGeneric = []
        for name in self.__listNamesInserts__:
            tempNode = hou.copyNodesTo(tempGroup, originalBuilding.parent())[0]
            tempNode.setName(name, True)
            listPartsInserts.append(tempNode)
        for name in self.__listNamesGeneric__:
            tempNode = hou.copyNodesTo(tempGroup, originalBuilding.parent())[0]
            tempNode.setName(name, True)
            listPartsGeneric.append(tempNode)
        originalBuilding.destroy()

        # Create the final building node
        finalBuilding = self.__geo__.createNode('merge')
        finalBuilding.setName('finalBuilding', True)
        finalBuilding.moveToGoodPosition()
        # Connect the building inserts geometry(modified) with the final building
        for node in listPartsInserts:
            finalBuilding.setNextInput(node)
            node.moveToGoodPosition()
        # Connect the building general(no insert geometry) with the condition node especific for they
        for node in listPartsGeneric:
            mergeFromGeneric.setNextInput(node)
            node.moveToGoodPosition()
        fuseFromGeneric.setNextInput(mergeFromGeneric)
        conditionNodeGeneric.setNextInput(fuseFromGeneric)
        mergeFromGeneric.moveToGoodPosition()
        fuseFromGeneric.moveToGoodPosition()
        conditionNodeGeneric.moveToGoodPosition()

        mergeNode.moveToGoodPosition()
        labeler.moveToGoodPosition()
        combineGroupPartDes.moveToGoodPosition()
        combineGroupTotDes.moveToGoodPosition()
        combineGroupNotDes.moveToGoodPosition()

        # Finally connect the condition node of the general geometry to the final building
        finalBuilding.setNextInput(labeler)
        finalBuilding.moveToGoodPosition()
        # Assign the data
        self.__listPartsInserts__ = listPartsInserts
        self.__listPartsGeneric__ = listPartsGeneric
        self.__conditionNodeInserts__ = conditionNodeInserts
        self.__conditionNodeGeneric__ = conditionNodeGeneric
        self.__finalBuilding__ = finalBuilding
        self.__labeler__ = labeler

    ###############################################################################################

    # #Global variables used: nameParmGroups, nameParmObjPath, offsetCondNodeGroupsParm, nameParmEnable
    def __iniBuildingNodes__(self):

        patternGroups = re.compile(nameParmGroups + '[0-9]*')
        # the order to set name group is: first group name to the first group name in node condition parm

        ###___###___###   Inserts geometry   ###___###___###

        for node in self.__listPartsInserts__:
            for parm in node.parms():
                if patternGroups.match(parm.name()):
                    nodeInParm = hou.node(node.parm(nameParmObjPath + str(re.split(nameParmGroups, parm.name())[1])).evalAsString())
                    # Ok for insert nodes geometry
                    if nodeInParm.type().name() == 'Insert':
                        expression = "hou.evalParm(\"" + self.__conditionNodeInserts__.parms()[offsetCondNodeGroupsParm + self.__listPartsInserts__.index(node)].path() + "\")"
                        parm.setExpression(expression, hou.exprLanguage.Python)
                    else:
                        node.parm(nameParmEnable + str(re.split(nameParmGroups, parm.name())[1])).set(False)

        ###___###___###   Generic geometry   ###___###___###

        for node in self.__listPartsGeneric__:
            for parm in node.parms():
                if patternGroups.match(parm.name()):
                    nodeInParm = hou.node(node.parm(nameParmObjPath + str(re.split(nameParmGroups, parm.name())[1])).evalAsString())
                    # Not insert nodes geometry
                    if nodeInParm.type().name() == 'Insert':
                        node.parm(nameParmEnable + str(re.split(nameParmGroups, parm.name())[1])).set(False)

    ###############################################################################################

    def __iniCondiNode__(self, conditionNode, inside, outside, typeOfgeometry, mode):

        ###___###___###   MODE=0, two spheres mode   ###___###___###

        if mode == 0:
            conditionNode.parm('importgeototal').set(inside.path())
            conditionNode.parm('importgeoparti').set(outside.path())
            # typeOfgeometry=0, geometry of insert nodes
            if typeOfgeometry == 0:
                conditionNode.parm(self.__conditionGroupsParm__[0]).set(self.__nameOfInsertGroups__[0])
                conditionNode.parm(self.__conditionGroupsParm__[1]).set(self.__nameOfInsertGroups__[1])
                conditionNode.parm(self.__conditionGroupsParm__[2]).set(self.__nameOfInsertGroups__[2])
                conditionNode.parm('pythonfile').set(self.__rayIntersectAllPointsPath__)
                conditionNode.parm('pythonfile2').set(self.__rayIntersectCenterPath__)
            # typeOfgeometry=1, geometry of generic nodes
            elif typeOfgeometry == 1:
                conditionNode.parm(self.__conditionGroupsParm__[0]).set(self.__nameOfGenericGroups__[0])
                conditionNode.parm(self.__conditionGroupsParm__[1]).set(self.__nameOfGenericGroups__[1])
                conditionNode.parm(self.__conditionGroupsParm__[2]).set(self.__nameOfGenericGroups__[2])
                conditionNode.parm('pythonfile').set(self.__rayIntersectAllPointsPath__)
                conditionNode.parm('pythonfile2').set(self.__rayIntersectSomePointPath__)
            conditionNode.parm('filter').set('')
            conditionNode.parm('parms').set('Two spheres')

        ###___###___###   MODE=1, secure selection mode   ###___###___###

        elif mode == 1:
            conditionNode.parm('importgeototal').set(inside.path())
            # typeOfgeometry=0, geometry of insert nodes
            if typeOfgeometry == 0:
                conditionNode.parm(self.__conditionGroupsParm__[0]).set(self.__nameOfInsertGroups__[0])
                conditionNode.parm(self.__conditionGroupsParm__[1]).set(self.__nameOfInsertGroups__[1])
                conditionNode.parm(self.__conditionGroupsParm__[2]).set(self.__nameOfInsertGroups__[2])
                conditionNode.parm('pythonfile').set(self.__rayIntersectAllPointsPath__)
            # typeOfgeometry=1, geometry of generic nodes
            elif typeOfgeometry == 1:
                conditionNode.parm(self.__conditionGroupsParm__[0]).set(self.__nameOfGenericGroups__[0])
                conditionNode.parm(self.__conditionGroupsParm__[1]).set(self.__nameOfGenericGroups__[1])
                conditionNode.parm(self.__conditionGroupsParm__[2]).set(self.__nameOfGenericGroups__[2])
                conditionNode.parm('pythonfile').set(self.__rayIntersectAllPointsPath__)
            conditionNode.parm('pythonfile2').set(self.__secureSelectionPath__)
            conditionNode.parm('filter').set('')
            conditionNode.parm('parms').set('Secure selection, 1')


    ###############################################################################################

    def __iniSpheres__(self, inside, outside, conditionNode):
        maxRadium = 0
        minRadium = modul3D(primBoundingBox(conditionNode.inputs()[0].geometry().prims()[0]).sizevec() - primBoundingBox(conditionNode.inputs()[0].geometry().prims()[0]).center())
        center = conditionNode.inputs()[0].geometry().globPoints('0')[0].position()
        for input in conditionNode.inputs():
            for prim in input.geometry().prims():
                radium = modul3D(primBoundingBox(prim).sizevec() - primBoundingBox(prim).center())
                maxRadium = (radium if radium > maxRadium else maxRadium)
                minRadium = (radium if radium < minRadium else minRadium)
                for vertex in prim.vertices():
                    position = vertex.point().position()
                    center = (position if position[1] > center[1] else center)
        if inside != None:
            inside.parm('radx').set((minRadium + maxRadium) / 4)
            inside.parm('rady').set((minRadium + maxRadium) / 4)
            inside.parm('radz').set((minRadium + maxRadium) / 4)
            inside.setName('inside', True)
            inside.parm('tx').set(center[0])
            inside.parm('ty').set(center[1])
            inside.parm('tz').set(center[2])
            inside.parm('freq').set('4')
            inside.parm('type').set('poly')
            inside.moveToGoodPosition()
        if outside != None:
            outside.parm('radx').set(maxRadium / 1.5)
            outside.parm('rady').set(maxRadium / 1.5)
            outside.parm('radz').set(maxRadium / 1.5)
            outside.parm('tx').set(center[0])
            outside.parm('ty').set(center[1])
            outside.parm('tz').set(center[2])
            outside.setName('outside', True)
            outside.parm('type').set('poly')
            outside.parm('freq').set('4')
            outside.moveToGoodPosition()

    ###############################################################################################

    def __iniDeleteGeo__(self):
        '''
        #Creating delete nodes to the totally destroyed geometry
        insertsDeleteTotDes = self.__geo__.createNode('delete')
        insertsDeleteTotDes.setName('insertsDeleteTotDes', True)
        genericDeleteTotDes = self.__geo__.createNode('delete')
        genericDeleteTotDes.setName('genericDeleteTotDes', True)
        #Disconect from the final building
        indexInputFinalbuildingInserts = self.__listPartsInserts__[0].outputConnections()[0].inputIndex()
        self.__finalBuilding__.setInput(indexInputFinalbuildingInserts, None)
        indexInputFinalbuildingGeneric = self.__conditionNodeGeneric__.outputConnections()[0].inputIndex()
        self.__finalBuilding__.setInput(indexInputFinalbuildingGeneric, None)
        insertsDeleteTotDes.setInput(0, self.__listPartsInserts__[0], 0)
        genericDeleteTotDes.setInput(0, self.__conditionNodeGeneric__, 0)
        self.__finalBuilding__.setNextInput(genericDeleteTotDes, 0)
        self.__finalBuilding__.setNextInput(insertsDeleteTotDes, 0)
        insertsDeleteTotDes.parm('group').set("")
        insertsDeleteTotDes.parm('negate').set(True)
        genericDeleteTotDes.parm('group').set(self.__conditionNodeGeneric__.parm(self.__conditionGroupsParm__[0]).evalAsString())
        genericDeleteTotDes.parm('negate').set(False)
        insertsDeleteTotDes.moveToGoodPosition()
        genericDeleteTotDes.moveToGoodPosition()
        '''

###############################################################################################

    def printAtributtes(self):
        print self.__listPartsInserts__
        print self.__listPartsGeneric__
        print self.__conditionNodeInserts__
        print self.__conditionNodeGeneric__
        print self.__finalBuilding__

        # Program names
        print self.__listNamesInserts__
        print self.__listNamesGeneric__
        print self.__nameOfInsertGroups__
        print self.__nameOfGenericGroups__
        print self.__conditionGroupsParm__

        print self.__rayIntersectSomePointPath__
        print self.__rayIntersectAllPointsPath__
        print self.__rayIntersectCenterPath__
        print self.__secureSelectionPath__
        print self.__selectionMetode__
        print self.__geo__

    def __ERRORCONTROL__(self, stage):
        pass

###############################################################################################
###############################################################################################
###############################################################################################
###############################################################################################

def modul3D(listObject):
    return math.sqrt(listObject[0] * listObject[0] + listObject[1] * listObject[1] + listObject[2] * listObject[2])

###############################################################################################

def primBoundingBox(prim):
    tempListMin = prim.vertices()[0].point().position()
    tempListMax = prim.vertices()[0].point().position()
    for index in prim.vertices():
        position = index.point().position()
        tempListMin[0] = min(tempListMin[0], position[0])
        tempListMin[1] = min(tempListMin[1], position[1])
        tempListMin[2] = min(tempListMin[2], position[2])
        tempListMax[0] = max(tempListMax[0], position[0])
        tempListMax[1] = max(tempListMax[1], position[1])
        tempListMax[2] = max(tempListMax[2], position[2])
    boundingBox = hou.BoundingBox(tempListMin[0], tempListMin[1], tempListMin[2], tempListMax[0], tempListMax[1], tempListMax[2])
    return boundingBox

###############################################################################################



