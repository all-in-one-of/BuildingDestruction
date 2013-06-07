# -*- coding: utf-8 -*-
import time
from lib import GeoMath
import CalculateHeuristic
import RejectionSampling
import InfoPathPrim
import math
import logging

DEBUG = False
MAXTIMEFORONEPATH = 15
MAXTIMEFORALLPATHS = 30
TimeExecutionFirst = 0
TimeExecutionCurrent = 0
class PathBackTracking(object):
    def __init__(self, firstPrim, lastPrim, partDes, totDes, volume=None, max_iterations=None):
        global DEBUG
        if(DEBUG):
            reload(GeoMath)
            reload(InfoPathPrim)
        self.volume = volume
        #Convert all in InfoPathPrims
        indexFirst = partDes.index(firstPrim.prim)
        indexLast = partDes.index(lastPrim.prim)
        infoPartDes = InfoPathPrim.convertListIntoInfoPrim(partDes)
        infoTotDes = InfoPathPrim.convertListIntoInfoPrim(totDes)
        infoPartDes[indexFirst] = firstPrim
        infoPartDes[indexLast] = lastPrim
        firstInfoPrim = firstPrim
        lastInfoPrim = lastPrim

        self.firstPrim = firstInfoPrim
        self.lastPrim = lastInfoPrim
        self.partDes = infoPartDes
        self.totDes = infoTotDes
        self.clockwise = False
        self.goodPath = False
        self.path = []
        self.max_iterations_exceeded = False
        self.currentIteration = 0
        if(max_iterations):
            self.max_interations = max_iterations
        else:
            self.auto_choose_max_iterations()


    def do(self):
        #Start pathfinding with backtracking
        logging.debug("Start method do, class PathBackTracking")
        logging.debug("Group partially destroyed: %s", str([p.prim.number() for p in self.partDes]))
        logging.debug("Group totally destroyed: %s", str([p.prim.number() for p in self.totDes]))
        global TimeExecutionFirst
        global TimeExecutionCurrent
        global MAXTIMEFORALLPATHS
        count = 1
        pathAchieved = False
        TimeExecutionFirst = time.time()
        while(not pathAchieved and count < 2):
            self.max_iterations_exceeded = False
            path = []
            pathAchieved = False
            if(count == 1):
                refPrim = self.getBestPrimReference(self.firstPrim)
                angle = GeoMath.angleBetweenPointsByPrim(GeoMath.primBoundingBox(self.lastPrim.prim).center(), GeoMath.primBoundingBox(self.firstPrim.prim).center(), refPrim.prim)
                logging.debug("Main angle, which determine direction: %s", str(angle))
                self.clockWise = angle < 0
            else:
                self.clockWise = not self.clockWise
            path.append(self.firstPrim)
            pathAchieved = self.backTracking(self.firstPrim, path)
            count += 1
        self.path = path
        logging.debug("Last prim: %s, First prim: %s", str(self.lastPrim.prim.number()), str(self.firstPrim.prim.number()))
        if(pathAchieved):
            self.goodPath = True
            logging.debug("End method do, class PathBackTracking. State: good")
        else:
            self.goodPath = False
            logging.debug("End method do, class PathBackTracking. State: No path achieved")


    def backTracking(self, curPrim, path):
        global TimeExecutionFirst
        global TimeExecutionCurrent
        global MAXTIMEFORONEPATH
        global DEBUG
        logging.debug("Start method backTracking, class PathBackTracking")
        logging.debug("Current prim from parm: %s", str(curPrim.prim.number()))

        conPrims = GeoMath.getConnectedInfoPrims(curPrim, self.partDes)
        indexPrims = 0
        pathAchieved = False
        startPoint = None
        max_iterations_exceeded = False
        while (not pathAchieved and indexPrims < len(conPrims) and not max_iterations_exceeded):
            logging.debug("Current iteration: " + str(self.currentIteration))
            self.currentIteration += 1
            nextPrim = conPrims[indexPrims]
            #Now, choose the best prim reference
            refPrim = self.getBestPrimReference(curPrim)
            logging.debug("Current prim: %s. Next prim: %s", str(curPrim.prim.number()), str(nextPrim.prim.number()))
            logging.debug("Conected prims: %s. Count: %s", str([p.prim.number() for p in conPrims]), str(indexPrims))
            logging.debug("Reference prim: %s", str(refPrim.prim.number()))
            if(nextPrim not in path):
                if(self.volume):
                    edges = GeoMath.getEdgesBetweenPrims(curPrim.prim, nextPrim.prim)
                    for edge in edges:
                        rs = RejectionSampling.RejectionSampling(edge, self.volume)
                        rs.do()
                        startPoint = rs.getValue()
                        if(startPoint):
                            break
                logging.debug("Inicial point: %s", str(startPoint))

                if(startPoint):
                    angleMin, angleMax = GeoMath.getMinMaxAngleBetweenPointsInPrim(curPrim.prim, nextPrim.prim, refPrim.prim)
                    logging.debug("Current prim: %s. Next prim: s", str(curPrim.prim.number()), str(nextPrim.prim.number()))
                    logging.debug("Min angle: %s. Max angle: %s", str(angleMin), str(angleMax))
                    if(self.clockWise and (angleMin > 0 or angleMin < -(math.pi - math.pi * 0.1))):

                        logging.debug("ignorada por clockwise y revolverse")

                    if(not self.clockWise and (angleMax < 0 and angleMax < (math.pi - math.pi * 0.1))):

                        logging.debug("ignorada por not clockwise y revolverse")


                    if(nextPrim == self.lastPrim and curPrim.sumAngle < (1.4 * math.pi)):

                        logging.debug("ignorada por ultima y angulo no suficiente")


                    if((nextPrim == self.lastPrim and curPrim.sumAngle > (1.4 * math.pi))):

                        logging.debug("aceptada por ultima y angulo suficiente")




                    if((not((self.clockWise and (angleMin > 0 or angleMin < -(math.pi - math.pi * 0.01))) or \
                           (not self.clockWise and (angleMax < 0 or angleMax > (math.pi - math.pi * 0.01))) or \
                           (nextPrim == self.lastPrim and curPrim.sumAngle < (1.4 * math.pi))) or \
                           (nextPrim == self.lastPrim and curPrim.sumAngle > (1.4 * math.pi)))):

                        ch = CalculateHeuristic.CalculateHeuristic(curPrim, nextPrim, refPrim)
                        ch.do()
                        curPrim.next = nextPrim
                        curPrim.setfPoint(list(startPoint))
                        nextPrim.setiPoint(list(startPoint))
                        path.append(nextPrim)
                        logging.debug("Path: %s", str([p.number() for p in InfoPathPrim.convertListFromInfoPrimToPrim(path)]))
                        if(nextPrim == self.lastPrim):
                            #BASE CASE
                            logging.debug("Last prim achieved")
                            pathAchieved = True

                        if((self.currentIteration >= self.max_interations / 2) and not pathAchieved):
                            self.max_iterations_exceeded = True
                            logging.error('Max iterations, no path achieved in the maximum iterations')
                            #path.remove(nextPrim)
                            pathAchieved = False
                        if(not pathAchieved and not self.max_iterations_exceeded and self.backTracking(nextPrim, path)):
                            pathAchieved = True
                        elif (not pathAchieved and not self.max_iterations_exceeded):
                            path.remove(nextPrim)
                            logging.debug("Path: %s", str([p.number() for p in InfoPathPrim.convertListFromInfoPrimToPrim(path)]))

            indexPrims += 1
            if(pathAchieved):
                logging.debug("End ireration of while, method backTracking, class PathBackTracking. State: good")
            else:
                logging.debug("End ireration of while, method backTracking, class PathBackTracking. State: no path achieved")
        return pathAchieved


    def getPath(self):
        return self.path

    def getBestPrimReference(self, curPrim):
        listPrims = self.totDes
        index = 0
        #More little than the possible dot
        bestDot = -2
        while(index < len(listPrims) and bestDot < 0.998):
            #Both normals are good, because the projection will be the same
            dot = GeoMath.vecDotProduct(curPrim.prim.normal(), listPrims[index].prim.normal())
            if(dot > bestDot):
                bestDot = dot
                bestPrim = listPrims[index]
            index += 1
        return bestPrim

    def auto_choose_max_iterations(self):
        #=======================================================================
        # Backtracking has a eficiency of z^n, but it's too much, so I put 
        # n² iterations
        #=======================================================================

        self.max_interations = int(math.pow(len(self.partDes), 2))
        #self.max_interations = len(self.partDes)
        logging.debug("Number of automatic iterations: " + str(self.max_interations))
