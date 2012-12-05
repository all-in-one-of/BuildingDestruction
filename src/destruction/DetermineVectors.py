# -*- coding: utf-8 -*-
from ExternalClasses import GeoMath
import math
epsilon = 0.001


class DetermineVectors:
    #TODO: Refactoring without prim dependancy, allowing instead atributtes
    #points and normal
    @staticmethod
    def detVec(prim, dirVec, exception):
        global epsilon
        reload(GeoMath)
        vec1 = GeoMath.vecNormalize(GeoMath.vecSub(list(prim.vertices()[0].point().position()), list(prim.vertices()[1].point().position())))
        vec2 = GeoMath.vecNormalize(GeoMath.vecSub(list(prim.vertices()[2].point().position()), list(prim.vertices()[1].point().position())))
        prim_normal = list(prim.normal())
        if(list(prim_normal) != [0, 1, 0]):
            #We consider that y is vertical and x horizontal
            if(math.fabs(vec1[1]) > math.fabs(vec2[1])):
                #If the vectors are dependent
                if(math.fabs(GeoMath.vecDotProduct(vec1, vec2)) > epsilon):
                    vecV = GeoMath.rotateVecByVec(vec2, prim_normal, 90)
                    #Quads!!
                    if(GeoMath.vecDotProduct(vecV, vec1) < -epsilon):
                        vecV = GeoMath.rotateVecByVec(vec2, prim_normal, -90)
                else:
                    vecV = vec1
                vecH = vec2
            else:
                #If the vectors are dependent
                if(math.fabs(GeoMath.vecDotProduct(vec1, vec2)) > epsilon):
                    vecV = GeoMath.rotateVecByVec(vec1, prim_normal, 90)
                    #Quads!!
                    if(GeoMath.vecDotProduct(vecV, vec2) < -epsilon):
                        vecV = GeoMath.rotateVecByVec(vec1, prim_normal, -90)
                else:
                    vecV = vec2
                vecH = vec1
        else:
            #We consider that x is vertical and z horizontal
            if(math.fabs(vec1[0]) > math.fabs(vec2[0])):
                #If the vectors are dependent
                if(math.fabs(GeoMath.vecDotProduct(vec1, vec2)) > epsilon):
                    vecV = GeoMath.rotateVecByVec(vec2, prim_normal, 90)
                    #Quads!!
                    if(GeoMath.vecDotProduct(vecV, vec1) < -epsilon):
                        vecV = GeoMath.rotateVecByVec(vec2, prim_normal, -90)
                else:
                    vecV = vec1
                vecH = vec2
            else:
                #If the vectors are dependent
                if(math.fabs(GeoMath.vecDotProduct(vec1, vec2)) > epsilon):
                    vecV = GeoMath.rotateVecByVec(vec1, prim_normal, 90)
                    #Quads!!!
                    if(GeoMath.vecDotProduct(vecV, vec2) < -epsilon):
                        vecV = GeoMath.rotateVecByVec(vec1, prim_normal, -90)
                else:
                    vecV = vec2
                vecH = vec1

        if(GeoMath.vecDotProduct(dirVec, vecH) < 0):
            vecH = GeoMath.vecSub([0, 0, 0], vecH)
        if(GeoMath.vecDotProduct(dirVec, vecV) < 0):
            vecV = GeoMath.vecSub([0, 0, 0], vecV)
        vecH = GeoMath.vecNormalize(vecH)
        vecV = GeoMath.vecNormalize(vecV)
        return vecH, vecV
