'''
Created on Jun 13, 2011

@author: carlos
'''
import logging
import random
from ExternalClasses import GeoMath, HouInterface
class ValidatePath(object):
    '''
    Classe which permit to validate the path taking into account tree curves or set of primitives.
    -The totally destroyed set of primitives, that will be the closest set
    -The set of primitives partially destroyed, that will be the set which the path lies in
    -The set of not destroyed prims, that will be the set that validates the closure of the set of primitives
     partially destroyed recursively
     
     The path has to be a sequentially path
    '''

    def __init__(self, setNotDestroyed, setPartiallyDestroyed, setTotDestroyed, path):
        reload (GeoMath)
        reload (HouInterface)
        self.setNotDestroyed = setNotDestroyed
        self.setPartiallyDestroyed = setPartiallyDestroyed
        self.setTotDestroyed = setTotDestroyed
        self.path = path
        self.valid = self.doValidation(setNotDestroyed, setPartiallyDestroyed, setTotDestroyed, path)
    def doValidation(self, setNotDestroyed, setPartiallyDestroyed, setTotDestroyed, path):
        logging.debug("Start method doValidation. Class ValidatePath")
        '''
        We have to generate two branch for each primitive. One for one group of edges from prim, which
        all of its edges shared a group of primitives (not destroyed or tot destroyed), the other
        set of edges shared the other group of primitives (not destroyed or tot destroyed)
        
        To disjoin the two sets of edges, we take into account that each primitive is connected with
        two primitives more, that lies in set of path primitives. From one shared edge between this prim
        and one prim conected to this prim in the path set to the other edge shared to the other path prim
        we have a set of edges, and equal in the other side.
        '''
        validPrim1 = None
        validPrim2 = None
        find = False
        provePath = list(path)
        while(not (validPrim1 and validPrim2) and len(provePath) > 0):
            num = int(random.random() * len(provePath))
            prim = provePath[num]
            del provePath[num]
            '''
            h=HouInterface.HouInterface()
            h.showPoint(GeoMath.primBoundingBox(prim).center(), name='prim_'+str(prim.number()), color=[0,1,0])
            '''
            if(len(GeoMath.getEdgesFromPrim(prim)) <= 3):
                prim = self.tryToCollapseTwoTrianglesInOneQuad(prim, path)
                #NOT IMPLEMENTED YET
                logging.debug("Collapse in one quad NOT IMPLEMENTED YET")
            else:
                validPrim1, validPrim2 = self.getPrimsSharingGroupOfEdges(prim, setNotDestroyed, setPartiallyDestroyed, setTotDestroyed)
        if(not (validPrim1 and validPrim2)):
            logging.debug("Not valid path, because any prim is valid to do the validation, with groups:")
            logging.debug("Group not destroyed: %s", str([p.number() for p in setNotDestroyed]))
            logging.debug("Group partially destroyed: %s", str([p.number() for p in setPartiallyDestroyed]))
            logging.debug("Group totally destroyed: %s", str([p.number() for p in setTotDestroyed]))
            logging.debug("Path: %s", str([p.number() for p in path]))
            logging.debug("End method doValidation. Class ValidatePath. State: no valid path")
            #ONLY FOR DEBUGGING!!! IN FACT, IT MUST TO RETURN FALSE!!!!
            return True
        logging.debug("Valid primitives: %s, %s", str(validPrim1.number()), str(validPrim2.number()))
        matchNotDes1, matchTotDes1 = self.findSomeGroupRecursively(validPrim1, setNotDestroyed, setPartiallyDestroyed, setTotDestroyed)
        matchNotDes2, matchTotDes2 = self.findSomeGroupRecursively(validPrim2, setNotDestroyed, setPartiallyDestroyed, setTotDestroyed)
        if((matchNotDes1 and matchTotDes2) or (matchNotDes2 and matchTotDes1)):
            logging.debug("Valid path")
            logging.debug("End method doValidation. Class ValidatePath. State: good")
            find = True
        if (not find):
            logging.debug("Not valid path with groups:")
            logging.debug("Group not destroyed: %s", str([p.number() for p in setNotDestroyed]))
            logging.debug("Group partially destroyed: %s", str([p.number() for p in setPartiallyDestroyed]))
            logging.debug("Group totally destroyed: %s", str([p.number() for p in setTotDestroyed]))
            logging.debug("Path: %s", str([p.number() for p in path]))
            logging.debug("End method doValidation. Class ValidatePath. State: no valid path")

        return find

    def findSomeGroupRecursively(self, prim, setNotDestroyed, setPartiallyDestroyed, setTotDestroyed):
        currentPartiallyDestroyed = list(setPartiallyDestroyed)
        '''
        h = HouInterface.HouInterface()
        h.showPoint(GeoMath.primBoundingBox(prim).center(), name='prim_' + str(prim.number()), color=[1, 0, 0])
        '''
        matchNotDes = prim in setNotDestroyed
        matchTotDes = prim in setTotDestroyed
        if(not matchNotDes):
            findInNotDestroyed = GeoMath.getConnectedPrims(prim, setNotDestroyed)
            matchNotDes = (findInNotDestroyed != [])
        if(not matchTotDes):
            findInTotDestroyed = GeoMath.getConnectedPrims(prim, setTotDestroyed)
            matchTotDes = (findInTotDestroyed != [])
        logging.debug("With prim %s, matchNotDes: %s, matchTotDes: %s", str(prim.number()), str(matchNotDes), str(matchTotDes))
        if(matchNotDes or matchTotDes):
            return matchNotDes, matchTotDes
        else:
            tempfind = []
            findInPartiallyDestroyed = GeoMath.getConnectedPrims(prim, currentPartiallyDestroyed)
            for primInPartiallyDestroyed in findInPartiallyDestroyed:
                if(primInPartiallyDestroyed not in self.path):
                    tempfind.append(primInPartiallyDestroyed)
            findInPartiallyDestroyed = list(tempfind)
            index = 0
            while(index < len(findInPartiallyDestroyed) and not matchNotDes and not matchTotDes):
                curPrim = findInPartiallyDestroyed[index]
                if(curPrim in currentPartiallyDestroyed):
                    logging.debug("with prim %s pass to %s", str(prim.number()), str(curPrim.number()))
                    currentPartiallyDestroyed.remove(curPrim)
                    matchNotDes, matchTotDes = self.findSomeGroupRecursively(curPrim, setNotDestroyed, currentPartiallyDestroyed, setTotDestroyed)
                index += 1
        return matchNotDes, matchTotDes


    def getPrimsSharingGroupOfEdges(self, prim, setNotDestroyed, setPartiallyDestroyed, setTotDestroyed):
        validPrim1 = None
        validPrim2 = None
        if(self.isThisPrimMaybeValid(prim)):
            primsSharedInPathSet = GeoMath.getConnectedPrims(prim, self.path)
            primsSharedInGeneral = GeoMath.getConnectedPrims(prim, setPartiallyDestroyed)
            primsSharedInGeneral.extend(GeoMath.getConnectedPrims(prim, setNotDestroyed))
            primsSharedInGeneral.extend(GeoMath.getConnectedPrims(prim, setTotDestroyed))
            setOfEdgesToTrack = []
            for primSharedInGeneral in primsSharedInGeneral:
                setOfEdgesToTrack.extend(GeoMath.getEdgesBetweenPrims(prim, primSharedInGeneral))
            excluded = []
            for primSharedPath in primsSharedInPathSet:
                edgesSharedWithPrim = GeoMath.getEdgesBetweenPrims(primSharedPath, prim)
                excluded.extend(edgesSharedWithPrim)

            #We need some first edge and last edge for track edges between this edges, excluding edges
            #(included in group "excluded") in other prims that share some edge with central prim
            indexPrim = self.path.index(prim)
            if(indexPrim == 0):
                prevIndexPrim = len(self.path) - 1
            else:
                prevIndexPrim = indexPrim - 1
            edgesSharedWithPrim1 = GeoMath.getEdgesBetweenPrims(self.path[(indexPrim + 1) % len(self.path)], prim)
            edgesSharedWithPrim2 = GeoMath.getEdgesBetweenPrims(self.path[prevIndexPrim], prim)
            logging.debug("edges shared curPrim1: %s with prim: %s, edges: %s", str(self.path[(indexPrim + 1) % len(self.path)].number()), str(prim.number()), str(edgesSharedWithPrim1))
            logging.debug("edges shared curPrim2: %s with prim: %s, edges: %s", str(self.path[prevIndexPrim].number()), str(prim.number()), str(edgesSharedWithPrim2))
            groupEdges1, groupEdges2 = GeoMath.trackEdges(edgesSharedWithPrim1[0], setOfEdgesToTrack, edgesSharedWithPrim2[0], excluded)

            #Find two good prims containing one of the group of edges
            index = 0
            while(index < len(primsSharedInGeneral) and not (validPrim1 and validPrim2)):
                curPrim = primsSharedInGeneral[index]
                conEdges = GeoMath.getEdgesBetweenPrims(curPrim, prim)
                if(not validPrim1):
                    for edge in groupEdges1:
                        if(GeoMath.sameEdge(conEdges[0], edge)):
                            validPrim1 = curPrim
                        break
                if (not validPrim2):
                    for edge in groupEdges2:
                        if(GeoMath.sameEdge(conEdges[0], edge)):
                            validPrim2 = curPrim
                        break
                index += 1
        return validPrim1, validPrim2

    def tryToCollapseTwoTrianglesInOneQuad(self, prim, path):
        index = 0
        while(index < len(path) and path[index] != prim):
            index += 1
        if (index == len(path)):
            #If error ocurred and no prim mathched
            return None
        nextPrim = (index + 1) % len(path)
        if(index != 0):
            previousPrim = len(path) - 1
        else:
            previousPrim = index - 1
        nextPrimEdges = GeoMath.getEdgesFromPrim(path[nextPrim])
        previousPrimEdges = GeoMath.getEdgesFromPrim(path[previousPrim])
        if(len(nextPrimEdges) >= 3 and len(previousPrimEdges) >= 3):
            return None
        else:
            #Case when we can to collapse two connected triangles
            #NOT IMPLEMENTED YET
            pass

    '''
    This function do a filtering deleting prim that not have at least some prims in groups like
    not destroyed, partially destroyed, totatlly destroyed. But this not ensures that the prim
    is valid
    '''
    def isThisPrimMaybeValid(self, prim):
        # Has each edge of prim a connected prim? if not, track edges will not work!, so the prim
        # will not valid
        allGroups = []
        allGroups.extend(self.setNotDestroyed)
        allGroups.extend(self.setPartiallyDestroyed)
        allGroups.extend(self.setTotDestroyed)
        edgesHavingPrimitiveConnected = len(GeoMath.getConnectedPrimsOneForEachEdge(prim, allGroups))
        connectedWithNot = len(GeoMath.getConnectedPrims(prim, self.setNotDestroyed, 1))
        connectedWithTot = len(GeoMath.getConnectedPrims(prim, self.setTotDestroyed, 1))
        connectedWithPartially = len(GeoMath.getConnectedPrimsOneForEachEdge(prim, self.setPartiallyDestroyed))
        connectedWithPath = len(GeoMath.getConnectedPrimsOneForEachEdge(prim, self.path))
        #Prim must to acomplished that the number of connected with partially destroyed plus
        #connected with not destroyed plus connected with totally destroyed minus connecte with path
        #must to be greater than 2 primitives (at least two wanted primitives to do recursion after)
        logging.debug("Method isThisPrimMaybeValid, prim %s , with:", str(prim.number()))
        logging.debug("Connected with not: %s, connected with tot: %s, connected with partially: %s, connected with path: %s, edges having primitive: %s",
                      str(connectedWithNot), str(connectedWithTot), str(connectedWithPartially), str(connectedWithPath), str(edgesHavingPrimitiveConnected))
        return (((connectedWithPartially + connectedWithTot + connectedWithNot - connectedWithPath) >= 2) and (edgesHavingPrimitiveConnected == len(GeoMath.getEdgesFromPrim(prim))))

    def getisValid(self):
        return self.valid

