class InfoPathPrim():
    """
    Class which add nedded information to a single houdini primitive for path finding
    """
    def __init__(self, prim):
        self.prim = prim
        self.visited = False
        self.parent = None
        #Sum of heuristics G and H
        self.F = 0
        #Cost from initial point to this point
        self.G = 0
        #Cost from this point to final point
        self.H = 0
        #Angle from initial point to this point trougth path
        self.sumAngle = 0
        self.next = None
        self.fPoint = None
        self.iPoint = None

    def setParent(self, newParent):
        self.parent = newParent

    def setNext(self, next):
        self.next = next

    def getNext(self):
        return self.next

    def setiPoint(self, iPoint):
        self.iPoint = iPoint

    def setfPoint(self, fPoint):
        self.fPoint = fPoint

    def getiPoint(self):
        return self.iPoint

    def getfPoint(self):
        return self.fPoint

    def getPrim(self):
        return self.prim

    def setHeuristic(self, G, H):
        self.G = G
        self.H = H
        self.F = G + H

    def setSumAngle(self, angle):
        self.sumAngle = angle

    #Functions to manage InfoPathPrim instances
def convertIntoInfoPrim(prim):
    infoPrim = InfoPathPrim(prim)
    return infoPrim

def convertListIntoInfoPrim(listPrims):
    listInfoPrim = []
    for prim in listPrims:
        infoPrim = convertIntoInfoPrim(prim)
        listInfoPrim.append(infoPrim)
    return listInfoPrim

def convertFromInfoPrimToPrim(p):
    return p.prim

def convertListFromInfoPrimToPrim(listPrims):
    return [p.prim for p in listPrims]

def setListParent(listToSetParent, parent):
    for infoPrim in listToSetParent:
        infoPrim.setParent(parent)
    return listToSetParent
