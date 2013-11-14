# -*- coding: utf-8 -*
from lib import UIProcessStatus
import BoolIntersection_RegionGrowing
import crack
import Data
import DefPath
DEBUG = True

class DesPatternControl(object):
    def __init__(self, partDes=None, totDes=None, notDes=None, geo=None, namePathGroup="path", node=None, volume=None, modelTex=None):

        global DEBUG
        if(DEBUG):
            reload(crack)
            reload(DefPath)
            reload(BoolIntersection_RegionGrowing)
            reload(Data)
        self.partDes = partDes
        self.totDes = totDes
        self.notDes = notDes
        self.namePathGroup = namePathGroup
        self.geo = geo
        self.node = node
        self.volume = volume
        self.modelTex = modelTex
        self.regionGrowing = None
        self.composeNeededGeometry = None
        self.pathConf = None
        self.crack = None
        self.nodePath = None
        self.booleanIntersectionNodes = []

    def doPath(self, geo, node):
        self.pathConf = DefPath.DefPath(self.partDes, self.totDes, self.notDes, volume=self.volume)
        groupPath = geo.createNode('group', 'groupPath')
        groupPath.parm('crname').set(self.namePathGroup)
        string = ""
        for prim in self.pathConf.getPathInPrims():
            string = string + str(prim.number()) + " "
        groupPath.parm('pattern').set(string)
        groupPath.setNextInput(node)
        groupPath.moveToGoodPosition()
        self.nodePath = groupPath

    def doCrack(self):
        reload(crack)
        self.crack = crack.Crack()
        self.modelTex.assignTextureForPrim()
        
        for count in range(len(self.pathConf.path)):
            previousPrim = self.pathConf.path[count - 1]
            thisPrim = self.pathConf.path[count]
            nextPrim = self.pathConf.path[(count + 1) % (len(self.pathConf.path))]
            texture = self.modelTex.assignedPrimTexture[thisPrim.getPrim()]
            self.crack.doCrack(texture, previousPrim, thisPrim, nextPrim)
        self.crack.doLineCrackPerPrim(self.pathConf.path)

    def showTextures(self):
        self.modelTex.showTextures(geo=self.geo)

    def deleteShowTextureNodes(self):
        self.modelTex.deleteShowTextureNodes()

    def showCrack(self, allInOne=True):
        # Show crack
        self.crack.showCrack(self.geo, self.pathConf.path, False)

    def deleteShowCrackNodes(self):
        self.crack.deleteShowCrackNodes()

    def showIntersectionTexture(self):
        # Show crack
        self.crack.showTextureIntersections(self.geo)

    def deleteShowIntersectionTexture(self):
        self.crack.deleteShowTextureIntersectionNodes()

    def doBooleanIntersection(self, initDestroyedObject):
        reload(BoolIntersection_RegionGrowing)
        sweepingNode = self.geo
        self.composeNeededGeometry = sweepingNode.createNode('delete', 'composeNeededGeometry')
        self.composeNeededGeometry.setNextInput(initDestroyedObject.__finalBuilding__)
        self.mergeResult = sweepingNode.createNode('merge', 'result')
        self.boolIntersection = BoolIntersection_RegionGrowing.BoolIntersection_RegionGrowing(self.pathConf.refPrim, self.partDes, self.crack.linePerPrim, initDestroyedObject.__finalBuilding__, sweepingNode)

        stringToCompose = ""
        # Generic and inserts not broken prims
        stringToCompose = stringToCompose + initDestroyedObject.__nameOfGenericGroups__[2] + " "
        stringToCompose = stringToCompose + initDestroyedObject.__nameOfInsertGroups__[2] + " "

        for primToCompose in self.partDes:
            if(primToCompose not in self.boolIntersection.alreadyVisited and primToCompose not in self.boolIntersection.primitivesDivided):
                stringToCompose = stringToCompose + "__" + str(primToCompose.number()) + " "

        self.composeNeededGeometry.parm('group').set(stringToCompose)
        self.composeNeededGeometry.parm('negate').set(True)
        self.mergeResult.setNextInput(self.composeNeededGeometry)

        for primDivided in self.boolIntersection.primitivesDivided.values():
            self.mergeResult.setNextInput(primDivided.deleteNode)
            self.booleanIntersectionNodes.extend(primDivided.nodes)

        self.mergeResult.moveToGoodPosition()
        self.composeNeededGeometry.moveToGoodPosition()
        initDestroyedObject.__finalBuilding__.setHardLocked(True)
        self.mergeResult.setDisplayFlag(True)

        self.booleanIntersectionNodes.append(self.composeNeededGeometry)
        self.booleanIntersectionNodes.append(self.mergeResult)

    def deleteBooleanIntersectionNodes(self):
        for node in self.booleanIntersectionNodes:
            node.destroy()
        self.booleanIntersectionNodes = []

    def add_noise_to_crack(self, heigth, frequency, for_edge, wavelength):
        self.deleteShowCrackNodes()
        self.crack.add_noise_to_crack(heigth, frequency, for_edge, wavelength)
        self.crack.doLineCrackPerPrim(self.pathConf.path)
        self.showCrack(True)
