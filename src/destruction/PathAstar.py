# -*- coding: utf-8 -*-
from lib import GeoMath
import RejectionSampling
import InfoPathPrim
import math

class PathAstar(object):

    def __init__(self, firstPrim, lastPrim, partDes, refPrim, minimum=True, aperture=150, volume=None, DEBUG=False):

        # Convert all in InfoPathPrims
        indexFirst = partDes.index(firstPrim.prim)
        indexLast = partDes.index(lastPrim.prim)



        self.firstPrim = firstPrim
        self.lastPrim = lastPrim
        self.partDes = InfoPathPrim.convertListIntoInfoPrim(partDes)
        self.partDes[indexFirst] = firstPrim
        self.partDes[indexLast] = lastPrim
        self.refPrim = InfoPathPrim.InfoPathPrim(refPrim)
        self.minimum = minimum
        self.aperture = aperture
        self.volume = volume
        self.DEBUG = DEBUG

    def do(self):
        epsilon = 0.001
        if (self.DEBUG):
            print "REF PRIM"
            print self.refPrim.prim.number()
            print "########## START PATH ###############"
        """
        Construct a path around refPrim with start prim "firstPrim" and goal prim "lastPrim"
        if parameter minimum is true, que path is the minimum path, otherwise is the "maximum"
        path (inverted heuristic, but not maximum path)
        """
        count = 0
        path = []
        while(not path and count < 2):
            count += 1
            openList = []
            closedList = []
            connectedPrims = []
            if(count == 1):
                angleMin, angleMax = GeoMath.getMinMaxAngleBetweenPointsInPrim(self.lastPrim.prim, self.firstPrim.prim, self.refPrim.prim)
                clockWise = max(math.fabs(angleMin), math.fabs(angleMax)) == math.fabs(angleMin)
            else:
                clockWise = not clockWise
            if(self.DEBUG):
                print "Angulo min max"
                print angleMin, angleMax, clockWise


            openList.append(self.firstPrim)

            # Start A* search
            while(len(openList) > 0 and (self.lastPrim not in closedList)):
                # Get the node with more or less heuristic depending of parm minimum
                if(self.minimum):
                    curPrim = openList[0]
                    del openList[0]
                else:
                    curPrim = openList.pop()
                # Switch the current prim to closest list
                closedList.append(curPrim)
                # Get connected primitives
                connectedPrims = GeoMath.getConnectedInfoPrims(curPrim, self.partDes)
                if(self.DEBUG):
                    print "CLOSE PRIM"
                    print curPrim.prim.number()
                    print "CONNECTED PRIMS"
                    print [conp.prim.number() for conp in connectedPrims]
                # Clean not possible primitives(because we are go around refPrim)
                for index in range(len(connectedPrims)):
                    conPrim = connectedPrims[index]
                    # angleMin, angleMax = GeoMath.getMinMaxAngleBetweenPointsInPrim(curPrim.prim, conPrim.prim, refPrim)
                    angleMin = angleMax = GeoMath.angleBetweenPointsByPrim(GeoMath.primBoundingBox(curPrim.prim).center(), GeoMath.primBoundingBox(conPrim.prim).center(), self.refPrim)
                    dot = GeoMath.vecDotProduct(self.refPrim.normal(), conPrim.prim.normal())
                    if(dot > 1 - epsilon):
                        # precision error
                        dot = 1
                    # math.acos(dot) > aperture

                    if(self.volume):
                        edges = GeoMath.getEdgesBetweenPrims(curPrim.prim, curPrim.parent.prim)
                        for edge in edges:
                            rs = RejectionSampling.RejectionSampling(edge, self.volume)
                            rs.do()
                            inicialPoint = rs.getValue()
                            if(inicialPoint):
                                break
                    if((not((math.acos(dot) > self.aperture) or \
                           (clockWise and (angleMin > 0 or angleMin < -(math.pi - math.pi * 0.1))) or \
                           (not clockWise and (angleMax < 0 or angleMax > (math.pi - math.pi * 0.1))) or \
                           (conPrim in closedList) or \
                           (conPrim == self.lastPrim and curPrim.sumAngle < (1.4 * math.pi))) or \
                           (conPrim == self.lastPrim and curPrim.sumAngle > (1.4 * math.pi))) and \
                           (inicialPoint or not self.volume)):

                        # If prim is already in openList
                        if(conPrim in openList):
                            heuristic = 1
                            if((curPrim.G + heuristic > conPrim.G and not self.minimum) or
                               (curPrim.G + heuristic < conPrim.G and self.minimum)):
                                # If this path is better than the path with the current parent
                                conPrim.setParent(curPrim)
                                conPrim = self.calculateHeuristic(curPrim, conPrim, self.refPrim)
                                if(self.volume):
                                    conPrim.fPoint = list(inicialPoint)
                                    curPrim.iPoint = list(inicialPoint)
                                if(self.DEBUG):
                                    print "Prim aceptada y ya estaba en openlist"
                                    print curPrim.prim.number(), conPrim.prim.number()
                        else:
                            conPrim.setParent(curPrim)
                            conPrim = self.calculateHeuristic(curPrim, conPrim, self.refPrim)
                            if(self.volume):
                                conPrim.fPoint = list(inicialPoint)
                                curPrim.iPoint = list(inicialPoint)
                            openList.append(conPrim)
                            if(self.DEBUG):
                                print "Prim aceptada y no estaba en openlist"
                                print curPrim.prim.number(), conPrim.prim.number()

                # Sort nodes by heuristic
                openList.sort(key=lambda infoPrim: infoPrim.F)

            if(self.lastPrim in closedList):
                if(self.DEBUG):
                    print "Last prim Angle", self.lastPrim.sumAngle
                curPrim = closedList.pop()
                while(curPrim != self.firstPrim):
                    path.append(curPrim)
                    curPrim = curPrim.parent
                path.append(curPrim)
            else:
                path = []
            path.reverse()
        print "########## FINALIZE PATH ###############"
        self.path = path

