# -*- coding: utf-8 -*-
import logging
import math
import random

import DetermineVectors
from ExternalClasses import GeoMath
import Validator
epsilon = 0.001
primnumber = 51
class AutoPattern(object):
    '''
    Automates the process of get the best pattern
    '''
    def __init__(self, currentPoint, nextPoint, setClass, prim, wavelenght,
                patternCrack, tbn, tbnInverse, pointWhichIsRelative, texture, texturePrim):
        reload (DetermineVectors)
        reload (GeoMath)
        reload (Validator)
        self.wavelength = wavelenght
        self.type = setClass
        if(not setClass.is_dynamic()):
            self.pattern = self.findBestPattern(currentPoint, nextPoint, setClass,
                            prim, patternCrack, tbn, tbnInverse,
                            pointWhichIsRelative, texture, texturePrim)
        else:
            self.pattern = self.findBestPatternDynamic(currentPoint, nextPoint,
                            setClass, prim, patternCrack, tbn, tbnInverse,
                            pointWhichIsRelative, texture, texturePrim)
    #NOT USED!!!! Now we use TBN matrix
    def convertVector(self, normal):
        logging.debug("Start method convertVector, class AutoPattern")
        global epsilon
        #Convert vector to the plane x,y
        #Convert it in a matrix vector
        normal.append(0)
        logging.debug("Normal in convertVector %s", str(normal))
        if(not(math.fabs(normal[0]) < epsilon and math.fabs(normal[1]) < epsilon)):
            '''
            Transformations for moving a vector to the z-axis
            '''
            #The matrix to rotate a vector about the  z-axis to the  xz-plane is
            Rxz = GeoMath.Matrix(4, 4)
            Rxz[0, 0] = normal[0] / math.sqrt(pow(normal[0], 2) + math.pow(normal[1], 2))
            Rxz[0, 1] = -normal[1] / math.sqrt(pow(normal[0], 2) + math.pow(normal[1], 2))
            Rxz[1, 0] = normal[1] / math.sqrt(pow(normal[0], 2) + math.pow(normal[1], 2))
            Rxz[1, 1] = normal[0] / math.sqrt(pow(normal[0], 2) + math.pow(normal[1], 2))
            #The matrix to rotate the vector in the xz-plane to the  z-axis is
            Rz = GeoMath.Matrix(4, 4)
            Rz[0, 0] = normal[2] / math.sqrt(math.pow(normal[0], 2) + math.pow(normal[1], 2) + math.pow(normal[2], 2))
            Rz[0, 2] = math.sqrt(pow(normal[0], 2) + math.pow(normal[1], 2)) / math.sqrt(math.pow(normal[0], 2) + math.pow(normal[1], 2) + math.pow(normal[2], 2))
            Rz[2, 0] = -math.sqrt(pow(normal[0], 2) + math.pow(normal[1], 2)) / math.sqrt(math.pow(normal[0], 2) + math.pow(normal[1], 2) + math.pow(normal[2], 2))
            Rz[2, 2] = normal[2] / math.sqrt(math.pow(normal[0], 2) + math.pow(normal[1], 2) + math.pow(normal[2], 2))
            vectorRotated = Rxz.mulPoint4ToMatrix4(normal)
            vectorRotated = Rz.mulPoint4ToMatrix4(vectorRotated)
            vectorRotated.pop()
        else:
            logging.debug("convertVector normal por else")
            vectorRotated = list(normal)
            Rxz = GeoMath.Matrix(4, 4)
            Rz = GeoMath.Matrix(4, 4)

        normal.pop()
        logging.debug("End method convertVector, class AutoPattern")
        return Rxz, Rz

    def translatePointToPrim(self, point, trans):
            pointCon = list(point)
            pointCon.append(1)
            trans.append(1)
            Rtrans = GeoMath.Matrix(4, 4)
            Rtrans.matrix4Trans(trans)
            pointCon = Rtrans.mulPoint4ToMatrix4(pointCon)#Delete the last element
            pointCon.pop()
            return pointCon

    def goToPrimPattern(self, curPoint, nextPoint, pat, tbn, pointWhichIsRelative):
        '''
        TBN aplication
        '''
        global epsilon
        for num in range(len(pat.points)):
            pat.points[num] = tbn.mulPoint3ToMatrix3(pat.points[num])
            pat.points[num] = GeoMath.vecPlus(pointWhichIsRelative, pat.points[num])
        #Transform normal vector also
        logging.debug("Changing normal" + str(pat.getNormal()))
        transformed_normal = tbn.mulPoint3ToMatrix3(pat.getNormal())
        logging.debug("Transformed normal" + str(transformed_normal))
        normalized_normal = GeoMath.vecNormalize(transformed_normal)
        logging.debug("normalized normal" + str(normalized_normal))
        pat.setNormal(normalized_normal)
        logging.debug("normalized normal set?? " + str(pat.getNormal()))
        trans = GeoMath.vecSub(curPoint, pat.getFirstPoint())
        likelyPointF = GeoMath.vecPlus(pat.getLastPoint(), trans)
        if(GeoMath.vecModul(GeoMath.vecSub(likelyPointF, nextPoint)) > epsilon):
            trans = GeoMath.vecSub(curPoint, pat.getLastPoint())

        for num in range(len(pat.getPoints())):
            pat.points[num] = self.translatePointToPrim(pat.points[num], trans)

        if(GeoMath.vecModul(GeoMath.vecSub(likelyPointF, nextPoint)) > epsilon):
            pat.points.reverse()


    def valPattern(self, curPoint, nextPoint, pat, tbn, pointWhichIsRelative, prim, patternCrack, texture, texturePrim):
        '''
                        if(prim.number()==primnumber):
                    h=HouInterface.HouInterface(hou.node('obj/example_CGAShape_compatible'))
                    h.showCurve(pat.points, 'patttt')
        '''
        global primnumber
        logging.debug("Start method valPattern, class Autopattern")
        self.goToPrimPattern(curPoint, nextPoint, pat, tbn, pointWhichIsRelative)
        #################################
        c = Validator.Validator.patternInsidePrim(pat, prim)
        if(not c):
            logging.debug("Points of pattern outside prim in prim: %s", str(prim.number()))
            return False
        c = Validator.Validator.patternInsideTexture(pat, prim, texture, texturePrim)

        if(not c):
            logging.debug("Points of pattern outside of texture: %s", str(prim.number()))
            return False
        #To avoid the first pattern we ask if the prim has already added to the list of prims
        #with patterns
        if((prim in patternCrack.keys())):
            c = Validator.Validator.patternWithPatternsInPrim(pat, patternCrack[prim], prim)

            #c = Validator.Validator.patternWithPatternsInPrim(pat, patternCrack[prim], prim)
            if(not c):
                logging.debug("Pattern intersect other pattern in the same primitive")
                return False

        c = Validator.Validator.patternPrimWithNeigborsPatternsPrims(pat, prim, patternCrack)
        if(not c):
            logging.debug("Pattern intersect with other patterns in other primitives, prim: %s", str(prim.number()))
            logging.debug("End method valPattern, class Autopattern. State: Falla in others")
            return False

        logging.debug("End method valPattern, class Autopattern")
        return c


    def getPossiblePatterns(self, curPoint, nextPoint, setClass, epsilon, setPat, vector, vectorRotated, pat):
        match = False
        goodPattern = None
        copyPat = pat.copy()
        vecPat = GeoMath.vecSub(copyPat.points[len(copyPat.points) - 1], copyPat.points[0])
        vecPatIn = GeoMath.vecSub(copyPat.points[0], pat.points[len(copyPat.points) - 1])
        logging.debug("Index pat %s", str(setPat.index(pat)))
        logging.debug("Vectors")
        logging.debug("Vector in prim %s", str(vector))
        logging.debug("Pattern vector %s", str(vecPat))
        logging.debug("Vector rotated %s", str(vectorRotated))
        logging.debug("Curpooint %s", str(curPoint))
        logging.debug("NextPoint %s", str(nextPoint))
        #Same length
        if (math.fabs(GeoMath.vecModul(vecPat) - GeoMath.vecModul(vectorRotated)) < epsilon):
            rest = GeoMath.vecSub(vectorRotated, vecPat)
            restIn = GeoMath.vecSub(vectorRotated, vecPatIn)
            #Same direction
            if ((GeoMath.vecModul(rest) < epsilon) or (GeoMath.vecModul(restIn) < epsilon)):
                goodPattern = copyPat
                match = True #No same direction
            if (match == False):
                '''
            See simetry in this order:
            1-rot in z
            2-rot in y
            3-rot in x
            '''
                anglez = setClass.getRotz()
                if (anglez != 0):
                    Rzva = GeoMath.Matrix(4, 4)
                    Rzva.singleRotz(anglez)
                    copyVecPat = list(vecPat)
                    copyVecPat.append(0)
                    numRotations = 0
                    if (anglez == 0):
                        maxRot = 0
                    else:
                        maxRot = (360 / anglez) - 1
                    while numRotations < (maxRot) and not match:
                        copyVecPat = Rzva.mulPoint4ToMatrix4(copyVecPat) #Not necesary to delete the last number in vector(which added for homogeneous)
                        restRz = GeoMath.vecSub(copyVecPat, vectorRotated)
                        restInRz = GeoMath.vecSub(GeoMath.vecSub([0, 0, 0], copyVecPat), vectorRotated)
                        numRotations += 1

                    if ((numRotations <= maxRot) and (GeoMath.vecModul(restRz) < epsilon or GeoMath.vecModul(restInRz) < epsilon)):
                        anglezTot = numRotations * anglez
                        copyPat.rotatePattern([0, 0, 1], anglezTot)
                        goodPattern = copyPat
                        match = True
                #Rotation in y if in z is not valid
                simRoty = setClass.getSimY(copyPat)
                if (not match and simRoty):
                    Ry = GeoMath.Matrix(4, 4)
                    Ry.singleRoty(180)
                    copyVecPat = list(vecPat)
                    copyVecPatIn = list(vecPatIn)
                    copyVecPat.append(0)
                    copyVecPatIn.append(0)
                    copyVecPat = Ry.mulPoint4ToMatrix4(copyVecPat)
                    copyVecPatIn = Ry.mulPoint4ToMatrix4(copyVecPatIn) #Not necesary to delete the last number in vector(which added for homogeneous)
                    restRy = GeoMath.vecSub(copyVecPat, vectorRotated)
                    restRyIn = GeoMath.vecSub(copyVecPatIn, vectorRotated)
                    if (GeoMath.vecModul(restRy) < epsilon or (GeoMath.vecModul(restRyIn) < epsilon)):
                        copyPat.rotatePattern([0, 1, 0], 180)
                        goodPattern = copyPat
                        match = True #Rotation in x if in z neither y is valid
                simRotx = setClass.getSimX(copyPat)
                if (not match and simRotx):
                    Rx = GeoMath.Matrix(4, 4)
                    Rx.singleRotx(180)
                    copyVecPat = list(vecPat)
                    copyVecPatIn = list(vecPatIn)
                    copyVecPat.append(0)
                    copyVecPatIn.append(0)
                    copyVecPat = Rx.mulPoint4ToMatrix4(copyVecPat)
                    copyVecPatIn = Rx.mulPoint4ToMatrix4(copyVecPatIn) #Not necesary to delete the last number in vector(which added for homogeneous)
                    restRx = GeoMath.vecSub(copyVecPat, vectorRotated)
                    restRxIn = GeoMath.vecSub(copyVecPatIn, vectorRotated)
                    if (GeoMath.vecModul(restRx) < epsilon or (GeoMath.vecModul(restRxIn) < epsilon)):
                        copyPat.rotatePattern([1, 0, 0], 180)
                        goodPattern = copyPat
                        match = True
        return goodPattern

    def validateAndAdjustPatterns(self, curPoint, nextPoint, setClass, prim,
                                   patternCrack, tbn, pointWhichIsRelative,
                                    texture, texturePrim, pat):
        match = False
        validatedPattern = None
        goodCopyPat = pat.copy()
        if (self.valPattern(curPoint, nextPoint, goodCopyPat, tbn,
                             pointWhichIsRelative, prim, patternCrack,
                              texture, texturePrim)):
            validatedPattern = goodCopyPat
            match = True #If not valid we try to rotate about direction of pattern (firsPoint-lastPoint)
        goodCopyPat = pat.copy()
        if (not match and setClass.getSimDir(pat)):

            goodCopyPat.rotatePattern(dir, 180)
            if (self.valPattern(curPoint, nextPoint, goodCopyPat, tbn,
                                 pointWhichIsRelative, prim, patternCrack,
                                  texture, texturePrim)):
                validatedPattern = goodCopyPat
                match = True #If not valid we try to rotate about normal
        goodCopyPat = pat.copy()
        if (not match and setClass.getSimNormal(pat)):
            nor = goodCopyPat.getNormal()
            goodCopyPat.rotatePattern(nor, 180)
            if (self.valPattern(curPoint, nextPoint, goodCopyPat, tbn,
                                 pointWhichIsRelative, prim, patternCrack,
                                  texture, texturePrim)):
                validatedPattern = goodCopyPat
                match = True

        return validatedPattern

    def findBestPattern(self, curPoint, nextPoint, setClass, prim, patternCrack,
                         tbn, tbnInverse, pointWhichIsRelative, texture, texturePrim):
        logging.debug("Start method finBestPattern, class Autopattern")
        global epsilon
        global primnumber
        setPat = setClass.getPatternsWavelength(self.wavelength)
        #We have to convert vector, because the patterns are defined into positive xy plane
        goodPatterns = []
        vector = GeoMath.vecSub(nextPoint, curPoint)
        vectorRotated = tbnInverse.mulPoint3ToMatrix3(vector)
        for pat in setPat:
            goodPattern = self.getPossiblePatterns(curPoint, nextPoint, setClass,
                                                    epsilon, setPat, vector,
                                                     vectorRotated, pat)
            if(goodPattern):
                goodPatterns.append(goodPattern)

        #Validate patterns with prim
        validatedPatterns = []
        for pat in goodPatterns:
            validatedPattern = self.validateAndAdjustPatterns(
                                           curPoint, nextPoint, setClass, prim,
                                            patternCrack, tbn, pointWhichIsRelative,
                                            texture, texturePrim, pat)
            if(validatedPattern):
                validatedPatterns.append(validatedPattern)

        if(not validatedPatterns):
            #Apply the joker pattern!
            vecH, vecV = DetermineVectors.DetermineVectors.detVec(prim, GeoMath.vecSub(nextPoint, curPoint), [0, 0, 1])
            validatedPatterns.append(setClass.applyJoker(curPoint, nextPoint, vecH, vecV))
            logging.debug("End method finBestPattern, class Autopattern. State: Joker applied")
        else:
            logging.debug("End method finBestPattern, class Autopattern. State: good")

        return validatedPatterns[random.randint(0, len(validatedPatterns) - 1)]

    def findBestPatternDynamic(self, curPoint, nextPoint, setClass, prim, patternCrack, tbn, tbnInverse, pointWhichIsRelative, texture, texturePrim):
        '''
        Get the best dynamic pattern
        
        @param curPoint:
        @type curPoint:
        @param nextPoint:
        @type nextPoint:
        @param setClass:
        @type setClass:
        @param prim:
        @type prim:
        @param patternCrack:
        @type patternCrack:
        @param tbn:
        @type tbn:
        @param tbnInverse:
        @type tbnInverse:
        @param pointWhichIsRelative:
        @type pointWhichIsRelative:
        @param texture:
        @type texture:
        @param texturePrim:
        @type texturePrim:
        '''
        logging.debug('Class AutoPattern, method findBestPatternDinamically')
        logging.debug('cur_point: ' + str(curPoint) + "next_point: " + str(nextPoint))

        #Direction of the crack
        vector = GeoMath.vecSub(nextPoint, curPoint)
        vector_rotated = tbnInverse.mulPoint3ToMatrix3(vector)
        logging.debug("vector_rotated: " + str(vector_rotated))
        #Number of attemps to try to find a good pattern
        attempts = 2
        #Get a pattern generated dynamically
        #TODO: wavelength now only 0, but it can be any number
        wavelenght = 0
        first_point = [0, 0, 0]
        #Calculate normal of pattern
        direction = GeoMath.vecNormalize(GeoMath.vecSub(vector_rotated, first_point))
        normal_of_pattern = GeoMath.vecCrossProduct(list(prim.normal()), direction)
        pattern = setClass.getRandomPattern(wavelenght, first_point, vector_rotated, normal_of_pattern)
        validatedPattern = self.validateAndAdjustPatterns(curPoint, nextPoint, setClass, prim, patternCrack, tbn, pointWhichIsRelative, texture, texturePrim, pattern)

        if(not validatedPattern):
            #Try 10 times variing random offset(seed) in the noise function to get a valid pattern
            for _ in range(attempts):
                pattern = setClass.getRandomPattern(wavelenght, first_point, vector_rotated, normal_of_pattern)
                validatedPattern = self.validateAndAdjustPatterns(curPoint, nextPoint, setClass, prim, patternCrack, tbn, pointWhichIsRelative, texture, texturePrim, pattern)
                if(validatedPattern):
                    break

        if(not validatedPattern):
            #Try "attemps" times varying the random offset(seed) of the noise funcion and do the height little to
            #increase posibilities to get a valid pattern
            height = setClass.getSizey() / 2
            reduction_height = 2
            for _ in range(attempts):
                pattern = setClass.getRandomPattern(wavelenght, first_point, vector_rotated, normal_of_pattern, height)

                validatedPattern = self.validateAndAdjustPatterns(curPoint, nextPoint, setClass, prim, patternCrack, tbn, pointWhichIsRelative, texture, texturePrim, pattern)
                #Make the height half, for get more possibilities to do a good pattern
                height = height / reduction_height
                if(validatedPattern):
                    break
        if(not validatedPattern):
            #Apply the joker pattern!
            vecH, vecV = DetermineVectors.DetermineVectors.detVec(prim, GeoMath.vecSub(nextPoint, curPoint), [0, 0, 1])
            validatedPattern = setClass.applyJoker(curPoint, nextPoint, vecH, vecV)
            logging.debug("End method finBestPatternDynamic, class Autopattern. State: Joker applied")
        else:
            logging.debug("End method finBestPatternDynamic, class Autopattern. State: good")

        return validatedPattern

