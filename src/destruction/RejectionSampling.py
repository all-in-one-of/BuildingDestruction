# -*- coding: utf-8 -*-
from lib import GeoMath

class RejectionSampling():
        def __init__(self, edge, volume):
            self.edge = edge
            self.volume = volume
            self.value = None

        def do(self):
            for _ in range(10):
                point = GeoMath.getRandomPointInEdge(self.edge, 0.06)
                if(GeoMath.pointInVolume(self.volume, point)):
                    self.value = point
                    break

        def getValue(self):
            return self.value
