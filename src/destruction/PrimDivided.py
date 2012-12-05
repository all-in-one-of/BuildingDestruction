'''
Created on Mar 25, 2011

@author: carlos
'''
from ExternalClasses import GeoMath
import logging
epsilon = 0.01
class PrimDivided(object):
    '''
    WARNING=This class works with prims in diferents states.
    '''
    def __init__(self, prim, connectedPrim, listOfDividedPrims, crack, volumeNode, sweepingNode):
        reload (GeoMath)
        self.prim = prim
        self.primBroken = None
        self.primNotBroken = None
        self.curveNode = None
        self.extrudeNode = None
        self.cookieNode = None
        self.deleteNode = None
        self.pointsOutside = None
        self.nameGroupBroken = 'Broken_prim_' + str(prim.number())
        self.nameGroupNotBroken = 'NotBroken_prim_' + str(prim.number())
        self.nodes = []
        self.houDoBooleanOperation(prim, connectedPrim, listOfDividedPrims, crack, volumeNode, sweepingNode)

    def houDoBooleanOperation(self, prim, previousPrim, listOfDividedPrims, crack, volumeNode, sweepingNode):
        logging.debug("Start method houDoBooleanOperation, class PrimDivided")
        global epsilon
        logging.debug("This prim: %s", str(prim))
        logging.debug("Previous prim: %s", str(previousPrim))
        if(previousPrim in listOfDividedPrims.keys()):
            edgeToValidate = GeoMath.getSharedEdges(listOfDividedPrims[previousPrim].pointsOutside, [list(po.point().position()) for po in prim.vertices()], 1)
            if(not edgeToValidate):
                self.prim = None
                logging.error("No edge to validate")
                logging.debug("Start method houDoBooleanOperation, class PrimDivided. State: No edge to valide in prim %s", str(prim.number()))
                return False
            edgeToValidate = edgeToValidate[0]
        else:
            edgeToValidate = GeoMath.getSharedEdgesPrims(previousPrim, prim, 1)[0]
            if(not edgeToValidate):
                logging.error("No edge to validate")
                logging.debug("Start method houDoBooleanOperation, class PrimDivided. State: No edge to valide in prim %s", str(prim.number()))
                self.prim = None
                return False

        logging.debug("Edge to validate: %s", str(edgeToValidate))
        edgeToValidate = [list(edgeToValidate[0]), list(edgeToValidate[1])]

        firstPointCrack = crack[prim][0]
        lastPointCrack = crack[prim][len(crack[prim]) - 1]
        matched = False
        #Points ordered by prim
        points = [list(p.point().position()) for p in prim.vertices()]
        edgeFirst = GeoMath.getEdgeWithPointInPrim(prim, firstPointCrack)
        edgeFirst = [list(edgeFirst[0]), list(edgeFirst[1])]
        #Put the edge in clockwise direction
        if(GeoMath.determineDirEdge(edgeFirst, prim, True)):
            curEdge = [firstPointCrack, edgeFirst[1]]
        else:
            curEdge = [firstPointCrack, edgeFirst[0]]
        index = 0
        logging.debug("Points: %s", str(points))
        logging.debug("Current edge: %s", str(curEdge))
        count = 0
        while(points[index] != curEdge[1]):
            count += 1
            if(count == 10):
                logging.error("First edge not found")
                logging.debug("End method houDoBooleanOperation, class PrimDivided. State: first edge not found")
                return
            index += 1
        nextIndex = (index + 1) % len(points)
        nextEdge = [curEdge[1], points[nextIndex]]
        edgeLast = GeoMath.getEdgeWithPointInPrim(prim, lastPointCrack)
        edgeLast = [list(edgeLast[0]), list(edgeLast[1])]
        if(not GeoMath.determineDirEdge(edgeLast, prim, True)):
            edgeLast = [list(edgeLast[1]), list(edgeLast[0])]
        pointsDisplaced = []

        #Normal iteration over points
        count = 0
        logging.debug("Last edge where the 'to validate edge' lies: %s", str(edgeLast))
        self.pointsOutside = []
        logging.debug("Normal iteration over points")
        while(len(GeoMath.getSharedEdges(curEdge, edgeLast, 1)) == 0):
            logging.debug("Current edge: %s", str(curEdge))
            count += 1
            if(count == 10):
                logging.error("Last edge not found")
                logging.debug("End method houDoBooleanOperation, class PrimDivided. State: Last edge not found")
                return
            #Calcule the displacement
            vecDis = self.calculateDisplacement(curEdge, nextEdge)
            pointDisplaced = self.applyDisplacement(curEdge[1], vecDis)
            #Add displace point
            pointsDisplaced.append(pointDisplaced)
            self.pointsOutside.append(curEdge[1])
            if(len(GeoMath.getSharedEdges(curEdge, edgeToValidate, 1)) > 0):
                matched = True
            curEdge = [curEdge[1], points[nextIndex]]
            nextIndex = (nextIndex + 1) % len(points)
            nextEdge = [nextEdge[1], points[nextIndex]]
        logging.debug("Ha salido del segundo bucle con: %s", str(curEdge))
        curEdge = [curEdge[0], lastPointCrack]
        #Last comprovation
        if(not matched and (len(GeoMath.getSharedEdges(curEdge, edgeToValidate, 1)) > 0)):
            logging.debug("Final comprovation edge: %s", str(curEdge))
            matched = True
        if(not matched):
            logging.debug("Not matched at normal iteration over points, trying in inverse mode")
            #Do inverse
            #Put the edge in not clockwise direction
            if(GeoMath.determineDirEdge(edgeFirst, prim, False)):
                curEdge = [firstPointCrack, edgeFirst[1]]
            else:
                curEdge = [firstPointCrack, edgeFirst[0]]
            index = 0
            count = 0
            while(points[index] != curEdge[1]):
                count += 1
                if(count == 10):
                    logging.error("First edge not found")
                    logging.debug("End method houDoBooleanOperation, class PrimDivided. State: Last edge not found")
                    return
                index += 1
            nextIndex = (index - 1)
            if(nextIndex < 0):
                nextIndex = (len(points) - 1)
            nextEdge = [curEdge[1], points[nextIndex]]
            edgeLast = GeoMath.getEdgeWithPointInPrim(prim, lastPointCrack)
            if(not GeoMath.determineDirEdge(edgeLast, prim, False)):
                edgeLast = [list(edgeLast[1]), list(edgeLast[0])]
            pointsDisplaced = []
            self.pointsOutside = []
            #Inverse iteration over points
            count = 0
            logging.debug("Inverse iteration over points")
            while(len(GeoMath.getSharedEdges(curEdge, edgeLast, 1)) == 0):
                count += 1
                if(count == 10):
                    logging.error("Last edge not found")
                    logging.debug("End method houDoBooleanOperation, class PrimDivided. State: Last edge not found")
                    return
                #Calcule the displacement
                vecDis = self.calculateDisplacement(curEdge, nextEdge)
                pointDisplaced = self.applyDisplacement(curEdge[1], vecDis)
                pointsDisplaced.append(pointDisplaced)
                self.pointsOutside.append(curEdge[1])
                if((len(GeoMath.getSharedEdges(curEdge, edgeToValidate, 1)) > 0)):
                    matched = True
                curEdge = [curEdge[1], points[nextIndex]]
                nextIndex = (nextIndex - 1)
                if(nextIndex < 0):
                    nextIndex = len(points) - 1
                nextEdge = [nextEdge[1], points[nextIndex]]
            curEdge = [curEdge[0], lastPointCrack]
            #Last comprovation
            if(not matched and (len(GeoMath.getSharedEdges(curEdge, edgeToValidate, 1)) > 0)):
                logging.debug("Final comprovation edge: %s", str(curEdge))
                matched = True
        if(not matched):
            logging.error("Validate edge not found at primitive")
        #Add the extrem points
        self.pointsOutside.insert(0, firstPointCrack)
        self.pointsOutside.append(lastPointCrack)
        #Now we have a structure with the points in correct order, with the edge that was broken and
        #with applied displacement for each point. Not firstCrackPoint either lastCrackPoint added.
        curveNode = sweepingNode.createNode('curve', 'crack_pattern_' + str(prim.number()))
        #curveNode.setNextInput(volumeNode)
        pointsString = ""
        for point in crack[prim]:
            pointsString = pointsString + str(point[0]) + "," + str(point[1]) + "," + str(point[2]) + " "
        #Now we add the displacement point to close the prim
        pointsDisplaced.reverse()
        for point in pointsDisplaced:
            pointsString = pointsString + str(point[0]) + "," + str(point[1]) + "," + str(point[2]) + " "


        curveNode.parm('coords').set(pointsString)
        curveNode.moveToGoodPosition()
        curveNode.parm('close').set(True)
        extrudeNode = sweepingNode.createNode('extrude', 'extrude_' + str(prim.number()))

        extrudeNode.setNextInput(curveNode)

        largeOfGeo = extrudeNode.geometry().boundingBox().sizevec().length()
        extrudeNode.parm('depthxlate').set(-largeOfGeo / 2 - 0.5)
        extrudeNode.parm('depthscale').set(largeOfGeo + 1)

        #Associate part B with crack line volume
        #extrudeNode.setNextInput(crackNode)

        cookieNode = sweepingNode.createNode('cookie', 'cookie_' + str(prim.number()))

        cookieNode.parm('dojitter').set(True)
        cookieNode.parm('jitteramount').set(0.001)
        cookieNode.parm('seed').set(3)
        cookieNode.parm('boolop').set('other')
        cookieNode.parm('insideB').set(True)
        cookieNode.parm('outsideB').set(True)
        cookieNode.setNextInput(extrudeNode)
        #Associate part B with volume
        cookieNode.setNextInput(volumeNode)
        cookieNode.parm('groupB').set("__" + str(prim.number()))
        cookieNode.parm('createGroup').set(True)
        cookieNode.parm('insideAGroup').set("Ain")
        cookieNode.parm('insideBGroup').set(self.nameGroupBroken)
        cookieNode.parm('outsideAGroup').set("Aout")
        cookieNode.parm('outsideBGroup').set(self.nameGroupNotBroken)
        cookieNode.parm('overlapAGroup').set("Aover")
        cookieNode.parm('overlapBGroup').set("Bover")

        #Delete the unwanted groups
        deleteNode = sweepingNode.createNode('delete', 'unwantedGroups_' + str(prim.number()))
        deleteNode.parm('group').set(self.nameGroupBroken + ' Ain Aout Aover Bover')
        deleteNode.setNextInput(cookieNode)
        self.curveNode = curveNode
        self.extrudeNode = extrudeNode
        self.cookieNode = cookieNode
        self.deleteNode = deleteNode
        self.curveNode.moveToGoodPosition()
        self.extrudeNode.moveToGoodPosition()
        self.cookieNode.moveToGoodPosition()
        self.deleteNode.moveToGoodPosition()

        self.nodes.append(self.curveNode)
        self.nodes.append(self.extrudeNode)
        self.nodes.append(self.cookieNode)
        self.nodes.append(self.deleteNode)
        logging.debug("End method houDoBooleanOperation, class PrimDivided. State: good")

    def calculateDisplacement(self, curEdge, nextEdge):
        '''
            Edges are correlatives and in wise direction
        '''
        curEdgeNor = GeoMath.vecSub(curEdge[1], curEdge[0])
        curEdgeNor = GeoMath.vecNormalize(curEdgeNor)
        nextEdgeNor = GeoMath.vecSub(nextEdge[1], nextEdge[0])
        nextEdgeNor = GeoMath.vecNormalize(nextEdgeNor)
        return GeoMath.vecSub(curEdgeNor, nextEdgeNor)

    def applyDisplacement(self, point, displacement):
        displacement.append(0)
        m = GeoMath.Matrix(4, 4)
        m.matrix4Trans(displacement)
        point.append(1)
        pointModificated = m.mulPoint4ToMatrix4(point)
        point.pop()
        displacement.pop()
        pointModificated.pop()
        return pointModificated

