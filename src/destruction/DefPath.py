# -*- coding: utf-8 -*-
from lib import GeoMath
from lib import HouInterface
import Data
import DesError
import InfoPathPrim
import PathAstar
import PathBackTracking
import RejectionSampling
import ValidatePath
import logging
import random
DEBUG = True
epsilon = 0.001

class DefPath(object):
    """
    Class for define a path interprimitive
    @partDes: group of primitives partially destroyed.
    @type partDes: hou.PrimGroup
    @totDes: group of primitives totally destroyed.
    @type partDes: hou.PrimGroup
    @notDes: group of primitives not destroyed.
    @type notDes: hou.PrimGroup
    @geo: geometry node(python sop) where on this program can work and where it will has to be called
    """
    def __init__(self, partDes=None, totDes=None, notDes=None, Ipoint=None, primOfIpoint=None, volume=None, max_time=120):
        logging.debug("Start method __init__, class DefPath")
        global DEBUG
        global ITERATIONS
        if (DEBUG):
            reload (GeoMath)
            reload (Data)
            reload (RejectionSampling)
            reload (InfoPathPrim)
            reload (PathBackTracking)
            reload (PathAstar)
            reload (ValidatePath)
        self.path = []
        self.error = DesError.DesError()
        if(totDes): totDes = list(totDes)
        if(partDes): partDes = list(partDes)
        if(notDes): notDes = list(notDes)
        if(totDes):
            self.refPrim = totDes[0]
            count = 0
            # Limit=number of primitives in partDes(it is not a combinational result)
            max_interations = 10
            goodPath = False
            while(not goodPath and count < max_interations):
                count += 1
                firstPrim = None
                lastPrim = None
                countExtremPrims = 0
                while((not firstPrim or not lastPrim) and countExtremPrims < 15):
                    firstPrim, lastPrim = self.getExtremPrims(Ipoint, primOfIpoint, partDes, self.refPrim, notDes, volume)
                    countExtremPrims += 1
                if (countExtremPrims == 15):
                    logging.error("No first and last prim")
                    logging.debug("End method __init__, class DefPath. State: too many comprovations for first and last prim")
                    return
                logging.debug("First prim: %s, Last prim: %s", str(firstPrim.prim.number()), str(lastPrim.prim.number()))
                if(not(firstPrim and lastPrim) and Ipoint and primOfIpoint):
                    self.error.setCode(1)
                    logging.debug("End method __init__, class DefPath. State: not first and last prim")
                    return
                self.path, goodPath = self.getPathBackTracking(firstPrim, lastPrim, notDes, partDes, totDes, volume)
            if len(self.path) == 0:
                self.error.setCode(2)
                logging.error("No path")
                logging.debug("End method __init__, class DefPath. State: no path")
                return

    def getExtremPrims(self, Ipoint, primOfIpoint, partDes, refPrim, notDes, volume=None):
        '''
        We can't ensure that the primitives have a posible path, but we ensure that last primitive
        have at least 2 adjacent primitives and first primitive is connected with the last primitive
        '''
        logging.debug("Start method getExtremPrims, class DefPath")
        firstPrim = None
        lastPrim = None
        if(primOfIpoint and Ipoint):
            # NOT YET TOTALLY IMPLEMENTED
            edge = GeoMath.getEdgeWithPointInPrim(primOfIpoint, Ipoint)
            lastPrim = primOfIpoint
            for prim in partDes:
                if(prim != lastPrim):
                    sharedEdges = GeoMath.getSharedEdgesPrims(lastPrim, prim)
                    rs_lP_fP = False
                    if(volume):
                        for edge in sharedEdges:
                            rs = RejectionSampling.RejectionSampling(edge, volume)
                            rs.do()
                            point = rs.getValue()
                            if(point):
                                rs_lP_fP = True
                                break
                    if (len(sharedEdges >= 1) and  (edge in sharedEdges) and (volume == None or rs_lP_fP)):
                        firstPrim = prim
        else:
            # Automatically decision of extrem prims.
            # Ensure that 2 prims is connected to another primitive in
            # group of partially destroyed.
            # Didn't use "getConnectedPrims" because need ramdonless in choice of prims.
            stopSearch = False
            tempList1 = list(partDes)
            # minimum of 4 prims to get a path
            while (len(tempList1) > 4 and not stopSearch):
                numPrim1 = random.randint(0, len(tempList1) - 1)
                prim1 = tempList1[numPrim1]
                del tempList1[numPrim1]
                # We have to ensure that first prim has at least two conected prims
                if(True):  # prim1.number()>17 and prim1.number()<27
                    while((len(GeoMath.getConnectedPrims(prim1, list(partDes), 2)) < 2) and (len(tempList1) > 4)):
                        numPrim1 = random.randint(0, len(tempList1) - 1)
                        prim1 = tempList1[numPrim1]
                        del tempList1[numPrim1]
                    # If prim1 has at least two conected prims
                    if(len(tempList1) > 4):
                        conectedToPrim1 = GeoMath.getConnectedPrims(prim1, list(tempList1))
                        while (len(conectedToPrim1) > 0 and not stopSearch):
                            numPrim2 = random.randint(0, len(conectedToPrim1) - 1)
                            prim2 = conectedToPrim1[numPrim2]
                            if(prim2 != prim1):
                                # If prim2 has at least 2 conected prims
                                if(len(GeoMath.getConnectedPrims(prim2, list(tempList1), 2)) >= 2):
                                    stopSearch = True
                                    if(volume):
                                        rs_lP_fP = False
                                        for edge in GeoMath.getEdgesBetweenPrims(prim1, prim2):
                                            logging.debug("Edge: %s", str(edge))
                                            rs = RejectionSampling.RejectionSampling(edge, volume)
                                            rs.do()
                                            point = rs.getValue()
                                            if(point):
                                                rs_lP_fP = True
                                                break
                                        if(not rs_lP_fP):
                                            stopSearch = False
                                    if(stopSearch):
                                        # Assign the last evaluate because we have it now in a variable.
                                        firstPrim = InfoPathPrim.InfoPathPrim(prim2)
                                        # Last prim sure has two adjacent primitives.
                                        lastPrim = InfoPathPrim.InfoPathPrim(prim1)
                                        firstPrim.setiPoint(list(point))
                                        lastPrim.setfPoint(list(point))
                            del conectedToPrim1[numPrim2]
            if(firstPrim and lastPrim):
                logging.debug("End method getExtremPrims, class DefPath. State: good")
            else:
                logging.debug("End method getExtremPrims, class DefPath. State: no extrem prims")
            return firstPrim, lastPrim

    def getPathBackTracking(self, firstPrim, lastPrim, notDes, partDes, totDes, volume=None, DEBUG=False, max_interations=None):
        logging.debug("Start method getPathBackTracking, class DefPath")
        p = PathBackTracking.PathBackTracking(firstPrim, lastPrim, partDes, totDes, volume, max_interations)
        p.do()
        goodPath = True
        if(p.goodPath):
            # TEMP: We not ensure the path, because we are debugging cracking now
            '''
            if(ValidatePath.ValidatePath(notDes, partDes, totDes, InfoPathPrim.convertListFromInfoPrimToPrim(p.path)).getisValid()):
                logging.debug("End method getPathBackTracking, class DefPath. State: good")
                goodPath = True
            else:
                logging.debug("Path have not closure around totally destroyed")
                goodPath = False
            '''
        else:
            logging.error("No path")
            logging.debug("End method getPathBackTracking, class DefPath. State: No path achived")
            goodPath = False
        return p.getPath(), goodPath

    def getPathAstar(self, firstPrim, lastPrim, notDes, partDes, totDes, refPrim, minimum=True, aperture=150, volume=None, DEBUG=False):
        p = PathAstar.PathAstar(firstPrim, lastPrim, partDes, refPrim, minimum, aperture, volume)
        p.do()
        if(len(p.path) > 3):
            if(ValidatePath.ValidatePath(notDes, partDes, totDes, InfoPathPrim.convertListFromInfoPrimToPrim(p.path)).getisValid()):
                logging.debug("End method getPathBackTracking, class DefPath. State: good")
                goodPath = True
            else:
                logging.debug("Path have not closure around totally destroyed")
                goodPath = False
        else:
            logging.error("No path")
            logging.debug("End method getPathBackTracking, class DefPath. State: path < 4")
            goodPath = False
        return p.getPath(), goodPath

    def getPathInPrims(self):
        return InfoPathPrim.convertListFromInfoPrimToPrim(self.path)

    def showPoints(self):
        h = HouInterface.HouInterface()
        for prim in self.path:
            h.showPoint(prim.getiPoint())
# _End class defPath_#
