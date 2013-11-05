# -*- coding: utf-8 -*-
# DEPREATED, use instead the base class crack and make a new type of crack builder

from lib import GeoMath
from lib import HouInterface
from lib import UIProcessStatus
from lib.CDF import CDF
import AutoPattern
import Bresenham
import Data
import DetermineVectors
import InfoPathPrim
import cmath
import logging
import math

HouInter = None
epsilon = 0.001
primnumber = 31
NUMITER = 0


# _Class to manage a crack_#
class Crack(object):

    def __init__(self):
        global HouInter
        reload(AutoPattern)
        reload(Bresenham)
        reload(Data)
        reload(GeoMath)
        reload(HouInterface)
        reload(InfoPathPrim)
        self.patternCrack = {}
        self.IPrimPoint = []
        self.linePerPrim = {}
        self.HI = None
        self.showCrackNodes = []
        self.intersectionPoints = []

    #==========================================================================
    # doCrack
    #==========================================================================
    def doCrack(self, texture, infoPreviousPrim, infoPrim, infoNextPrim):
        logging.debug("Start method doCrack, class Crack")
        reload(AutoPattern)
        reload(Bresenham)
        reload(Data)
        reload(GeoMath)
        reload(HouInterface)
        reload(InfoPathPrim)
        prim = infoPrim.getPrim()
        previousPrim = infoPreviousPrim.getPrim()
        nextPrim = infoNextPrim.getPrim()
        logging.debug("PRIMS")
        logging.debug("Previous prim: %s", str(previousPrim.number()))
        logging.debug("Previous iPoint: %s", str(infoPreviousPrim.getiPoint()))
        logging.debug("Previous fPoint: %s", str(infoPreviousPrim.getfPoint()))
        logging.debug("This prim: %s", str(prim.number()))
        logging.debug("This prim iPoint: %s", str(infoPrim.getiPoint()))
        logging.debug("This prim fPoint: %s", str(infoPrim.getfPoint()))
        logging.debug("Next prim: %s", str(nextPrim.number()))
        logging.debug("Next prim iPoint: %s", str(infoNextPrim.getiPoint()))
        logging.debug("Next prim fPoint: %s", str(infoNextPrim.getfPoint()))

        Ipoint = list(infoPrim.getiPoint())
        finalPoint = list(self.defFpoint(infoPrim, nextPrim))
        self.defCrack(prim, Ipoint, finalPoint, texture)

        if(len(self.patternCrack.keys()) > 3):
            logging.debug("End method doCrack, class Crack. State: good")
        else:
            logging.debug("End method doCrack, class Crack. State: length of path < 4")

    #===========================================================================
    # defCrack
    #===========================================================================
    def defCrack(self, prim, Ipoint, Fpoint, texturePrim):
        reload(AutoPattern)
        reload(Bresenham)
        reload(Data)
        reload(GeoMath)
        reload(HouInterface)
        global epsilon
        global primnumber
        # TEMP: only for debug the patterns
        # Size x and size y is the valor of some material with the minor wavelength(bigger pattern)
        curPoint = Ipoint
        self.patternCrack[prim] = []
        vertices = [list(p.point().position()) for p in prim.vertices()]
        print "vertices"
        print vertices
        # Convert prim to tangent space of patterns
        # Get some arbitrary vectors conected from vertices of prim
        vec1 = GeoMath.vecSub(vertices[0], vertices[1])
        vec2 = GeoMath.vecSub(vertices[2], vertices[1])
        # We have to know which angle reside between the two coencted vectors, to know if suposed vectors
        # in tangent space will be correct
        angle = GeoMath.vecDotProduct(vec1, vec2) / (GeoMath.vecModul(vec1) * GeoMath.vecModul(vec2))
        angle = math.acos(angle)
        angle = math.degrees(angle)

        # We put relative one arbitrary point to tangent space
        pointWhichIsRelative = vertices[1]
        # Determine x and y vectors, now we'll have suposed horizontal and vertical vectors acording to
        # prim and direction of the crack

        vecH, vecV = DetermineVectors.DetermineVectors.detVec(prim, GeoMath.vecSub(Ipoint, Fpoint), [0, 0, 1])
        # CHAPUZA CON NUMEROS COMPLEJOS!!! Precision de python pésima, 1.000000001>1?? no! y math.acos error

        cosAngle = GeoMath.vecDotProduct(vecH, vec1) / (GeoMath.vecModul(vec1) * GeoMath.vecModul(vecH))
        complexAngle = cmath.acos(cosAngle)
        if(complexAngle.imag == 0):
            angleBetweenDetVecAndVecH = math.acos(cosAngle)
        else:
            if(cosAngle < 0):
                angleBetweenDetVecAndVecH = math.acos(-1)
            else:
                angleBetweenDetVecAndVecH = math.acos(1)

        #=======================================================================
        # Now we have to ensure that the vec1 has the same direction that the horizontal vector, if not, we
        # change and the horizontal vector will be vec2. Also we have to check if the prim is not a quad,
        # in this case we have to get the vertical vector from horizontal vector, rotating the known angle
        # between the two vectors conected in prim (in quad we know that the angle is 90 and we already have the
        # good vectors)
        #=======================================================================
        print "Create TBN"
        if((math.fabs(angleBetweenDetVecAndVecH) < epsilon) or (math.fabs(angleBetweenDetVecAndVecH) > (math.pi - epsilon))):
            x = GeoMath.vecScalarProduct([1, 0, 0], GeoMath.vecModul(vec1))
            y = GeoMath.rotateVecByVec(x, [0, 0, 1], angle)
            y = GeoMath.vecScalarProduct(GeoMath.vecNormalize(y), GeoMath.vecModul(vec2))
            tbn = GeoMath.createTBNmatrix(vertices[0], vertices[1], vertices[2], x, [0, 0], y)
        else:
            x = GeoMath.vecScalarProduct([1, 0, 0], GeoMath.vecModul(vec2))
            y = GeoMath.rotateVecByVec(x, [0, 0, 1], angle)
            y = GeoMath.vecScalarProduct(GeoMath.vecNormalize(y), GeoMath.vecModul(vec1))
            tbn = GeoMath.createTBNmatrix(vertices[0], vertices[1], vertices[2], y, [0, 0], x)

        print "Edn create tbn"
        tbnInverse = GeoMath.Matrix(3, 3)
        tbnInverse.copy(tbn)
        tbnInverse.matrix3Inverse()

        # Get the first material:
        print "texture get first layer"
        texture = texturePrim.getFirstLayer(Ipoint)
        nextMaterial = texture.get_material()
        print "end get material"
        # Create status of the process to show to the user
        distance_to_complete = GeoMath.vecModul(GeoMath.vecSub(curPoint, Fpoint))
        ui_process_status = UIProcessStatus.UIProcessStatus('crack for prim',
                                                                distance_to_complete)
        while(GeoMath.vecModul(GeoMath.vecSub(curPoint, Fpoint)) > epsilon):
            # Print status of the process
            dist = GeoMath.vecModul(GeoMath.vecSub(curPoint, Fpoint))
            ui_process_status.calculate_status(dist, inverse=True)
            ui_process_status.print_status()

            genPattern = Data.GeneralPattern()
            for wavelength in nextMaterial.mat.keys():
                singleMat = nextMaterial.mat[wavelength]
                setOfTypeOfPattern = CDF.cdf([[singleMat.classesAndPercentage[k], k] for k in singleMat.classesAndPercentage.keys()])
                if(wavelength == 0):
                    nextPoint = Bresenham.Bresenham.bresenham(Ipoint, curPoint, Fpoint, setOfTypeOfPattern.getSizex(), setOfTypeOfPattern.getSizey(), prim, [1, 0, 0])
                    pat = AutoPattern.AutoPattern(curPoint, nextPoint, setOfTypeOfPattern, prim, wavelength, self.patternCrack, tbn, tbnInverse, pointWhichIsRelative, texture, texturePrim).pattern
                genPattern.applyPattern(pat, wavelength)

            # Check texture
            previousTexture = texture
            pii, texture = self.checkTexture(texturePrim, previousTexture, genPattern, Fpoint, nextPoint)
            logging.debug('Pii defcrack: ' + str(pii))
            logging.debug('CurPoint defcrack: ' + str(curPoint))
            logging.debug('genPattern ' + str(genPattern.getPoints()))
            '''
            if(not curPoint):
                curPoint=genPattern.getLastPoint()
            '''
            curPoint = genPattern.getLastPoint()
            if(texture):
                nextMaterial = texture.get_material()
            else:
                if(not (GeoMath.vecModul(GeoMath.vecSub(curPoint, Fpoint)) > epsilon)):
                    logging.error('Texture no matched, previous texture applied')
            # version 4
            self.patternCrack[prim].append(genPattern)

    def getSample(self, Ipoint, curPoint, Fpoint, xSize, ySize, prim):
        sample = Bresenham.Bresenham.bresenham(Ipoint, curPoint, Fpoint, xSize, ySize, prim, [1, 0, 0])
        return sample

    def getFirstPoint(self, prim):
        return self.patternCrack[prim].listOfPatterns[0].getPoints[0]

    def showCrack(self, node, groupOfInfoPrimsOrdered, allInOne):
        groupOfPrimsOrdered = InfoPathPrim.convertListFromInfoPrimToPrim(groupOfInfoPrimsOrdered)
        for countPrim in range(len(groupOfPrimsOrdered)):
            pointsString = ""
            prim = groupOfPrimsOrdered[countPrim]
            if(allInOne):
                crackNode = node.createNode('curve', 'crack_patternPrim_' + str(prim.number()))
                if(prim in self.linePerPrim):
                    listOfPoints = self.linePerPrim[prim]
                for point in listOfPoints:
                    pointsString = pointsString + str(point[0]) + "," + str(point[1]) + "," + str(point[2]) + " "
                crackNode.parm('coords').set(pointsString)
                crackNode.moveToGoodPosition()
                crackNode.setTemplateFlag(True)
                self.showCrackNodes.append(crackNode)
            else:
                count = 0
                if(prim in self.patternCrack):
                    for patt in self.patternCrack[prim]:
                    # Show crack
                        crackNode = node.createNode('curve', 'crack_pattern_' + str(prim.number()) + "_" + str(count))
                        pointsString = ""
                        for point in patt.getPoints():
                            pointsString = pointsString + str(point[0]) + "," + str(point[1]) + "," + str(point[2]) + " "
                        crackNode.parm('coords').set(pointsString)
                        crackNode.moveToGoodPosition()
                        crackNode.setTemplateFlag(True)
                        self.showCrackNodes.append(crackNode)
                        count += 1

    def deleteShowCrackNodes(self):
        for node in self.showCrackNodes:
            node.destroy()
        self.showCrackNodes = []

    def showTextureIntersections(self, geo):
        if(not self.HI):
            self.HI = HouInterface.HouInterface(geo=geo)
        for point in self.intersectionPoints:
            self.HI.showPoint(point=point, name='inter_point')

    def deleteShowTextureIntersectionNodes(self):
        if(self.HI):
            self.HI.deletePoints()

    def doLineCrackPerPrim(self, groupOfInfoPrimsOrdered):
        groupOfPrimsOrdered = InfoPathPrim.convertListFromInfoPrimToPrim(groupOfInfoPrimsOrdered)
        for prim in groupOfPrimsOrdered:
            self.linePerPrim[prim] = []
            if(prim in self.patternCrack):
                for patt in self.patternCrack[prim]:
                    for point in patt.getPoints():
                            self.linePerPrim[prim].append(point)

        #=======================================================================
        #
        # for countPrim in range(len(groupOfPrimsOrdered)):
        #    prim = groupOfPrimsOrdered[countPrim]
        #    self.linePerPrim[prim] = []
        #    prevPrim = groupOfPrimsOrdered[countPrim - 1]
        #    listOfPatterns = self.patternCrack[prim]
        #    listOfPatternsPrev = self.patternCrack[prevPrim]
        #    if(countPrim == 0):
        #        firstp = listOfPatterns[0].getFirstPoint()
        #        finalp = listOfPatterns[0].getLastPoint()
        #        pFlast = listOfPatternsPrev[0].getLastPoint()
        #        pFfirst = listOfPatternsPrev[0].getFirstPoint()
        #        pIlast = listOfPatternsPrev[len(listOfPatternsPrev) - 1].getLastPoint()
        #        pIfirst = listOfPatternsPrev[len(listOfPatternsPrev) - 1].getFirstPoint()
        #        resttpFl = GeoMath.vecModul(GeoMath.vecSub(firstp, pFlast))
        #        resttpFf = GeoMath.vecModul(GeoMath.vecSub(firstp, pFfirst))
        #        resttpIl = GeoMath.vecModul(GeoMath.vecSub(firstp, pIlast))
        #        resttpIf = GeoMath.vecModul(GeoMath.vecSub(firstp, pIfirst))
        #        restlpFl = GeoMath.vecModul(GeoMath.vecSub(finalp, pFlast))
        #        restlpFf = GeoMath.vecModul(GeoMath.vecSub(finalp, pFfirst))
        #        restlpIl = GeoMath.vecModul(GeoMath.vecSub(finalp, pIlast))
        #        restlpIf = GeoMath.vecModul(GeoMath.vecSub(finalp, pIfirst))
        #        minim = min(resttpFl, resttpFf, resttpIl, resttpIf, restlpFl, restlpFf, restlpIl, restlpIf)
        #        if(minim == resttpFl or minim == restlpFl):
        #            lastP = pFlast
        #        elif(minim == resttpFf or minim == restlpFf):
        #            lastP = pFfirst
        #        elif(minim == resttpIl or minim == restlpIl):
        #            lastP = pIlast
        #        elif(minim == resttpIf or minim == restlpIf):
        #            lastP = pIfirst
        #    if(prim in self.patternCrack):
        #        for countPat in range(len(self.patternCrack[prim])):
        #            patt = listOfPatterns[countPat]
        #            if(GeoMath.vecModul(GeoMath.vecSub(patt.getFirstPoint(), lastP)) < GeoMath.vecModul(GeoMath.vecSub(patt.getLastPoint(), lastP))):
        #                for point in patt.getPoints():
        #                    self.linePerPrim[prim].append(point)
        #                lastP = patt.getPoints()[len(patt.getPoints()) - 1]
        #            else:
        #                #Inverse recorrido
        #                rang = range(len(patt.getPoints()))
        #                rang.reverse()
        #                for countPoint in rang:
        #                    point = patt.getPoints()[countPoint]
        #                    self.linePerPrim[prim].append(point)
        #                lastP = patt.getPoints()[0]
        #            countPrim += 1
        #=======================================================================

    def checkTexture(self, texture, previousTexture, genPattern, Fpoint, nextPoint):

        tex, nearestPointIntersect, minDistance = texture.findIntersectionWithNearestTexture(genPattern.getPoints())
        logging.debug("Start method checkTexture, class Crack")
        if(tex):
            logging.debug('nearestPointIntersect: ' + str(nearestPointIntersect) + 'Distance: ' + str(minDistance) + 'Texture: ' + str(tex.get_material().get_name()))
        else:
            logging.debug('nearestPointIntersect: ' + str(nearestPointIntersect) + 'Distance: ' + str(minDistance) + 'No Texture')

        # If we found some interect point we clip the pattern to this point
        if(nearestPointIntersect):
            achieved = genPattern.clipPattern(nearestPointIntersect)
            if(not achieved):
                logging.error("No clipping achieved")
                return None, previousTexture
        else:
            return None, previousTexture
        # Now we have to ensure that the next texture is correct, because possibly the intersection
        # is correct and the next texture in pattern direction is correct, but maybe the direction
        # has changed due to the clipping of the pattern and the point clipped. The direction now is
        # the direction between point clipped-intersected with next texture and the final point of
        # the crack in prim.
        # also, in the NORMAL case, maybe the pattern intersect with his texture, because are exiting
        # from it, so we have to do a point in polygon to search what texture is the next

        # Check texture, for do that get the vector direction and do it little and do a point in
        # polygon with the texture
        nextDir = GeoMath.vecSub(Fpoint, nearestPointIntersect)
        logging.debug('next dir before', str(nextDir))
        if(GeoMath.vecModul(nextDir) > 0):
            nextDir = GeoMath.vecNormalize(nextDir)
            # make it little, not more little than the epsilon used at GeoMath pointInSegmentDistance method,
            # so we use a 10x bigger than epsilon, so 0.05
            nextDir = GeoMath.vecScalarProduct(nextDir, 0.05)
            nextPoint = GeoMath.vecPlus(nextDir, nearestPointIntersect)
            nextTex = texture.findUpperTextureContainingPoint(nextPoint)
            logging.debug('Direction and texture , next point: %s, next direction', str(nextPoint), str(nextDir))
        else:
            nextTex = None
            # We get the final point, so we not have to ensure anything


        logging.debug("End method checkTexture, class Crack")
        if(nearestPointIntersect):
            self.intersectionPoints.append(nearestPointIntersect)
        return nearestPointIntersect, nextTex

############CHANGE THIS METHOD TO GET THE PATH WELL, CHANGE THE EPSILON!!!!!!!!!!!!!#############


    def defFpoint(self, prim, nextPrim):

        global HouInter
        '''
        This method can do more things to choose a good final point
        '''
        return list(prim.getfPoint())

    def getPointsByPrim(self, prim):
        return self.patternCrack[prim].getPoints()

    def recalculate(self):
        pass

    def add_noise_to_crack(self, heigth, frequency, for_edge, wavelength):
        for patterns in self.patternCrack.values():
            for pattern in patterns:
                pattern.add_noise(heigth, frequency, for_edge, wavelength)

class CrackFloor(Crack):
    def __init__(self, infoPath):
        pass