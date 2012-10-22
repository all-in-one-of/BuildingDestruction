# -*- coding: utf-8 -*-
from ExternalClasses import GeoMath
import BoundingBox
import logging
epsilon = 0.001
DEBUG = False


class Validator:
    '''
    Be careful with epsilon, change if it doesn't work fine
    '''
    @staticmethod
    def pointInsidePrim(point, prim):
        if(GeoMath.getEdgeWithPointInPrim(prim, point)):
            return True
        if(GeoMath.pointInPolygon(point, prim)):
            return True
        return False

    @staticmethod
    def patternInsideTexture(pat, prim, texture, textureForPrim):
        #BUT IS OK FOR MORE THAN THE FIRST POINT!!! WE HAVE TO DO THE CLIP, IF NOT WE DOESN?T ANYTHING!!!
        #IMPLEMENTS!!!!
        inside = True
        valid = False
        #We have to check if the pattern (is inside of the texture except the first and the last point,
        #because by definition this points are always inside) OR (intersect with his texture) OR
        #(intersect with a texture in upper level than his texture)
        #In the three cases the pattern will be valid, in other case the pattern will be invalid
        for index in range(len(pat.getPoints()) - 2):
            #check if the upper texture containign the point of pattern is his texture
            inside = (textureForPrim.findUpperTextureContainingPoint(pat.getPoints()[index + 1]) == texture)
            if (not inside):
                tex = textureForPrim.findUpperTextureContainingPoint(pat.getPoints()[index + 1])
                logging.debug("MUST TO BE")
                logging.debug(str(texture))
                logging.debug(str(texture.get_is_default_texture()))
                logging.debug(str(texture.get_absolute_points()))
                logging.debug(str(texture.get_absolute_points_not_erasable()))
                logging.debug(str(texture.get_delimited_proportions()))
                logging.debug(str(texture.get_obj()))
                logging.debug("IS")
                logging.debug(str(tex))
                logging.debug(str(tex.get_is_default_texture()))
                logging.debug(str(tex.get_absolute_points()))
                logging.debug(str(tex.get_absolute_points_not_erasable()))
                logging.debug(str(tex.get_delimited_proportions()))
                logging.debug(str(tex.get_obj()))
                firstIndexOutside = index
                break

        if(inside):
            valid = True
        else:
            #Check if the pattern intersect with his texture
            #To do that, we have to check if it intersects, and if it intersects, the point which intersect
            #the texture has to be before than the first point outside the texture
            minDistance, nearestPointIntersect, allIntersections = texture.checkIntersectionWithTexture(pat.getPoints(), prim) #@UnusedVariable
            outsidePointDistance = GeoMath.takeDistanceInTrackToPoint(pat.getPoints(), pat.getPoints()[firstIndexOutside], pat.getPoints()[0])
            valid = (minDistance <= outsidePointDistance)
            if(not valid):
                logging.debug("Texture not inside")
                #Check if intersect with upper texture
                upperLayer = textureForPrim.get_upper_texture(texture)
                if(upperLayer):
                    logging.debug("Texture has upper layer")
                    logging.debug(str(upperLayer))
                    logging.debug(str(upperLayer.get_is_default_texture()))
                    logging.debug(str(upperLayer.get_absolute_points()))
                    logging.debug(str(upperLayer.get_absolute_points_not_erasable()))
                    logging.debug(str(upperLayer.get_delimited_proportions()))
                    logging.debug(str(upperLayer.get_obj()))
                    #If exsits upper layer than the current texture
                    minDistance, nearestPointIntersect, allIntersections = upperLayer.checkIntersectionWithTexture(pat.getPoints(), prim) #@UnusedVariable
                    #Now check if the point intersection is before than the first point outside of his texture
                    if(nearestPointIntersect):
                        valid = (minDistance <= outsidePointDistance)
                        if(not valid):
                            logging.debug('Texture upper layer doesnt intersect before the first point outside')
                        else:
                            logging.debug('Texture upper layer intersect')
                    else:
                        logging.debug('Texture upper layer doesnt intersect')
                else:
                    #If not exists upper layer of texture, we check the intersection before,
                    #so if it doesn't intersect, the pattern will be invalid
                    logging.debug('Texture has not upper layer, so its incorrect')
                    valid = False
        return valid

    @staticmethod
    def patternInsidePrim(pat, prim):
        reload(GeoMath)
        reload(BoundingBox)
        logging.debug("Pat points" + str(pat.getPoints()))
        pat_bounding_box = BoundingBox.BoundingBox2D(pat.getPoints(), prim)
        prim_points = [list(p.point().position()) for p in prim.vertices()]
        prim_bounding_box = BoundingBox.BoundingBox2D(prim_points, prim)
        valid = prim_bounding_box.contain_bounding_box_3D(pat_bounding_box)

        return valid

    '''
    @param pat will be the pattern to validate
    @param listOfPatterns will be the list of patterns was created in current primitive
    @param groupOfPrims will be all the primitives that has posibility to be a neighbor primitive
    to the current primitive
    @param prim will be the current prim where the pattern are being validated
    '''
    @staticmethod
    def patternWithPatternsInPrim(pat, listOfPatterns, prim):
        reload(GeoMath)
        reload(BoundingBox)
        global DEBUG
        '''
        edgesPat = GeoMath.getEdgesFromPoints(pat.getPoints())
        '''
        pattern_bounding_box = BoundingBox.BoundingBox2D(pat.getPoints(), prim)
        for patInGr in listOfPatterns:
            param_pattern_bounding_box = BoundingBox.BoundingBox2D(patInGr.getPoints(), prim)
            intersections = pattern_bounding_box.intersect_bounding_box_without_limits_3D(param_pattern_bounding_box)
            if (intersections):
                if(DEBUG):
                    pattern_bounding_box.display_bounding_box_object_space()
                    param_pattern_bounding_box.display_bounding_box_object_space()
                    pattern_bounding_box.display_intersections()
                return False
            '''
            matchPoints = GeoMath.getIntersectionBetweenEdgesWithoutLimits2D(GeoMath.getEdgesFromPoints(patInGr.getPoints()), edgesPat, 1)
            matchEdges = GeoMath.getEdgesBetweenEdges(pat.getPoints(), patInGr.getPoints(), 1)
            if(len(matchPoints) != 0 or len(matchEdges) != 0):
                return False
            '''
        return True

    '''
    @param pat will be the pattern to validate
    @param listOfPatterns will be the list of patterns was created in current primitive
    @param groupOfPrims will be all the primitives that has posibility to be a neighbor primitive
    to the current primitive
    @param prim will be the current prim where the pattern are being validated
    '''
    @staticmethod
    def patternPrimWithNeigborsPatternsPrims(pat, prim, groupOfPrims):
        reload(GeoMath)
        reload(BoundingBox)
        prims = groupOfPrims.keys()
        primsConected = GeoMath.getConnectedPrims(prim, prims)
        pattern_bounding_box = BoundingBox.BoundingBox2D(pat.getPoints(), prim)
        for primConected in primsConected:
            if(primConected != prim):
                gr = groupOfPrims[primConected]
                for patInGr in gr:
                    param_pattern_bounding_box = BoundingBox.BoundingBox2D(patInGr.getPoints(), prim)
                    intersections, shared_prims_edges = pattern_bounding_box.intersect_bounding_box_with_limits_3D(param_pattern_bounding_box) #@UnusedVariable
                    if (intersections):
                        #Check if it is true that intersect
                        edges = GeoMath.getEdgesBetweenPoints(patInGr.getPoints(), pat.getPoints(), 1)

                        if(edges):
                            return False
        return True
