# -*- coding: utf-8 -*-
from lib import GeoMath
import logging

class CalculateHeuristic(object):
    def __init__(self, curPrim, nextPrim, refPrim):
        self.curPrim = curPrim
        self.nextPrim = nextPrim
        self.refPrim = refPrim

    def do(self):

        angleToSum = abs(GeoMath.angleBetweenPointsByPrim(GeoMath.primBoundingBox(self.curPrim.prim).center(), \
                         GeoMath.primBoundingBox(self.nextPrim.prim).center(), self.refPrim.prim))

        heuristic = self.curPrim.F + 1
        angle = self.curPrim.sumAngle + angleToSum
        logging.debug("Heuristic for prim %s with next prim %s and ref prim %s, angle to sum: %s", str(self.curPrim.prim.number()), str(self.nextPrim.prim.number()), str(self.refPrim.prim.number()), str(angle))
        self.nextPrim.setHeuristic(heuristic, 0)
        self.nextPrim.setSumAngle(angle)
        return self.nextPrim

