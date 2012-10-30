# -*- coding: utf-8 -*-

from DestructionDataAndFunctions import DesPatternControl
from DestructionDataAndFunctions import Model_Texture
from Structure import BuildingStructure
import hou #@UnresolvedImport
import logging
from MainFunctions.InitDestroyedBuilding import InitDestroyedBuilding
class DefDestroy(object):
    def __init__(self):
        reload (DesPatternControl)
        reload(Model_Texture)
        #Building to apply the destruction
        self.__finalBuilding__ = None

        #Type labels
        self.__labelWindow = "window"
        self.__labelWall = "facade"
        self.__labelDoor = "door"

        #Nodes
        self.nodes = []
        self.patternControl = None

    def initPattern(self, initDestroyedBuildingClass):
        # @type initDestroyedBuildingClass InitDestroyedBuilding
        conditionNodeGeneric = initDestroyedBuildingClass.__conditionNodeGeneric__
        conditionNodeInserts = initDestroyedBuildingClass.__conditionNodeInserts__
        listOfParmsGroup = initDestroyedBuildingClass.__conditionGroupsParm__
        geo = initDestroyedBuildingClass.__geo__
        namePathGroup = 'path'

        #Create merge node
        mergeNode = geo.createNode('merge')
        mergeNode.setNextInput(conditionNodeInserts)
        mergeNode.setNextInput(conditionNodeGeneric)

        #Connect groupNode partDes shop to condition nodes
        combineGroupPartDes = geo.createNode('group')
        combineGroupPartDes.setNextInput(mergeNode)
        #rename node
        combineGroupPartDes.setName('combinedGroupPartDes', True)
        #Connect groupNode totDes shop to groupPartDes node
        combineGroupTotDes = geo.createNode('group')
        combineGroupTotDes.setNextInput(combineGroupPartDes)
        #rename node
        combineGroupTotDes.setName('combinedGroupTotDes', True)

        combineGroupNotDes = geo.createNode('group')
        combineGroupNotDes.setNextInput(combineGroupTotDes)
        #rename node
        combineGroupNotDes.setName('combinedGroupNotDes', True)

        totDesInsertName = conditionNodeInserts.evalParm(listOfParmsGroup[0])
        partiDesInsertName = conditionNodeInserts.evalParm(listOfParmsGroup[1])
        notDesInsertName = conditionNodeInserts.evalParm(listOfParmsGroup[2])

        totDesGenericName = conditionNodeGeneric.evalParm(listOfParmsGroup[0])
        partiDesGenericName = conditionNodeGeneric.evalParm(listOfParmsGroup[1])
        notDesGenericName = conditionNodeGeneric.evalParm(listOfParmsGroup[2])

        #Inicialize combined groups
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

        primsCombinedTotDes = combineGroupNotDes.geometry().findPrimGroup('combinedTotDes')
        primsCombinedPartDes = combineGroupNotDes.geometry().findPrimGroup('combinedPartDes')
        primsCombinedNotDes = combineGroupNotDes.geometry().findPrimGroup('combinedNotDes')

        if(primsCombinedTotDes != None):
            primsCombinedTotDesG = primsCombinedTotDes.prims()
        if(primsCombinedNotDes != None):
            primsCombinedNotDesG = primsCombinedNotDes.prims()
        if(primsCombinedPartDes != None):
            primsCombinedPartDesG = primsCombinedPartDes.prims()

        '''
        primGroups=primsCombinedNotDes.geometry().primGroups()
        for group in primGroups:
            if group.name()=='combinedPartDes':
                combinedPDgroup=group
            elif group.name()=='combinedTotDes':
                combinedTDgroup=group
        '''
        volume = initDestroyedBuildingClass.outside
        #Prepare to get path and crack and texturing
        logging.debug('INSERTS DEFDESTROY:' + str(initDestroyedBuildingClass.__inserts__))
        modelTex = Model_Texture.Model_Texture(combineGroupNotDes,
                                                initDestroyedBuildingClass.__inserts__)
        self.patternControl = DesPatternControl.DesPatternControl(
                            primsCombinedPartDesG, primsCombinedTotDesG,
                            primsCombinedNotDesG, geo, namePathGroup,
                            primsCombinedNotDes, volume=volume, modelTex=modelTex)
        self.patternControl.doPath(geo, combineGroupNotDes)
        #self.patternControl.doCrack()
        #Insert color to primitives in path
        primitivePath = geo.createNode('primitive')
        primitivePath.setName('Color_to_path')
        primitivePath.parm('doclr').set('on')
        primitivePath.parm('group').set(namePathGroup)
        expression = "this=hou.pwd().inputs()[0].geometry() \n"\
        "for group in this.primGroups(): \n"\
        "   if group.name()=='path': \n"\
        "       list=group.prims() \n"\
        "listP=[prim.number() for prim in list] \n"\
        "return listP.index(hou.lvar('PR'))/float(len(listP)) "

        primitivePath.parm('diffg').setExpression(expression, hou.exprLanguage.Python)
        primitivePath.parm('diffr').deleteAllKeyframes()
        primitivePath.parm('diffb').deleteAllKeyframes()
        combineGroupNotDes.moveToGoodPosition()
        primitivePath.setNextInput(self.patternControl.nodePath)

        primitivePath.moveToGoodPosition()
        combineGroupTotDes.moveToGoodPosition()
        combineGroupPartDes.moveToGoodPosition()
        combineGroupNotDes.moveToGoodPosition()

        self.nodes.append(mergeNode)
        self.nodes.append(combineGroupNotDes)
        self.nodes.append(combineGroupPartDes)
        self.nodes.append(combineGroupTotDes)
        self.nodes.append(primitivePath)
        self.nodes.append(self.patternControl.nodePath)
        primitivePath.setDisplayFlag(True)

    def createStructure(self, initDestroyedBuildingClass):
        reload (BuildingStructure)
        logging.debug("Class DefDestroy, Method createStructure")
        '''
        user_restriction_parms:
            general:
                #label_window
                window_size_x
                window_size_y
            floors:
                #floor_default_size_y
                floor_default_put_each_y
            tubes:
                #tube_default_radius
                tube_default_put_each_y
                tube_default_put_each_x
                tube_default_put_each_z
        '''
        user_restriction_parms = {}
        #FIXME: hardcoded window label
        user_restriction_parms['label_window'] = 'finestra'
        user_restriction_parms['floor_default_size_y'] = 0.1
        user_restriction_parms['tube_default_radius'] = 0.08

        building_structure = BuildingStructure.BuildingStructure(self.patternControl.crack,
                                            initDestroyedBuildingClass.__inserts__,
                                             initDestroyedBuildingClass.__geo__,
                                              user_restriction_parms)
        building_structure.do()

    def deleteNodes(self):
        for node in self.nodes:
            node.destroy()
