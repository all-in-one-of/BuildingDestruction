'''
Created on Mar 25, 2011

@author: carlos
'''
from lib import GeoMath
import PrimDivided
import logging

class BoolIntersection_RegionGrowing(object):
    '''
    classdocs
    '''
    def __init__(self, refPrim, allPrims, crack, volumeNode, sweepingNode):
        reload (GeoMath)
        reload (PrimDivided)
        self.alreadyVisited = []
        self.primitivesDivided = {}
        self.growing(refPrim, None, allPrims, crack, volumeNode, sweepingNode)

    def growing(self, thisPrim, previousPrim, allPrims, primsWithLine, volumeNode, sweepingNode):
        logging.debug("Start method growing, class BoolIntersection_RegionGrowing")
        # Base case, prim matched
        if (thisPrim in primsWithLine.keys() and thisPrim not in self.primitivesDivided.keys()):
            # Divide prim in two prims with boolean intersection
            primDivided = PrimDivided.PrimDivided(thisPrim, previousPrim, self.primitivesDivided, primsWithLine, volumeNode, sweepingNode)
            # "thisPrim" doesn't exists anymore(it was converted into two prims, contained in "primDivided"
            if(primDivided.prim):
                logging.debug("Divided prim de %s", str(primDivided.prim.number()))
                self.primitivesDivided[thisPrim] = primDivided
            else:
                logging.debug("NO prim divided de %s", str(thisPrim.number()))
                logging.debug("End method growing, class BoolIntersection_RegionGrowing. State: good, no prim divided")
                return
        inside = True
        # Only put in "already visited" the prims totally destroyed, the others remain in "primitivesDivided"
        if(thisPrim not in self.primitivesDivided.keys()):
            self.alreadyVisited.append(thisPrim)
            if(previousPrim in self.primitivesDivided.keys()):
                inside = self.testInsideOutside(thisPrim, self.primitivesDivided[previousPrim])
        # Next recursivity
        if(inside):
            connectedPrims = GeoMath.getConnectedPrims(thisPrim, allPrims)
            logging.debug("CONNECTED PRIMS:")
            logging.debug(str([p.number() for p in connectedPrims]))
            for nextPrim in connectedPrims:
                if(nextPrim not in self.alreadyVisited and nextPrim not in self.primitivesDivided.keys()):
                    logging.debug("Siguiente growing con: %s", str(nextPrim.number()), " viene de %s", str(thisPrim.number()))
                    self.growing(nextPrim, thisPrim, allPrims, primsWithLine, volumeNode, sweepingNode)
                else:
                    if(nextPrim in self.alreadyVisited):
                        logging.debug("Visitada %s", str(nextPrim.number()), " viene de %s", str(thisPrim.number()))
                    if(nextPrim in self.primitivesDivided.keys()):
                        logging.debug("Divided prim %s", str(nextPrim.number()), " viene de %s", str(thisPrim.number()))

        else:
            # It's not inside, so we have to conserve it
            self.alreadyVisited.pop()
        logging.debug("End method growing, class BoolIntersection_RegionGrowing.  State: good")
        return

    def testInsideOutside(self, prim, primDivided):
        edgeToValidate = GeoMath.getSharedEdges(primDivided.pointsOutside, [list(po.point().position()) for po in prim.vertices()], 1)
        if(len(edgeToValidate) > 0):
            return True
        else:
            return False
