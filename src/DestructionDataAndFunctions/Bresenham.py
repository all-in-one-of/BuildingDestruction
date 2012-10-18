# -*- coding: utf-8 -*-
from ExternalClasses import GeoMath
import DetermineVectors
import Validator
class Bresenham(object):
    @staticmethod
    def bresenham(Ipoint, point1, fPoint, xSize, ySize, prim, exception):
        reload (GeoMath)
        reload (DetermineVectors)
        reload (Validator)
        curPoint = point1
        dirVec = GeoMath.vecNormalize(GeoMath.vecSub(fPoint, Ipoint))
        #Get the horizontal and vertical vectors
        xVec, yVec = DetermineVectors.DetermineVectors.detVec(prim, dirVec, exception)
        xSizeVec = GeoMath.vecScalarProduct(xVec, xSize)
        ySizeVec = GeoMath.vecScalarProduct(yVec, ySize)
        vecToFinal = GeoMath.vecSub(curPoint, fPoint)
        sizeToFinalx = abs(GeoMath.vecDotProduct(vecToFinal, xVec) / GeoMath.vecModul(xVec))
        sizeToFinaly = abs(GeoMath.vecDotProduct(vecToFinal, yVec) / GeoMath.vecModul(yVec))
        if(sizeToFinalx > xSize or sizeToFinaly > ySize):
            pointx = GeoMath.vecPlus(curPoint, xSizeVec)
            pointy = GeoMath.vecPlus(curPoint, ySizeVec)
            pointxy = GeoMath.vecPlus(curPoint, xSizeVec)
            pointxy = GeoMath.vecPlus(pointxy, ySizeVec)
            curxVec = GeoMath.vecNormalize(GeoMath.vecSub(pointx, Ipoint))
            curyVec = GeoMath.vecNormalize(GeoMath.vecSub(pointy, Ipoint))
            curxyVec = GeoMath.vecNormalize(GeoMath.vecSub(pointxy, Ipoint))
            #We get the max dot product, the vector nearest to line
            dotx = GeoMath.vecDotProduct(curxVec, dirVec)
            doty = GeoMath.vecDotProduct(curyVec, dirVec)
            dotxy = GeoMath.vecDotProduct(curxyVec, dirVec)
            pointsTemp = {}
            if(Validator.Validator.pointInsidePrim(pointx, prim)): pointsTemp[dotx] = pointx
            if(Validator.Validator.pointInsidePrim(pointy, prim)): pointsTemp[doty] = pointy
            if(Validator.Validator.pointInsidePrim(pointxy, prim)): pointsTemp[dotxy] = pointxy
            if(not pointsTemp):
                point = list(fPoint)
            else:
                bestPoint = list(pointsTemp[sorted(pointsTemp)[len(pointsTemp) - 1]])
                point = bestPoint
        else:
            point = list(fPoint)
            '''   
            if(prim.number()==54):
            print "Ipoint, fpoint"
            print Ipoint, fPoint
            print "pointx, pointy, pointxy"
            print pointx, pointy, pointxy
            print "Dots"
            print dotx, doty, dotxy
            print "sizes"
            print sizeToFinalx, sizeToFinaly            
            print "Point"
            print point
            '''
        return point
